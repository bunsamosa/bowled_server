import uuid
import random
from typing import Any, Dict

from fastapi import APIRouter, Request, HTTPException, status
import structlog

# Core models and manager
from gamelib.turn_based_models import GameState, GameStatus, PlayerScorecard
from lib.game_state_manager import save_game_state  # Only save needed here

# Input/Output models for this endpoint
from .api_models import StartMatchInput

# Helper functions
# Assume get_players_by_team_id is correctly imported
from gamelib.team.live_team import get_players_by_team_id
# Assume a similar helper exists for team details
from gamelib.team.live_team import get_team_by_id

# Initialize logger
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/matches",
    response_model=GameState,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new turn-based match",
    tags=["TurnBasedMatch"]
)
async def start_new_match(
    request: Request,
    match_input: StartMatchInput,
) -> GameState:
    """Initiates a new turn-based match between two teams.

    Performs validation, toss, initializes the game state in the cache,
    and returns the initial state requiring opener selection.
    """
    context: Any = request.state.context
    await logger.info(
        "Starting new turn-based match",
        team1=match_input.team1_id,
        team2=match_input.team2_id,
    )

    # --- 1. Fetch Player Data & Validate Squads ---
    await logger.debug("Received input squads", team1_ids=match_input.team1_squad_player_ids, team2_ids=match_input.team2_squad_player_ids)
    # Acquire DB connection and attach to context for this block
    async with context.data_store.acquire() as conn:
        context.ds_connection = conn  # Attach the connection
        try:
            team1_all_players = await get_players_by_team_id(
                team_id=match_input.team1_id, context=context
            )
            team2_all_players = await get_players_by_team_id(
                team_id=match_input.team2_id, context=context
            )
            await logger.debug("Fetched players from DB", team1_count=len(team1_all_players), team2_count=len(team2_all_players))

            # Create sets of valid player IDs for quick lookup
            # Convert DB IDs to strings for comparison with input (which are strings)
            team1_valid_player_ids = {str(p["player_id"]) for p in team1_all_players}
            team2_valid_player_ids = {str(p["player_id"]) for p in team2_all_players}
            await logger.debug("DB player ID sets created", team1_db_ids=team1_valid_player_ids, team2_db_ids=team2_valid_player_ids)

            input_team1_squad_ids = set(match_input.team1_squad_player_ids)
            input_team2_squad_ids = set(match_input.team2_squad_player_ids)
            await logger.debug("Input player ID sets created", team1_input_ids=input_team1_squad_ids, team2_input_ids=input_team2_squad_ids)

            # Validate squad size
            if len(input_team1_squad_ids) != 11:
                await logger.warn("Invalid squad size for team 1", size=len(input_team1_squad_ids))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Team {match_input.team1_id} must have exactly "
                        f"11 unique players, got {len(input_team1_squad_ids)}."
                    )
                )
            if len(input_team2_squad_ids) != 11:
                await logger.warn("Invalid squad size for team 2", size=len(input_team2_squad_ids))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Team {match_input.team2_id} must have exactly "
                        f"11 unique players, got {len(input_team2_squad_ids)}."
                    )
                 )

            # Validate player IDs belong to the correct team
            await logger.debug("Performing subset validation for team 1")
            if not input_team1_squad_ids.issubset(team1_valid_player_ids):
                invalid_ids = input_team1_squad_ids - team1_valid_player_ids
                await logger.warn("Invalid player IDs found for team 1", invalid_ids=invalid_ids)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Invalid player IDs for team {match_input.team1_id}: "
                        f"{invalid_ids}"
                    )
                )
            await logger.debug("Performing subset validation for team 2")
            if not input_team2_squad_ids.issubset(team2_valid_player_ids):
                invalid_ids = input_team2_squad_ids - team2_valid_player_ids
                await logger.warn("Invalid player IDs found for team 2", invalid_ids=invalid_ids)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                         f"Invalid player IDs for team {match_input.team2_id}: "
                         f"{invalid_ids}"
                    )
                )

            # Filter the full player data to get the selected squads
            # Ensure keys are strings to match lookup IDs (which are strings from input)
            team1_player_map = {str(p["player_id"]): p for p in team1_all_players}
            team2_player_map = {str(p["player_id"]): p for p in team2_all_players}
            team1_squad_data = [
                team1_player_map[pid] for pid in match_input.team1_squad_player_ids
            ]
            team2_squad_data = [
                team2_player_map[pid] for pid in match_input.team2_squad_player_ids
            ]

            await logger.debug("Fetched and validated player data for squads")

        except HTTPException as http_exc:  # Re-raise validation errors
            raise http_exc
        except Exception as e:
            await logger.exception(
                "Error fetching/validating player data", exc_info=e
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve or validate player data."
            )
        finally:
            # Ensure connection attribute is removed from context after use
            context.ds_connection = None

    # --- 2. Fetch Team Names (New Step) ---
    team1_name = "Team 1" # Default
    team2_name = "Team 2" # Default
    try:
        team1_details = await get_team_by_id(match_input.team1_id, context)
        if team1_details and team1_details.get("team_name"):
            team1_name = team1_details["team_name"]

        team2_details = await get_team_by_id(match_input.team2_id, context)
        if team2_details and team2_details.get("team_name"):
            team2_name = team2_details["team_name"]
        await logger.info("Fetched team names", team1=team1_name, team2=team2_name)
    except Exception as e:
        await logger.warn("Could not fetch team names, using defaults.", exc_info=e)

    # --- 3. Perform Toss ---
    toss_winner_team_id = random.choice([
        match_input.team1_id,
        match_input.team2_id,
    ])
    # Simple rule: winner bats first (can be made random choice later)
    if toss_winner_team_id == match_input.team1_id:
        batting_team_id = match_input.team1_id
        bowling_team_id = match_input.team2_id
    else:
        batting_team_id = match_input.team2_id
        bowling_team_id = match_input.team1_id
    await logger.info(
        f"Toss won by {toss_winner_team_id}, decided to bat first.",
        batting_team=batting_team_id,
        bowling_team=bowling_team_id,
    )

    # --- 4. Initialize Game State ---
    match_id = str(uuid.uuid4())
    team1_ids = match_input.team1_squad_player_ids
    team2_ids = match_input.team2_squad_player_ids

    # Initialize player scorecards for all players in both squads
    initial_player_scorecards: Dict[str, PlayerScorecard] = {
        p_id: PlayerScorecard(player_id=p_id)
        for p_id in team1_ids + team2_ids
    }

    initial_state = GameState(
        match_id=match_id,
        status=GameStatus.REQUIRES_OPENERS,
        team1_id=match_input.team1_id,
        team2_id=match_input.team2_id,
        team1_name=team1_name, # Assign fetched/default name
        team2_name=team2_name, # Assign fetched/default name
        team1_squad=team1_squad_data,  # Store fetched player data
        team2_squad=team2_squad_data,
        total_overs=match_input.overs, # Store the number of overs
        current_innings=1,
        batting_team_id=batting_team_id,
        bowling_team_id=bowling_team_id,
        # Populate available players based on initial batting/bowling teams
        available_batsman_ids=list(team1_ids)
        if batting_team_id == match_input.team1_id
        else list(team2_ids),
        available_bowler_ids=list(team1_ids)
        if bowling_team_id == match_input.team1_id
        else list(team2_ids),
        player_scorecards=initial_player_scorecards, # Initialize scorecards
        # Other fields default to 0 or None
    )
    await logger.debug("Initial game state prepared", match_id=match_id)

    # --- 5. Save Initial State ---
    success = await save_game_state(context, match_id, initial_state)
    if not success:
        await logger.error(
            "Failed to save initial game state", match_id=match_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize match state.",
        )

    await logger.info(
        "Successfully started new match",
        match_id=match_id,
        status=initial_state.status,
    )
    return initial_state
