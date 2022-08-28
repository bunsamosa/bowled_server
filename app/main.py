from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.import_routes import import_routes
from app.cachestore import CacheStore

# Create fastAPI app
app = FastAPI()


###############################################################################
# Rest server startup hooks
###############################################################################
@app.on_event("startup")
async def startup_event() -> None:
    app.cachestore = CacheStore(namespace="stumped")
    import_routes(app)


# Add CORS rules
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
