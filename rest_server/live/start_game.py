import asyncio
import random
import uuid
from typing import Dict
from typing import Union

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import HTTPException
from fastapi import Request

from gamelib.team.public_team import get_players_by_team_id
from gamelib.team.public_team import get_team_by_id
from lib.utils.player_generator import generate_players
from lib.utils.simulate_game import simulate_game
from rest_server.live.api_models import LiveGameInput

# Create FastAPI router
router = APIRouter(prefix="/live")


async def game_finished(cache_store, logger):
    # a game has finished, update metrics
    finish_time = 600
    await asyncio.sleep(finish_time)

    live_metrics = cache_store.get_dictionary("live_metrics")
    if (live_metrics["games_live"]) > 0:
        live_metrics["games_live"] -= 1
        await logger.info("Live game finished, updating metrics")


@router.post(
    path="/game",
    response_model=Dict,
    tags=["Live"],
)
async def play_game(
    request: Request,
    game_input: LiveGameInput,
    bg_handler: BackgroundTasks,
) -> Union[Dict, HTTPException]:
    """
    Simulate game API
    """
    cache_store = request.app.cache_store
    data_store = request.app.data_store
    logger = request.app.logger
    await logger.info("Simulate game API")

    # TODO: Validate input data

    # Fetch team and players data
    async with data_store.acquire() as connection:
        user_team = await get_team_by_id(
            team_id=game_input.team_id,
            ds_connection=connection,
            cachestore=cache_store,
        )
        user_team_name = user_team["team_name"]

        user_team_players = await get_players_by_team_id(
            team_id=game_input.team_id,
            ds_connection=connection,
            cachestore=cache_store,
        )

    batting_lineup = []
    bowling_lineup = []

    player_data = {}
    for player in user_team_players:
        player_data[player["player_id"]] = player

    for player_id in game_input.batting_lineup:
        batting_lineup.append(player_data[player_id])

    for player_id in game_input.bowling_lineup:
        bowling_lineup.append(player_data[player_id])

    # generate bot team to play with
    bot_players = generate_players(names=request.app.player_names)

    # Toss generate random number and decide who will bat first
    toss_string = "%s won the toss and elected to bat first"
    toss = random.randint(0, 1)
    if toss == 0:
        game_results = simulate_game(
            team1=batting_lineup,
            team2=tuple(bot_players.values()),
            bowling_team1=bowling_lineup,
        )
        game_results["team_name"] = user_team_name
        game_results["enemy_team"] = "BOT Army"
        game_results["toss_result"] = toss_string % user_team_name
    else:
        game_results = simulate_game(
            team1=tuple(bot_players.values()),
            team2=batting_lineup,
            bowling_team2=bowling_lineup,
        )
        game_results["team_name"] = "BOT Army"
        game_results["enemy_team"] = user_team_name
        game_results["toss_result"] = toss_string % "BOT Army"

    # update game metrics
    live_metrics = cache_store.get_dictionary("live_metrics")
    await logger.info("Live game started, updating metrics")

    if "games_played" not in live_metrics:
        live_metrics["games_played"] = 0
        live_metrics["games_live"] = 0

    live_metrics["games_played"] += 1
    live_metrics["games_live"] += 1
    game_results["game_id"] = str(uuid.uuid4())

    # add a task to the background handler
    bg_handler.add_task(game_finished, cache_store, logger)
    return game_results
