from typing import Any

from fastapi import APIRouter, Request, HTTPException, status
import structlog

# Core models and manager
from gamelib.turn_based_models import GameState
from lib.game_state_manager import load_game_state


# Initialize logger
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()


@router.get(
    "/matches/{match_id}",
    response_model=GameState,
    summary="Get the current state of a match",
    tags=["TurnBasedMatch"]
)
async def get_match_state(
    match_id: str, request: Request
) -> GameState:
    """Retrieves the latest saved game state from the cache."""
    context: Any = request.state.context
    await logger.info("Fetching game state", match_id=match_id)

    game_state = await load_game_state(context, match_id)
    if not game_state:
        await logger.warn(
            "Attempted to fetch non-existent match state", match_id=match_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found.",
        )

    # Log the status of the loaded state
    await logger.debug("Game state loaded from cache", match_id=match_id, status=game_state.status)

    return game_state
