from typing import Dict
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from lib.core.auth_bearer import handler
from lib.utils.player_generator import generate_players
from lib.utils.simulate_game import simulate_game

# Create FastAPI router
router = APIRouter(prefix="/team")


@router.get(path="/game", response_model=Dict, tags=["Team"])
async def play_game(
    request: Request,
    user=handler,
) -> Union[Dict, HTTPException]:
    """
    Simulate game API
    """
    cache_store = request.app.cache_store
    logger = request.app.logger
    await logger.info("Simulate game API")

    # Read user_id from auth data
    user_id = user.get("sub", None)
    if not user_id:
        raise HTTPException(status_code=401)

    # Check if the user exists
    user_address = request.app.address_mapping.get(user_id)
    if not user_address:
        raise HTTPException(status_code=403)

    # Fetch player from users team
    data_key = f"user_data_{user_address}"
    user_data = cache_store.get_dictionary(data_key)
    team1 = user_data.get("players", None)

    if team1 is None:
        id_gen = cache_store.get_id_generator(key="players")
        team1 = generate_players(
            names=request.app.player_names,
            id_gen=id_gen,
        )
        user_data["players"] = team1

    # generate bot team to play with
    bot_players = generate_players(names=request.app.player_names)
    game_results = simulate_game(
        team1=tuple(team1.values()),
        team2=tuple(bot_players.values()),
    )
    game_results["team_name"] = user_data["team_name"]
    game_results["enemy_team"] = "BOT Army"
    return game_results
