import asyncio
from typing import Dict
from typing import Union

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import HTTPException
from fastapi import Request

from lib.utils.player_generator import generate_players
from lib.utils.simulate_game import simulate_game

# Create FastAPI router
router = APIRouter(prefix="/live")


async def game_finished(cache_store, logger):
    # a game has finished, update metrics
    finish_time = 30 * 60
    await asyncio.sleep(finish_time)

    live_metrics = cache_store.get_dictionary("live_metrics")
    if (live_metrics["games_live"]) > 0:
        live_metrics["games_live"] -= 1
        await logger.info("Live game finished, updating metrics")


@router.get(path="/game", response_model=Dict, tags=["Live"])
async def play_game(
    request: Request,
    myteam: str,
    bg_handler: BackgroundTasks,
) -> Union[Dict, HTTPException]:
    """
    Simulate game API
    """
    cache_store = request.app.cache_store
    logger = request.app.logger
    await logger.info("Simulate game API")

    live_teams = cache_store.get_dictionary(key="live_teams")
    id_gen = cache_store.get_id_generator(key="players")
    user_team = live_teams.get(myteam)

    if not user_team:
        user_team_name = "BOT User"
        user_players = generate_players(
            names=request.app.player_names,
            id_gen=id_gen,
        )
    else:
        user_team_name = user_team["team_name"]
        user_players = user_team["players"]

    # generate bot team to play with
    bot_players = generate_players(names=request.app.player_names)
    game_results = simulate_game(
        team1=user_players,
        team2=tuple(bot_players.values()),
    )
    game_results["team_name"] = user_team_name
    game_results["enemy_team"] = "BOT Army"

    # update game metrics
    live_metrics = cache_store.get_dictionary("live_metrics")
    await logger.info("Live game started, updating metrics")
    live_metrics["games_played"] += 1
    live_metrics["games_live"] += 1

    # add a task to the background handler
    bg_handler.add_task(game_finished, cache_store, logger)
    return game_results
