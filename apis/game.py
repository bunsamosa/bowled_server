from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request

# Create fast API router
router = APIRouter()


@router.get(
    path="/game/{teamID}",
)
async def play_game(request: Request, teamID: str):
    """
    Play game against a random team
    """
    team = {}
    return JSONResponse(team)
