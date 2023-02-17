from typing import List

from fastapi import APIRouter
from fastapi import Request

from gamelib.team.public_team import get_all_teams
from rest_server.live.api_models import PublicTeam

# Create FastAPI router
router = APIRouter(prefix="/live")


@router.get(path="/teams", response_model=List[PublicTeam], tags=["Live"])
async def get_teams(request: Request) -> List[PublicTeam]:
    """
    This API returns a list of public teams
    """
    datastore = request.app.data_store
    logger = request.app.logger
    await logger.info("Get live teams API")

    # Fetch teams data from postgres
    async with datastore.acquire() as connection:
        team_data = await get_all_teams(
            ds_connection=connection,
            cachestore=None,
        )

    return team_data
