from typing import Dict
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

# Create FastAPI router
router = APIRouter(prefix="/live")


@router.get(path="/game", response_model=Dict, tags=["Live"])
async def live_game(
    request: Request,
    gameid: str,
) -> Union[Dict, HTTPException]:
    """
    Simulate game API
    """
    cache_store = request.app.cache_store
    logger = request.app.logger
    await logger.info("Fetch game data API")

    game_results = cache_store.get_dictionary(key=gameid)
    return game_results
