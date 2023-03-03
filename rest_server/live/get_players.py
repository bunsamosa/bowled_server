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
    context = request.state.context
    await context.logger.info("Get players API")

    # Fetch players data from postgres
    async with context.datastore.acquire() as connection:
        context.ds_connection = connection
        player_data = await get_players_by_team_id(
            team_id=team,
            context=context,
        )

    return player_data
