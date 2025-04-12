from typing import Any
import asyncio

from fastapi import APIRouter, Request, HTTPException, status
import structlog

# Core models and manager
from gamelib.turn_based_models import (
    GameState, GameStatus, PlayerScorecard, BallData, OverSummary
)
from lib.game_state_manager import (
    load_game_state, save_game_state, publish_state_update
)

# Input/Output models for this endpoint
from .api_models import BowlResultOutput

# Match engine import
from bowled_match_engine.match_engine.ball_simulator import simulate_ball


# Initialize logger
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()


MAX_OVERS = 20  # Define max overs - should likely come from match settings
MAX_WICKETS = 10  # Define max wickets - should likely come from match settings


async def _update_game_state_after_ball(
    game_state: GameState, outcome_str: str
) -> GameState:
    """Updates the GameState based on the outcome of a simulated ball string.

    Handles score, wickets, player stats, ball logging, and status transitions
    related to the ball outcome string (excluding end-of-over logic).

    NOTE: This function is now async to allow awaiting logger calls.
    """
    # Use INFO level for debugging visibility
    await logger.info("Entering _update_game_state_after_ball", match_id=game_state.match_id, outcome=outcome_str)
    batsman_id = game_state.batsman_on_strike_id
    bowler_id = game_state.current_bowler_id

    if not batsman_id or not bowler_id:
        await logger.error(
            "Missing player IDs for state update", match_id=game_state.match_id
        )
        game_state.status = GameStatus.ERROR
        game_state.error_message = "Internal state error: Missing player IDs."
        await logger.info("Exiting _update_game_state_after_ball (ERROR)", match_id=game_state.match_id)
        return game_state

    # Get current player scorecards (or initialize if somehow missing)
    if batsman_id not in game_state.player_scorecards:
        game_state.player_scorecards[batsman_id] = PlayerScorecard(
            player_id=batsman_id
        )
    if bowler_id not in game_state.player_scorecards:
        game_state.player_scorecards[bowler_id] = PlayerScorecard(
            player_id=bowler_id
        )
    batsman_scorecard = game_state.player_scorecards[batsman_id]
    bowler_scorecard = game_state.player_scorecards[bowler_id]

    await logger.info("Got player scorecards", match_id=game_state.match_id)

    # Create/Get current OverSummary
    is_first_ball_of_over = game_state.current_ball_in_over == 0
    if is_first_ball_of_over:
        current_over_summary = OverSummary(
            innings=game_state.current_innings,
            over_number=game_state.current_over,
            bowler_id=bowler_id,
        )
        game_state.over_summaries.append(current_over_summary)
    else:
        current_over_summary = game_state.over_summaries[-1]
    await logger.info("Got OverSummary", match_id=game_state.match_id)

    runs_this_ball = 0
    extras_this_ball = 0
    extras_type = None
    # Correct check for wicket using descriptive strings
    wicket_this_ball = (outcome_str == "W" or outcome_str == "wicket")
    wicket_detail = "bowled" if wicket_this_ball else None  # TODO: Add more detail?

    # Check for legal delivery
    is_legal_delivery = outcome_str not in ["wide", "noball"]
    if is_legal_delivery:
        game_state.current_ball_in_over += 1
        game_state.total_balls_bowled += 1
        batsman_scorecard.batting.balls_faced += 1
        bowler_scorecard.bowling.balls_bowled += 1
        await logger.info("Processed legal delivery increments", match_id=game_state.match_id)

    # Update Score and player stats based on descriptive outcome_str
    await logger.info("Starting score/stat update", match_id=game_state.match_id)
    if outcome_str == "dot":
        pass # No runs
    elif outcome_str == "single":
        game_state.score += 1
        runs_this_ball = 1
        batsman_scorecard.batting.runs_scored += 1
        bowler_scorecard.bowling.runs_conceded += 1
    elif outcome_str == "double":
        game_state.score += 2
        runs_this_ball = 2
        batsman_scorecard.batting.runs_scored += 2
        bowler_scorecard.bowling.runs_conceded += 2
    elif outcome_str == "triple":
        game_state.score += 3
        runs_this_ball = 3
        batsman_scorecard.batting.runs_scored += 3
        bowler_scorecard.bowling.runs_conceded += 3
    elif outcome_str == "four":
        game_state.score += 4
        runs_this_ball = 4
        batsman_scorecard.batting.runs_scored += 4
        batsman_scorecard.batting.fours += 1
        bowler_scorecard.bowling.runs_conceded += 4
    elif outcome_str == "six":
        game_state.score += 6
        runs_this_ball = 6
        batsman_scorecard.batting.runs_scored += 6
        batsman_scorecard.batting.sixes += 1
        bowler_scorecard.bowling.runs_conceded += 6
    elif outcome_str == "wide":
        game_state.score += 1
        extras_this_ball = 1
        extras_type = "wide"
        bowler_scorecard.bowling.runs_conceded += 1
        bowler_scorecard.bowling.wides += 1
    elif outcome_str == "noball":
        game_state.score += 1
        extras_this_ball = 1
        extras_type = "noball"
        bowler_scorecard.bowling.runs_conceded += 1
        bowler_scorecard.bowling.noballs += 1
    elif wicket_this_ball:
        # Wicket handling (no runs conceded this ball)
        game_state.wickets += 1
        dismissed_batsman_id = game_state.batsman_on_strike_id
        if dismissed_batsman_id:
            game_state.dismissed_batsman_ids.append(dismissed_batsman_id)
        batsman_scorecard.batting.dismissed = True
        bowler_scorecard.bowling.wickets_taken += 1

        game_state.batsman_on_strike_id = None
        if game_state.wickets < MAX_WICKETS:
            game_state.status = GameStatus.REQUIRES_BATSMAN
            await logger.info(
                "Wicket fell, requires new batsman", match_id=game_state.match_id
            )
    else:
        # Log unknown descriptive string
        await logger.warning("Unhandled descriptive ball outcome string", outcome=outcome_str)

    # Update bowler overs_bowled
    b_balls = bowler_scorecard.bowling.balls_bowled
    bowler_scorecard.bowling.overs_bowled = round(b_balls // 6 + (b_balls % 6) / 10, 1)
    await logger.info("Updated bowler overs_bowled", match_id=game_state.match_id)

    # Create BallData
    await logger.info("Preparing BallData", match_id=game_state.match_id)
    ball_data = BallData(
        innings=game_state.current_innings,
        over=game_state.current_over,
        ball_in_over=game_state.current_ball_in_over if is_legal_delivery else 0,
        total_balls_bowled_innings=game_state.total_balls_bowled,
        batsman_on_strike_id=batsman_id,
        bowler_id=bowler_id,
        outcome=outcome_str, # Store the outcome string
        runs_scored=runs_this_ball,
        is_wicket=wicket_this_ball,
        wicket_type=wicket_detail,
        extras_type=extras_type,
        extras_runs=extras_this_ball,
        score_at_ball=game_state.score,
        wickets_at_ball=game_state.wickets,
    )
    current_over_summary.balls_in_over.append(ball_data)
    current_over_summary.runs_conceded += (runs_this_ball + extras_this_ball)
    if wicket_this_ball:
        current_over_summary.wickets_taken += 1
    await logger.info("Appended BallData to OverSummary", match_id=game_state.match_id)

    # Handle Batsman Swap
    await logger.info("Checking batsman swap", match_id=game_state.match_id)
    if (
        is_legal_delivery and
        not wicket_this_ball and
        runs_this_ball % 2 != 0
    ):
        (
            game_state.batsman_on_strike_id,
            game_state.batsman_off_strike_id,
        ) = (
            game_state.batsman_off_strike_id,
            game_state.batsman_on_strike_id,
        )
        await logger.info("Batsmen swapped ends", match_id=game_state.match_id)

    await logger.info("Exiting _update_game_state_after_ball (Success)", match_id=game_state.match_id)
    return game_state


@router.post(
    "/matches/{match_id}/bowl-next-ball",
    response_model=BowlResultOutput,
    summary="Simulate the next ball of the match",
    tags=["TurnBasedMatch"]
)
async def bowl_next_ball_endpoint(
    match_id: str, request: Request
) -> BowlResultOutput:
    """Simulates one ball, updates game state, and returns the outcome.

    Requires the game to be in the 'READY_FOR_BALL' state.
    Handles score updates, wickets, batsman swaps, end of over, end of innings.
    """
    context: Any = request.state.context
    await logger.info("Attempting to bowl next ball", match_id=match_id)

    # --- 1. Load Game State ---
    game_state = await load_game_state(context, match_id)
    if not game_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found.",
        )

    # --- 2. Validate Status ---
    if game_state.status != GameStatus.READY_FOR_BALL:
        await logger.warn(
            "Invalid state for bowling next ball",
            match_id=match_id,
            current_status=game_state.status,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot bowl next ball in current state: "
                   f"{game_state.status}. Action required.",
        )

    # --- 3. Get Batsman and Bowler Data ---
    try:
        batsman_id = game_state.batsman_on_strike_id
        bowler_id = game_state.current_bowler_id
        if not batsman_id or not bowler_id:
            raise HTTPException(
                status_code=500,
                detail="Internal state error: Missing player ID for simulation."
            )
        squad_players = game_state.team1_squad + game_state.team2_squad
        batsman_data = next((
            p for p in squad_players if str(p["player_id"]) == batsman_id
        ), None)
        bowler_data = next((
            p for p in squad_players if str(p["player_id"]) == bowler_id
        ), None)
        if not batsman_data or not bowler_data:
            raise HTTPException(
                status_code=500,
                detail="Internal state error: Player data missing."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error preparing simulation: {e}")

    # --- 4. Simulate the Ball --- #
    try:
        ball_outcome_str = await simulate_ball(batsman_data, bowler_data)
        ball_outcome_str = str(ball_outcome_str)  # Ensure standard string

        # Generate commentary based on the string outcome
        commentary_map = {  # Simple commentary mapping
            "0": "Dot ball, no run.", "1": "Single taken.", "2": "Good running, two runs.",
            "3": "Three runs.", "4": "FOUR! Great shot.", "6": "SIX! Clears the boundary.",
            "W": "OUT! That's a wicket!", "wicket": "OUT! That's a wicket!",
            "wide": "Wide ball.", "noball": "No ball."
        }
        commentary = commentary_map.get(ball_outcome_str, f"Outcome: {ball_outcome_str}")

        # Store string outcome and commentary in game state
        game_state.commentary = commentary
        game_state.last_ball_outcome = ball_outcome_str # Store the string
        await asyncio.sleep(0.2) # Keep the sleep just in case
    except Exception as e:
        await logger.error("Caught exception during ball simulation block", match_id=match_id, error=str(e), exc_info=True)
        await logger.exception(
            "Error during ball simulation", match_id=match_id, exc_info=e
        )

    # --- 5. Update Game State using Helper Function --- #
    try:
        # Call the helper function (now async, so await is needed)
        game_state = await _update_game_state_after_ball(game_state, ball_outcome_str)
        if game_state.status == GameStatus.ERROR:
            raise HTTPException(status_code=500, detail=game_state.error_message or "Error updating game state.")
    except Exception as e:
        await logger.exception("Error updating game state after ball", match_id=match_id, ball_outcome=ball_outcome_str, exc_info=e)
        game_state.status = GameStatus.ERROR
        game_state.error_message = f"Update failed after ball: {e}"
        raise HTTPException(status_code=500, detail="Failed to update game state after ball simulation.")

    # --- 6. Check and Handle End of Over / Innings --- #
    await logger.info("Starting end-of-over/innings checks", match_id=match_id)
    is_innings_finished = False
    # Check wickets first
    if game_state.status != GameStatus.ERROR and game_state.wickets >= MAX_WICKETS:
        is_innings_finished = True
        await logger.info("Innings finished: All wickets down", match_id=match_id)

    # Check if over is finished (legal balls >= 6)
    is_over_finished = (
        game_state.current_ball_in_over >= 6 and
        game_state.status != GameStatus.REQUIRES_BATSMAN and
        game_state.status != GameStatus.ERROR
    )

    if is_over_finished:
        current_over_summary = game_state.over_summaries[-1]
        if current_over_summary.runs_conceded == 0 and current_over_summary.wickets_taken == 0:
            # Only add maiden if no runs AND no wickets conceded in the over
            bowler_scorecard = game_state.player_scorecards.get(game_state.current_bowler_id)
            if bowler_scorecard:
                bowler_scorecard.bowling.maidens += 1
                await logger.info("Maiden over bowled", match_id=match_id, bowler=game_state.current_bowler_id)
        (game_state.batsman_on_strike_id, game_state.batsman_off_strike_id) = (
            game_state.batsman_off_strike_id, game_state.batsman_on_strike_id
        )
        await logger.info("Batsmen swapped for new over", match_id=match_id)
        game_state.current_over += 1
        game_state.current_ball_in_over = 0

        if game_state.current_over >= game_state.total_overs:
            is_innings_finished = True
            await logger.info(
                "Innings finished: Overs completed",
                match_id=match_id,
                over=game_state.current_over
            )
        # ONLY ask for bowler if innings is NOT finished
        elif not is_innings_finished:
            game_state.previous_over_bowler_id = game_state.current_bowler_id
            game_state.current_bowler_id = None
            game_state.status = GameStatus.REQUIRES_BOWLER
            await logger.info(
                "Over ended, status set to REQUIRES_BOWLER",
                match_id=game_state.match_id,
                status=game_state.status
            )
        else:  # Should not happen if logic is correct, but log if it does
            await logger.warn(
                "Unexpected state after over completion check",
                is_innings_finished=is_innings_finished,
                match_id=game_state.match_id
            )

    # --- Handle Innings Completion ---
    await logger.info(
        "Checking if innings is finished",
        match_id=match_id,
        is_innings_finished=is_innings_finished,
        current_status=game_state.status
    )
    if is_innings_finished:
        await logger.info("Inside is_innings_finished block", match_id=match_id, current_innings=game_state.current_innings)
        if game_state.current_innings == 1:
            await logger.info(
                "Innings 1 complete. Setting status to INNINGS_BREAK.",
                match_id=match_id
            )
            # Set status and target, reset handled by start_second_innings endpoint
            game_state.status = GameStatus.INNINGS_BREAK
            game_state.target = game_state.score + 1
            # Removed state reset logic from here
            await logger.info("Innings 1 finished, status set to INNINGS_BREAK", status=game_state.status, match_id=match_id)

        elif game_state.current_innings == 2:
            await logger.info(
                "Innings 2 complete. Setting status to COMPLETED.",
                match_id=game_state.match_id
            )
            game_state.status = GameStatus.COMPLETED

    # Check for win condition in 2nd innings
    await logger.info(
        "Checking win condition (2nd Innings)",
        match_id=match_id,
        current_status=game_state.status,
        is_innings_finished=is_innings_finished
    )
    if (
        not is_innings_finished and
        game_state.current_innings == 2 and
        game_state.target is not None and
        game_state.score >= game_state.target
    ):
        await logger.info(
            "Match completed: Target reached. Setting status to COMPLETED.",
            match_id=match_id
        )
        game_state.status = GameStatus.COMPLETED
        is_innings_finished = True  # Mark innings finished here too

    await logger.info("Finished end-of-over/innings checks", match_id=match_id, final_status_before_save=game_state.status)
    # --- 7. Save and Publish Updated State --- #
    await logger.info(
        "Final state before save",
        status=game_state.status,
        current_over=game_state.current_over,
        current_ball=game_state.current_ball_in_over,
        total_balls=game_state.total_balls_bowled,
        is_innings_finished=is_innings_finished,
        match_id=match_id
    )
    save_success = False
    loaded_state_after_save = None  # For debugging
    try:
        # === DETAILED LOGGING BEFORE SAVE ===
        await logger.info(
            "State PREPARED for save",
            status=game_state.status,
            current_over=game_state.current_over,
            current_ball=game_state.current_ball_in_over,
            total_balls=game_state.total_balls_bowled,
            score=game_state.score,
            wickets=game_state.wickets,
            target=game_state.target,
            match_id=match_id
        )
        # === END LOGGING ===
        save_success = await save_game_state(context, match_id, game_state)
        await logger.info("save_game_state function returned", success=save_success, match_id=match_id)

        # === DEBUG: Immediately load state after save ===
        if save_success:
            loaded_state_after_save = await load_game_state(context, match_id)
            if loaded_state_after_save:
                await logger.info("State loaded IMMEDIATELY after save", status=loaded_state_after_save.status, match_id=match_id)
            else:
                await logger.warn("Failed to load state immediately after successful save", match_id=match_id)
        # === END DEBUG ===

        if not save_success:
            await logger.error("save_game_state returned False, state may not be saved!", match_id=match_id)
    except Exception as e:
        await logger.exception("Failed to save state", match_id=match_id, exc_info=e)

    # Publish state update AFTER the save attempt (if successful)
    if save_success:
        try:
            # Add a small delay before publishing to allow cache write to settle
            await asyncio.sleep(0.2) # Delay for 200 milliseconds

            await publish_state_update(context, match_id)
            await logger.info("Game state update published successfully after save block", match_id=match_id)
        except Exception as e:
            await logger.exception("Failed to publish game state update separately", match_id=match_id, exc_info=e)
            # Log publish error, but likely continue to return response

    # --- 8. Prepare and Return Response --- #
    await logger.info("State being returned in response", status=game_state.status)
    response = BowlResultOutput(
        ball_outcome=game_state.last_ball_outcome, # Use the stored string outcome
        updated_game_state=game_state
    )
    return response
