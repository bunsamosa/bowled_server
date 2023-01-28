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
    # teams = cache_store.get_dictionary("live_teams")
    # TODO: read data from database
    teams = {
        "mi": {
            "team_name": "Mumbai Indians",
            "team_id": "mi",
            "team_logo": "https://static.wikia.nocookie.net/logopedia/images/5/50/MI.png",
        },
        "kkr": {
            "team_name": "Kolkata Knight Riders",
            "team_id": "kkr",
            "team_logo": "https://static.wikia.nocookie.net/logopedia/images/4/49/Kolkata_Knight_Riders_logo.svg/",
        },
        "csk": {
            "team_name": "Chennai Super Kings",
            "team_id": "csk",
            "team_logo": "https://static.wikia.nocookie.net/logopedia/images/8/83/Chennai_Super_Kings_logo.svg",
        },
        "dc": {
            "team_name": "Delhi Capitals",
            "team_id": "dc",
            "team_logo": "https://static.wikia.nocookie.net/logopedia/images/d/d2/Delhi_Capitals.png",
        },
    }
    return tuple(teams.values())
