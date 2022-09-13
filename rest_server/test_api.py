from fastapi import APIRouter
from fastapi.responses import JSONResponse
from rest_server.api_schema import SampleInput

# Create fast API router
router = APIRouter()


@router.post(
    path="/sample",
    tags=["Sample"],
)
async def sample_api(
    data: SampleInput,
):
    """
    Sample API
    """
    return JSONResponse(data.dict())
