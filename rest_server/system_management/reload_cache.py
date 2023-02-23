from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import Response

from gamelib.cache_manager import load_skills_attributes


# Create FastAPI router
router = APIRouter(prefix="/system")


@router.get(path="/reload-cache", tags=["System"])
async def reload_cache(request: Request):
    """
    This API calls the cache manager to reload the cache
    """
    logger = request.app.logger
    datastore = request.app.data_store
    cachestore = request.app.cache_store
    await logger.info("Reload cache API")

    # Reload cache
    async with datastore.acquire() as connection:
        await load_skills_attributes.load_data(
            ds_connection=connection,
            cachestore=cachestore,
        )
    await logger.info("Cache reloaded successfully")

    return Response(status_code=200)
