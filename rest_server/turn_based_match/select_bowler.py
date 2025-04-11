from typing import Any

from fastapi import APIRouter, Request, HTTPException, status
import structlog

# Core models and manager
from gamelib.turn_based_models import GameState, GameStatus
from lib.game_state_manager import (
    load_game_state, save_game_state, publish_state_update
)

# Input/Output models for this endpoint
from .api_models import SelectBowlerInput


# Initialize logger
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/matches/{match_id}/select-bowler",
    response_model=GameState,
    summary="Select the bowler for the upcoming over",
    tags=["TurnBasedMatch"]
)
async def select_bowler_for_over(
    match_id: str,
    bowler_input: SelectBowlerInput,
    request: Request,
) -> GameState:
    """Sets the bowler for the next over (or the current over if first)."""
    context: Any = request.state.context
    await logger.info(
        "Selecting bowler for over",
        match_id=match_id,
        bowler_id=bowler_input.bowler_id,
    )

    # --- 1. Load Game State ---
    game_state = await load_game_state(context, match_id)
    if not game_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found.",
        )

    # --- 2. Validate Status ---
    if game_state.status != GameStatus.REQUIRES_BOWLER:
        await logger.warn(
            "Invalid state for selecting bowler",
            match_id=match_id,
            current_status=game_state.status,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot select bowler in current state: {game_state.status}",
        )

    # --- 3. Validate Input ---
    bowler_id = bowler_input.bowler_id
    if bowler_id not in game_state.available_bowler_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Selected bowler {bowler_id} is not available.",
        )
    # Rule validation: Check if bowler bowled the previous over
    if (
        game_state.previous_over_bowler_id
        and bowler_id == game_state.previous_over_bowler_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bowler {bowler_id} cannot bowl consecutive overs.",
        )

    # --- 4. Update Game State ---
    game_state.current_bowler_id = bowler_id
    game_state.status = GameStatus.READY_FOR_BALL
    # Optionally track bowlers used this innings
    game_state.bowlers_used_this_innings.append(bowler_id)

    await logger.debug(
        "Game state updated for bowler selection", match_id=match_id
    )

    # --- 5. Save Updated State ---
    success = await save_game_state(context, match_id, game_state)
    if not success:
        await logger.error(
            "Failed to save game state after bowler selection",
            match_id=match_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save match state after selecting bowler.",
        )

    # --- 6. Publish Update ---
    await publish_state_update(context, match_id)
    await logger.info("Bowler selected successfully", match_id=match_id)

    return game_state
