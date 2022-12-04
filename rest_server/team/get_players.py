from typing import List
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from lib.core.auth_bearer import handler
from lib.utils.player_generator import generate_players

# Create FastAPI router
router = APIRouter(prefix="/team")


@router.get(path="/players", response_model=List, tags=["Team"])
async def get_players(
    request: Request,
    user=handler,
) -> Union[List, HTTPException]:
    """
    Get players API
    """
    cache_store = request.app.cache_store
    logger = request.app.logger
    await logger.info("Get players API")

    # Read user_id from auth data
    user_id = user.get("sub", None)
    if not user_id:
        raise HTTPException(status_code=401)

    # Check if the user exists
    user_address = request.app.address_mapping.get(user_id)
    if not user_address:
        raise HTTPException(status_code=403)

    # fetch players if exists, else generate and render players
    data_key = f"user_data_{user_address}"
    user_data = cache_store.get_dictionary(data_key)

    players = user_data.get("players", None)
    if players is None:
        id_gen = cache_store.get_id_generator(key="players")
        players = generate_players(
            names=request.app.player_names,
            id_gen=id_gen,
        )
        user_data["players"] = players

    return tuple(players.values())
