from typing import List

from fastapi import APIRouter
from fastapi import Request

from gamelib.team.live_team import get_all_teams
from rest_server.live.api_models import LiveTeam

# Create FastAPI router
router = APIRouter(prefix="/live")


@router.get(path="/teams", response_model=List[LiveTeam], tags=["Live"])
async def get_teams(request: Request) -> List[LiveTeam]:
    """
    This API returns a list of live teams
    """
    context = request.state.context
    await context.logger.info("Get live teams API")

    # Fetch teams data from postgres
    async with context.data_store.acquire() as connection:
        context.ds_connection = connection
        team_data = await get_all_teams(context=context)

    return team_data
