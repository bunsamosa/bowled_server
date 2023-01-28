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
    live_players = cache_store.get_dictionary(key="live_players")
    id_gen = cache_store.get_id_generator(key="players")
    user_team = live_teams.get(myteam)

    if not user_team:
        user_team_name = "BOT User"
        user_players = generate_players(
            names=request.app.player_names,
            id_gen=id_gen,
        )
    else:
        user_team = live_teams.get(myteam)
        user_team_name = user_team["team_name"]
        user_players = live_players.get(myteam)

    # generate bot team to play with
    bot_players = generate_players(names=request.app.player_names)
    game_results = simulate_game(
        team1=tuple(user_players.values()),
        team2=tuple(bot_players.values()),
    )
    game_results["team_name"] = user_team_name
    game_results["enemy_team"] = "BOT Army"
    return game_results
