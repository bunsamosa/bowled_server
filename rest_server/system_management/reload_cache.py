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
    context = request.state.context
    await context.logger.info("Reload cache API")

    # Reload cache
    async with context.datastore.acquire() as connection:
        context.ds_connection = connection
        await load_skills_attributes.load_data(context=context)
    await context.logger.info("Cache reloaded successfully")

    return Response(status_code=200)
