from typing import Dict
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from lib.utils.player_generator import generate_players
from lib.utils.simulate_game import simulate_game

# Create FastAPI router
router = APIRouter(prefix="/live")


@router.get(path="/game", response_model=Dict, tags=["Live"])
async def play_game(
    request: Request,
    myteam: str,
) -> Union[Dict, HTTPException]:
    """
    Simulate game API
    """
    cache_store = request.app.cache_store
    logger = request.app.logger
    await logger.info("Simulate game API")

    live_teams = cache_store.get_dictionary(key="live_teams")
    id_gen = cache_store.get_id_generator(key="players")
    team1 = generate_players(
        names=request.app.player_names,
        id_gen=id_gen,
    )

    # generate bot team to play with
    bot_players = generate_players(names=request.app.player_names)
    game_results = simulate_game(
        team1=tuple(team1.values()),
        team2=tuple(bot_players.values()),
    )

    user_team = live_teams.get(myteam)
    if not user_team:
        game_results["team_name"] = "BOT User"
    else:
        game_results["team_name"] = user_team["team_name"]
    game_results["enemy_team"] = "BOT Army"
    return game_results
