from typing import List
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

# Create FastAPI router
router = APIRouter(prefix="/live")


@router.get(path="/players", response_model=List, tags=["Live"])
async def get_players(
    request: Request,
    myteam: str,
) -> Union[List, HTTPException]:
    """
    Get players API
    """
    cache_store = request.app.cache_store
    logger = request.app.logger
    await logger.info("Get players API")
    live_players = cache_store.get_dictionary(key="live_players")
    user_players = live_players.get(myteam)

    return tuple(user_players.values())
