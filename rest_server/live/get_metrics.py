from typing import Dict
from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request


# Create FastAPI router
router = APIRouter(prefix="/live")


@router.get(path="/metrics", response_model=Dict, tags=["Live"])
async def get_live_metrics(
    request: Request,
    resetlive: bool = False,
) -> Union[dict, HTTPException]:
    """
    Get metrics API
    """
    cache_store = request.app.cache_store
    logger = request.app.logger
    await logger.info("Live metrics API")

    # Read available teams data from redis
    live_metrics = cache_store.get_dictionary("live_metrics")

    # reset live games metrics
    if resetlive:
        live_metrics["games_live"] = 0

    return live_metrics
