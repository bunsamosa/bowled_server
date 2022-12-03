from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from rest_server.monitoring.api_schema import HeartBeat

# Create FastAPI router
router = APIRouter()


@router.get(path="/heartbeat", response_model=HeartBeat, tags=["Monitoring"])
async def heartbeat(request: Request) -> Union[HeartBeat, HTTPException]:
    """
    Heartbeat API
    """
    logger = request.app.logger
    response = HeartBeat()

    # Check if cachestore is connected
    try:
        response.cachestore_connected = request.app.cachestore.is_connected()
    except Exception as exc:
        await logger.error("Unable to connect to cachestore")
        await logger.error(exc)
        response.errors["cachestore"] = str(exc)

    # TODO check if datastore is connected
    return response
