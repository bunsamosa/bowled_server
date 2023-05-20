import random
import uuid
from typing import Dict
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from bowled_match_engine.match_engine.game_simulator import simulate_game
from gamelib.team.live_team import get_players_by_team_id
from gamelib.team.live_team import get_team_by_id
from rest_server.live.api_models import LiveGameInput

# Create FastAPI router
router = APIRouter(prefix="/live")


@router.post(
    path="/game",
    response_model=Dict,
    tags=["Live"],
)
async def play_game(
    request: Request,
    game_input: LiveGameInput,
) -> Union[Dict, HTTPException]:
    """
    Simulate game API
    """
    context = request.state.context
    await context.logger.info("Simulate game API")

    # TODO: Validate input data
    # choose a random enemy team
    icc_teams = ["ind", "aus", "eng", "pak", "nz", "wi", "sl", "sa"]
    ipl_teams = [
        "csk",
        "dc",
        "gt",
        "kkr",
        "lsg",
        "mi",
        "pbks",
        "rr",
        "rcb",
        "srh",
    ]

    if game_input.team_id in icc_teams:
        icc_teams.remove(game_input.team_id)
        team_ids = icc_teams
    elif game_input.team_id in ipl_teams:
        ipl_teams.remove(game_input.team_id)
        team_ids = ipl_teams
    else:
        team_ids = icc_teams + ipl_teams

    enemy_team_id = random.choice(team_ids)

    # Fetch team and players data
    async with context.data_store.acquire() as connection:
        context.ds_connection = connection
        user_team = await get_team_by_id(
            team_id=game_input.team_id,
            context=context,
        )
        user_team_name = user_team["team_name"]

        user_team_players = await get_players_by_team_id(
            team_id=game_input.team_id,
            context=context,
        )

        enemy_team = await get_team_by_id(
            team_id=enemy_team_id,
            context=context,
        )
        enemy_team_name = enemy_team["team_name"]
        enemy_team_players = await get_players_by_team_id(
            team_id=enemy_team_id,
            context=context,
        )

    user_batting_lineup = []
    user_bowling_lineup = []

    player_data = {}
    for player in user_team_players:
        player_data[player["player_id"]] = player

    for player_id in game_input.batting_lineup:
        user_batting_lineup.append(player_data[player_id])

    for player_id in game_input.bowling_lineup:
        user_bowling_lineup.append(player_data[player_id])

    while len(user_bowling_lineup) < 20:
        user_bowling_lineup += user_bowling_lineup
    user_bowling_lineup = user_bowling_lineup[:20]

    # generate batting and bowling lineups for bot team
    enemy_bowling_lineup = [
        player
        for player in enemy_team_players
        if player["player_type"] in ("bowler", "all-rounder")
    ]

    while len(enemy_bowling_lineup) < 20:
        enemy_bowling_lineup += enemy_bowling_lineup
    enemy_bowling_lineup = enemy_bowling_lineup[:20]

    # Toss generate random number and decide who will bat first
    toss_string = "%s won the toss and elected to bat first"
    toss = random.randint(0, 1)
    if toss == 0:
        game_results = await simulate_game(
            team_one_batting=user_batting_lineup,
            team_one_bowling=user_bowling_lineup,
            team_two_batting=enemy_team_players,
            team_two_bowling=enemy_bowling_lineup,
        )
        game_results["team_name"] = user_team_name
        game_results["enemy_team_name"] = enemy_team_name
        game_results["toss_result"] = toss_string % user_team_name
    else:
        game_results = await simulate_game(
            team_one_batting=enemy_team_players,
            team_one_bowling=enemy_bowling_lineup,
            team_two_batting=user_batting_lineup,
            team_two_bowling=user_bowling_lineup,
        )
        game_results["team_name"] = enemy_team_name
        game_results["enemy_team_name"] = user_team_name
        game_results["toss_result"] = toss_string % enemy_team_name

    # update game metrics
    live_metrics = context.cache_store.get_dictionary("live_metrics")
    await context.logger.info("Live game started, updating metrics")

    if "games_played" not in live_metrics:
        live_metrics["games_played"] = 0
        live_metrics["games_live"] = 0

    live_metrics["games_played"] += 1
    live_metrics["games_live"] += 1
    game_results["game_id"] = str(uuid.uuid4())

    game_results["user_team"] = player_data
    game_results["enemy_team"] = {
        player["player_id"]: player for player in enemy_team_players
    }
    # print(json.dumps(game_results, indent=4))
    return game_results
