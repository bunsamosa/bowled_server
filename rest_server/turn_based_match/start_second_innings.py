from typing import Any

from fastapi import APIRouter, Request, HTTPException, status
import structlog

# Core models and manager
from gamelib.turn_based_models import GameState, GameStatus
from lib.game_state_manager import (
    load_game_state, save_game_state, publish_state_update
)


# Initialize logger
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/matches/{match_id}/start-second-innings",
    response_model=GameState,
    summary="Prepare the game state for the second innings",
    tags=["TurnBasedMatch"]
)
async def start_second_innings(
    match_id: str, request: Request
) -> GameState:
    """Transitions the game state from INNINGS_BREAK to start the 2nd innings."""
    context: Any = request.state.context
    await logger.info("Attempting to start second innings", match_id=match_id)

    # --- 1. Load Game State ---
    game_state = await load_game_state(context, match_id)
    if not game_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found.",
        )

    # --- 2. Validate Status ---
    if game_state.status != GameStatus.INNINGS_BREAK:
        await logger.warn(
            "Invalid state for starting second innings",
            match_id=match_id,
            current_status=game_state.status,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot start second innings in current state: {game_state.status}",
        )

    # --- 3. Update Game State for Second Innings ---
    try:
        # Set target
        game_state.target = game_state.score + 1

        # Swap teams
        first_innings_batting_team = game_state.batting_team_id
        first_innings_bowling_team = game_state.bowling_team_id
        game_state.batting_team_id = first_innings_bowling_team
        game_state.bowling_team_id = first_innings_batting_team

        # Reset innings counters
        game_state.score = 0
        game_state.wickets = 0
        game_state.current_over = 0
        game_state.current_ball_in_over = 0
        game_state.total_balls_bowled = 0

        # Reset player status lists
        game_state.dismissed_batsman_ids = []
        game_state.bowlers_used_this_innings = []

        # Reset available players based on new batting/bowling team
        if game_state.batting_team_id == game_state.team1_id:
            game_state.available_batsman_ids = [
                str(p["player_id"]) for p in game_state.team1_squad
            ]
            game_state.available_bowler_ids = [
                str(p["player_id"]) for p in game_state.team2_squad
            ]
        else:
            game_state.available_batsman_ids = [
                str(p["player_id"]) for p in game_state.team2_squad
            ]
            game_state.available_bowler_ids = [
                str(p["player_id"]) for p in game_state.team1_squad
            ]

        # Clear current players
        game_state.batsman_on_strike_id = None
        game_state.batsman_off_strike_id = None
        game_state.current_bowler_id = None

        # Update innings number and status
        game_state.current_innings = 2
        game_state.status = GameStatus.REQUIRES_OPENERS

        await logger.info(
            "Game state updated for second innings",
            match_id=match_id,
            target=game_state.target
        )

    except Exception as e:
        await logger.exception(
            "Error updating game state for second innings",
            match_id=match_id, exc_info=e
        )
        # Optionally set error status
        # game_state.status = GameStatus.ERROR
        # game_state.error_message = "Failed to prepare second innings state."
        # await save_game_state(context, match_id, game_state)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update game state for second innings."
        )

    # --- 4. Save Updated State ---
    success = await save_game_state(context, match_id, game_state)
    if not success:
        await logger.error(
            "Failed to save game state after preparing second innings",
            match_id=match_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save updated match state.",
        )

    # === DEBUG: Immediately load state after save ===
    if success:
        reloaded_state = await load_game_state(context, match_id)
        if reloaded_state:
            await logger.debug(
                "State reloaded IMMEDIATELY after save in start_second_innings",
                status=reloaded_state.status,
                available_batsmen=reloaded_state.available_batsman_ids,
                match_id=match_id
            )
        else:
            await logger.warn(
                "Failed to reload state immediately after successful save "
                "in start_second_innings",
                match_id=match_id
            )
    # === END DEBUG ===

    # --- 5. Publish Update ---
    await publish_state_update(context, match_id)
    await logger.info("Second innings started successfully", match_id=match_id)

    return game_state
