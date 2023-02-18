from typing import List

from fastapi import APIRouter
from fastapi import Request

from gamelib.team.public_team import get_players_by_team_id
from rest_server.live.api_models import PublicTeamPlayer

# Create FastAPI router
router = APIRouter(prefix="/live")


@router.get(
    path="/players",
    response_model=List[PublicTeamPlayer],
    tags=["Live"],
)
async def get_players(
    request: Request,
    team: str,
) -> List[PublicTeamPlayer]:
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
