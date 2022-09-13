import uuid

import structlog
from fastapi import Request


async def log_request(request: Request, call_next):
    """
    Bind request context variables to the logger
    """
    # Bind vars to structlog logger
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        url=request.url.path,
        request_id=uuid.uuid4().hex,
    )

    # Process API call
    response = await call_next(request)
    return response
