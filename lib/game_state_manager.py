import json
from typing import Optional, Any

import structlog
from pydantic import ValidationError

# Assuming context object structure provides cache_store
# from lib.core.context import RequestContext # Example hypothetical import
from lib.core.cache_store import CacheStore
from gamelib.turn_based_models import GameState


# Initialize logger for this module
logger = structlog.get_logger(__name__)

# Constants
GAME_STATE_KEY_PREFIX = "match"
GAME_UPDATE_CHANNEL_PREFIX = "match-updates"
GAME_STATE_TTL_SECONDS = 86400  # 24 hours


def _get_state_key(match_id: str) -> str:
    """Generates the Redis key for storing game state."""
    return f"{GAME_STATE_KEY_PREFIX}:{match_id}"


def _get_update_channel(match_id: str) -> str:
    """Generates the Redis Pub/Sub channel name for game updates."""
    return f"{GAME_UPDATE_CHANNEL_PREFIX}:{match_id}"


async def save_game_state(context: Any, match_id: str, state: GameState) -> bool:
    """Saves the game state to the cache (Redis).

    Args:
        context: The request context containing cache_store.
        match_id: The unique identifier for the match.
        state: The GameState object to save.

    Returns:
        True if saving was successful, False otherwise.
    """
    try:
        cache_store: CacheStore = context.cache_store
        state_key = _get_state_key(match_id)
        # Serialize Pydantic model to JSON string using Pydantic v2 method
        state_json = state.model_dump_json()

        # Use set_key which handles namespacing and expiry
        # CacheStore.set_key expects a string value.
        # Note: CacheStore.set_key expects string value,
        # Pydantic's .json() provides this.
        # It also has a default expiry of 300s, overridden here.
        # Max allowed is 86400.
        success = cache_store.set_key(
            key=state_key, value=state_json, expire=GAME_STATE_TTL_SECONDS
        )
        if not success:
            await logger.error(
                "Failed to save game state to cache.", match_id=match_id
            )
            return False
        return True
    except Exception as e:
        await logger.exception(
            "Error saving game state.", match_id=match_id, exc_info=e
        )
        return False


async def load_game_state(context: Any, match_id: str) -> Optional[GameState]:
    """Loads the game state from the cache (Redis).

    Args:
        context: The request context containing cache_store.
        match_id: The unique identifier for the match.

    Returns:
        The loaded GameState object, or None if not found or error occurs.
    """
    try:
        cache_store: CacheStore = context.cache_store
        state_key = _get_state_key(match_id)

        state_json = cache_store.get_key(key=state_key)

        if state_json is None:
            await logger.warn(
                "Game state not found in cache.", match_id=match_id
            )
            return None

        # Decode from bytes if necessary (redis-py might return bytes)
        if isinstance(state_json, bytes):
            state_json = state_json.decode('utf-8')

        # Parse JSON string back into Pydantic model
        state = GameState.model_validate_json(state_json)
        return state
    except (ValidationError, json.JSONDecodeError) as e:
        await logger.exception(
            "Failed to parse game state from cache.",
            match_id=match_id,
            exc_info=e,
        )
        return None
    except Exception as e:
        await logger.exception(
            "Error loading game state.", match_id=match_id, exc_info=e
        )
        return None


async def publish_state_update(context: Any, match_id: str) -> None:
    """Publishes a notification that the game state has been updated.

    Args:
        context: The request context containing cache_store.
        match_id: The unique identifier for the match whose state was updated.
    """
    try:
        cache_store: CacheStore = context.cache_store
        redis_client = cache_store.client  # Get the underlying client
        channel = _get_update_channel(match_id)
        message = "updated"

        # Publish the message synchronously
        redis_client.publish(channel, message)

    except Exception as e:
        await logger.exception(
            "Failed to publish game state update.",
            match_id=match_id,
            exc_info=e,
        )
