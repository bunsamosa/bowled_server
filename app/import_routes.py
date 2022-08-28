from fastapi import FastAPI
from apis import test_api


def import_routes(app: FastAPI) -> None:
    """
    Import routes from different modules and add them to the main application
    """
    app.include_router(test_api.router)
