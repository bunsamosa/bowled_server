from fastapi import FastAPI
from rest_server.monitoring import heartbeat


def import_routes(app: FastAPI) -> None:
    """
    Import routes from different modules and add them to the main application
    """
    app.include_router(heartbeat.router)
