from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request
from apis.model import Team

# Create fast API router
router = APIRouter()


@router.post(
    path="/team",
)
async def create_team(request: Request, data: Team):
    """
    Create new team
    """
    return JSONResponse(dict(data))
