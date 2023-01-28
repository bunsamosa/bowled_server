from typing import List
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from lib.utils.player_generator import generate_players

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
    }
    live_teams = cache_store.get_dictionary(key="live_teams")
    live_teams.update(teams)

    id_gen = cache_store.get_id_generator(key="players")

    live_players = cache_store.get_dictionary(key="live_players")
    for team_id in teams:
        if team_id not in live_players:
            team1 = generate_players(
                names=request.app.player_names,
                id_gen=id_gen,
            )
            live_players[team_id] = team1

    return tuple(teams.values())
