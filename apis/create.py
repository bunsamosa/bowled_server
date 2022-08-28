from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request
from apis.model import Team
from engine.team_generation import TeamBuilder

# Create fast API router
router = APIRouter()


@router.post(
    path="/team",
)
async def create_team(request: Request, data: Team):
    """
    Create new team
    """
    team = TeamBuilder(data.manager)

    team1 = team.build_new_team(data.teamName)
    team1["manager"] = data.manager
    team1["team_name"] = data.teamName
    team1["team_id"] = data.teamName
    team1["country"] = data.country

    storage = request.app.cachestore.get_dictionary(data.userID)
    storage.update(team1)
    return JSONResponse(team1)
