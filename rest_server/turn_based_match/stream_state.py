from typing import Any
import asyncio

from fastapi import APIRouter, Request
import structlog

# SSE
from sse_starlette import EventSourceResponse

# Core models and manager
from lib.game_state_manager import load_game_state


# Initialize logger
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()


@router.get(
    "/matches/{match_id}/stream",
    summary="Stream game state updates using Server-Sent Events (SSE)",
    tags=["TurnBasedMatch"]
)
async def stream_match_updates(match_id: str, request: Request):
    """Establishes an SSE connection to push game state updates.

    Subscribes to Redis Pub/Sub channel for the match.
    When an update message is received, it loads the latest state
    and sends it to the client.
    """
    context: Any = request.state.context
    redis_client = context.cache_store.client  # Assumes sync redis client
    channel_name = f"match-updates:{match_id}"  # Use helper if available

    async def event_publisher():
        # Check if connection is still alive before proceeding
        is_connected = True
        pubsub = None
        try:
            # Initial check
            if await request.is_disconnected():
                await logger.info(
                    "SSE client disconnected before starting.", match_id=match_id
                )
                is_connected = False
                return

            # Subscribe to the Redis channel
            pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
            pubsub.subscribe(channel_name)
            await logger.info(
                "SSE client subscribed to updates",
                match_id=match_id,
                channel=channel_name
            )

            while is_connected:
                # Check connection again before blocking/long operations
                if await request.is_disconnected():
                    await logger.info(
                        "SSE client disconnected.", match_id=match_id
                    )
                    is_connected = False
                    break  # Exit loop cleanly

                # Check for messages (using get_message with timeout)
                # This prevents blocking indefinitely if redis-py is sync
                message = pubsub.get_message(timeout=0.5)  # Timeout in seconds

                if message and message["type"] == "message":
                    await logger.debug(
                        "Received state update message", match_id=match_id
                    )
                    # Message received, load latest state and send
                    latest_state = await load_game_state(context, match_id)
                    if latest_state:
                        # Send the full game state as JSON
                        yield latest_state.json()
                    else:
                        # Log error if state couldn't be loaded
                        await logger.error(
                            "Received update signal but failed to load state",
                            match_id=match_id
                        )
                else:
                    # No message, check connection and sleep
                    if await request.is_disconnected():
                        await logger.info(
                            "SSE client disconnected during idle check.",
                            match_id=match_id
                        )
                        is_connected = False
                        break
                    # Optional: yield a keep-alive comment if needed
                    # yield ": keep-alive\n\n"
                    await asyncio.sleep(0.1)  # Short sleep if no message

        except asyncio.CancelledError:
            await logger.info(
                "SSE connection cancelled/closed by client.", match_id=match_id
            )
        except Exception as e:
            await logger.exception(
                "Error in SSE publisher", match_id=match_id, exc_info=e
            )
            # Optionally yield an error message to the client
            # yield json.dumps({"error": "Internal server error"})
        finally:
            # Ensure unsubscription on disconnect or error
            if pubsub:
                try:
                    pubsub.unsubscribe(channel_name)
                    pubsub.close()
                    await logger.info(
                        "SSE client unsubscribed.",
                        match_id=match_id,
                        channel=channel_name
                    )
                except Exception as unsub_e:
                    await logger.exception(
                        "Error during SSE unsubscribe",
                        match_id=match_id,
                        exc_info=unsub_e
                    )

    return EventSourceResponse(event_publisher())
