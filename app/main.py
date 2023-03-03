import json

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.import_routes import import_routes
from app.middlewares import create_context
from lib.core.cache_store import CacheStore
from lib.core.data_store import get_connection_pool
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

# add context middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=create_context)


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
    app.data_store = await get_connection_pool()

    # TODO delete legacy from here
    app.secret_store = CacheStore(namespace="secrets")
    address_key = "user_address"
    app.address_mapping = app.cache_store.get_dictionary(address_key)

    # load player names in memory
    with open("lib/utils/final_names.json", encoding="UTF-8") as f:
        app.player_names = json.load(f)
    # TODO delete till here

    # logger
    initialize_logger()
    app.logger = structlog.get_logger("rest_server")

    # routers
    import_routes(app)
