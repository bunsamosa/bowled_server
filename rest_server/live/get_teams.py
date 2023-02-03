from typing import List
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

# Create FastAPI router
router = APIRouter(prefix="/live")


@router.get(path="/teams", response_model=List, tags=["Live"])
async def get_teams(request: Request) -> Union[List, HTTPException]:
    """
    Get teams API
    """
    cache_store = request.app.cache_store
    logger = request.app.logger
    await logger.info("Get teams API")

    # Read available teams data from redis
    teams = cache_store.get_dictionary("live_teams")
    response_data = []
    for team_id in teams:
        team_data = teams[team_id]
        # team_data.pop("players")
        response_data.append(team_data)

    return response_data
