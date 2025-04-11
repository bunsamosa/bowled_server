from typing import Any

from fastapi import APIRouter, Request, HTTPException, status
import structlog

# Core models and manager
from gamelib.turn_based_models import GameState, GameStatus
from lib.game_state_manager import (
    load_game_state, save_game_state, publish_state_update
)

# Input/Output models for this endpoint
from .api_models import SelectOpenersInput


# Initialize logger
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()

@router.post(
    "/matches/{match_id}/select-openers",
    response_model=GameState,
    summary="Select the opening batsmen for the first innings",
    tags=["TurnBasedMatch"]
)
async def select_opening_batsmen(
    match_id: str,
    openers_input: SelectOpenersInput,
    request: Request,
) -> GameState:
    """Sets the on-strike and off-strike batsmen for the start of the match."""
    context: Any = request.state.context
    await logger.info(
        "Selecting opening batsmen",
        match_id=match_id,
        strike=openers_input.batsman_on_strike_id,
        non_strike=openers_input.batsman_off_strike_id,
    )

    # --- 1. Load Game State ---
    game_state = await load_game_state(context, match_id)
    if not game_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found.",
        )
    # Log loaded state details
    await logger.debug("Loaded state for opener selection", status=game_state.status, available_batsmen=game_state.available_batsman_ids)

    # --- 2. Validate Status ---
    if game_state.status != GameStatus.REQUIRES_OPENERS:
        await logger.warn(
            "Invalid state for selecting openers",
            match_id=match_id,
            current_status=game_state.status,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot select openers in current state: {game_state.status}",
        )

    # --- 3. Validate Input ---
    strike_id = openers_input.batsman_on_strike_id
    non_strike_id = openers_input.batsman_off_strike_id
    await logger.debug("Validating opener IDs", strike=strike_id, non_strike=non_strike_id)

    if strike_id == non_strike_id:
        await logger.warn("Strike and non-strike IDs are the same")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="On-strike/off-strike batsmen cannot be the same player.",
        )

    if strike_id not in game_state.available_batsman_ids:
        await logger.warn("Strike ID not in available list", strike_id=strike_id, available=game_state.available_batsman_ids)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Selected on-strike batsman {strike_id} is not available.",
        )
    if non_strike_id not in game_state.available_batsman_ids:
        await logger.warn("Non-strike ID not in available list", non_strike_id=non_strike_id, available=game_state.available_batsman_ids)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Selected off-strike batsman {non_strike_id} not available.",
        )
    await logger.debug("Opener IDs validated successfully")

    # --- 4. Update Game State ---
    game_state.batsman_on_strike_id = strike_id
    game_state.batsman_off_strike_id = non_strike_id
    game_state.status = GameStatus.REQUIRES_BOWLER
    # Remove selected openers from available list
    game_state.available_batsman_ids.remove(strike_id)
    game_state.available_batsman_ids.remove(non_strike_id)

    await logger.debug(
        "Game state updated for opener selection", match_id=match_id
    )

    # --- 5. Save Updated State ---
    success = await save_game_state(context, match_id, game_state)
    if not success:
        await logger.error(
            "Failed to save state after opener selection", match_id=match_id
        )
        # Don't publish update if save failed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save match state after selecting openers.",
        )

    # --- 6. Publish Update ---
    await publish_state_update(context, match_id)
    await logger.info("Openers selected successfully", match_id=match_id)

    return game_state
