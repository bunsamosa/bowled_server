from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request

# Create fast API router
router = APIRouter()


@router.get(
    path="/team/{teamID}",
)
async def fetch_team(request: Request, teamID: str):
    """
    Get an existing team or create new team
    """
    team = request.app.cachestore.get_dictionary(teamID)
    team = dict(team)

    return JSONResponse(team)
