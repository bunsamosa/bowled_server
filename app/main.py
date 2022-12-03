import structlog
from app.import_routes import import_routes
from app.middlewares import log_request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from lib.core.cache_store import CacheStore
from lib.core.logger import initialize_logger


# Create fastAPI app
app = FastAPI()

# Add middlewares
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BaseHTTPMiddleware, dispatch=log_request)


###############################################################################
# Rest server startup hooks
###############################################################################
@app.on_event("startup")
async def startup_event() -> None:
    """
    Initialize modules and attach them to app
    """
    # cachestore
    app.cache_store = CacheStore(namespace="rest_server")
    app.secret_store = CacheStore(namespace="secrets")

    # logger
    initialize_logger()
    app.logger = structlog.get_logger("rest_server")

    # routers
    import_routes(app)
