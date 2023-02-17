from typing import List

from fastapi import APIRouter
from fastapi import Request
from pypika.terms import Star

from rest_server.data_models import public_teams
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
        data_query = public_teams.select(Star())
        data_query = data_query.get_sql()
        teams = await connection.fetch(data_query)

    return teams
