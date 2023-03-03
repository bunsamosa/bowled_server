import uuid

import structlog
from fastapi import Request

from lib.core.server_context import Context


async def create_context(request: Request, call_next):
    """
    Create server context and bind it to the request
    Also bind request context variables to the logger
    """
    # Generate request ID
    request_id = uuid.uuid4().hex

    # Create context
    # ds_connection is kept null by default
    # individual request should acquire a connection from the pool
    # and bind it to the context whenever required
    server_context = Context(
        logger=request.app.logger,
        request_id=request_id,
        cachestore=request.app.cache_store,
        data_store=request.app.data_store,
        ds_connection=None,
    )

    # Bind vars to structlog logger
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        url=request.url.path,
        request_id=request_id,
    )

    # Bind context to request state
    request.state.context = server_context

    # Process API call
    response = await call_next(request)
    return response
