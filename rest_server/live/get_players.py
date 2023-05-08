from typing import List

from fastapi import APIRouter
from fastapi import Request

from gamelib.team.live_team import get_players_by_team_id
from rest_server.live.api_models import LiveTeamPlayer

# Create FastAPI router
router = APIRouter(prefix="/live")


@router.get(
    path="/players",
    response_model=List[LiveTeamPlayer],
    tags=["Live"],
)
async def get_players(
    request: Request,
    team: str,
) -> List[LiveTeamPlayer]:
    """
    This API returns players for a given team
    """
    context = request.state.context
    await context.logger.info("Get players API")

    # Fetch players data from postgres
    async with context.data_store.acquire() as connection:
        context.ds_connection = connection
        player_data = await get_players_by_team_id(
            team_id=team,
            context=context,
        )

    return player_data
