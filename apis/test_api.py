from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request
from apis.api_schema import SampleInput

# Create fast API router
router = APIRouter()


@router.post(
    path="/sample",
    tags=["Sample"],
)
async def sample_api(
    request: Request,
    data: SampleInput,
):
    """
    Sample API
    """
    return JSONResponse(data.dict())
