from fastapi import APIRouter
from fastapi import Request

from rest_server.live.api_models import LiveMetrics


# Create FastAPI router
router = APIRouter(prefix="/live")


@router.get(path="/metrics", response_model=LiveMetrics, tags=["Live"])
async def get_live_metrics(
    request: Request,
    resetlive: bool = False,
) -> LiveMetrics:
    """
    This API returns live metrics such as games live and total games
    :param resetlive: Reset current live games
    """
    cache_store = request.app.cache_store
    logger = request.app.logger
    await logger.info("Get live metrics API")

    # Read available teams data from redis
    live_metrics = cache_store.get_dictionary("live_metrics")

    # reset live games metrics
    if resetlive:
        live_metrics["games_live"] = 0

    return live_metrics
