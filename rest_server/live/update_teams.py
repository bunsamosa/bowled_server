from typing import Dict

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from lib.utils.player_generator import fill_skill_colors

# Create FastAPI router
router = APIRouter(prefix="/live")


@router.post(path="/update-teams", tags=["Live"], response_model=Dict)
async def update_teams(request: Request, data: Dict) -> HTTPException:
    """
    Update teams API
    """
    cache_store = request.app.cache_store
    logger = request.app.logger
    live_teams = cache_store.get_dictionary("live_teams")
    await logger.info("Update teams API")

    if not data:
        return live_teams

    id_gen = cache_store.get_id_generator(key="players")
    for team_id in data:
        player_data = []
        players = data[team_id]["players"]

        for player in players:
            player_id = next(id_gen)
            player["player_id"] = player_id
            updated_player = fill_skill_colors(player)
            player_data.append(updated_player)

        data[team_id]["players"] = player_data

    # Read available teams data from redis
    live_teams.clear()
    live_teams.update(data)

    return live_teams
