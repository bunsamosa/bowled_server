from typing import Any

from fastapi import APIRouter, Request, HTTPException, status
import structlog

# Core models and manager
from gamelib.turn_based_models import GameState, GameStatus
from lib.game_state_manager import (
    load_game_state, save_game_state, publish_state_update
)

# Input/Output models for this endpoint
from .api_models import SelectBatsmanInput


# Initialize logger
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/matches/{match_id}/select-next-batsman",
    response_model=GameState,
    summary="Select the next batsman after a wicket",
    tags=["TurnBasedMatch"]
)
async def select_next_batsman(
    match_id: str,
    batsman_input: SelectBatsmanInput,
    request: Request,
) -> GameState:
    """Sets the next batsman to come in after a wicket has fallen."""
    context: Any = request.state.context
    await logger.info(
        "Selecting next batsman",
        match_id=match_id,
        next_batsman_id=batsman_input.next_batsman_id,
    )

    # --- 1. Load Game State ---
    game_state = await load_game_state(context, match_id)
    if not game_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found.",
        )

    # --- 2. Validate Status ---
    if game_state.status != GameStatus.REQUIRES_BATSMAN:
        await logger.warn(
            "Invalid state for selecting next batsman",
            match_id=match_id,
            current_status=game_state.status,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot select next batsman in current state: {game_state.status}",
        )

    # --- 3. Validate Input ---
    next_batsman_id = batsman_input.next_batsman_id
    if next_batsman_id not in game_state.available_batsman_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Selected batsman {next_batsman_id} is not available.",
        )

    # Ensure the new batsman is not the one currently at the crease (off-strike)
    if next_batsman_id == game_state.batsman_off_strike_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Selected batsman {next_batsman_id} is already at the crease.",
        )

    # --- 4. Update Game State ---
    # The dismissed batsman was already removed from strike in bowl_next_ball
    # We just need to place the new batsman at the vacant striker's end
    game_state.batsman_on_strike_id = next_batsman_id
    game_state.status = GameStatus.READY_FOR_BALL  # Ready for next ball
    # Remove selected batsman from available list
    game_state.available_batsman_ids.remove(next_batsman_id)

    await logger.debug(
        "Game state updated for next batsman selection", match_id=match_id
    )

    # --- 5. Save Updated State ---
    success = await save_game_state(context, match_id, game_state)
    if not success:
        await logger.error(
            "Failed to save game state after next batsman selection",
            match_id=match_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save match state after selecting next batsman.",
        )

    # --- 6. Publish Update ---
    await publish_state_update(context, match_id)
    await logger.info("Next batsman selected successfully", match_id=match_id)

    return game_state
