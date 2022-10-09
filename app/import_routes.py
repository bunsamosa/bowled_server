from fastapi import FastAPI
from rest_server.monitoring import heartbeat
from rest_server.monitoring import index
from rest_server.user import get_user


def import_routes(app: FastAPI) -> None:
    """
    Import routes from different modules and add them to the main application
    """
    ###########################################################################
    # Monitoring
    ###########################################################################
    app.include_router(index.router)
    app.include_router(heartbeat.router)

    ###########################################################################
    # User
    ###########################################################################
    app.include_router(get_user.router)
