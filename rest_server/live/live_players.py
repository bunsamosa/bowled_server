from typing import List
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from lib.utils.player_generator import fill_skill_colors

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
    live_teams = cache_store.get_dictionary(key="live_teams")
    team_data = live_teams.get(myteam)

    # Update player data
    player_data = []
    for player in team_data["players"]:
        updated_player = fill_skill_colors(player)
        player_data.append(updated_player)
    team_data["players"] = player_data
    live_teams[myteam] = team_data

    return player_data
