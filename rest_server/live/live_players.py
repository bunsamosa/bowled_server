from typing import List
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from lib.game.team.public_team import get_players_by_team_id

# Create FastAPI router
router = APIRouter(prefix="/live")


@router.get(path="/players", response_model=List, tags=["Live"])
async def get_players(
    request: Request,
    team: str,
) -> Union[List, HTTPException]:
    """
    This API returns players for a given team
    """
    datastore = request.app.data_store
    cachestore = request.app.cache_store
    logger = request.app.logger
    await logger.info("Get players API")

    # Fetch players data from postgres
    async with datastore.acquire() as connection:
        player_data = await get_players_by_team_id(
            team_id=team,
            ds_connection=connection,
            cachestore=cachestore,
        )

    return player_data
