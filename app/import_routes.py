from fastapi import FastAPI

from rest_server.live import get_metrics
from rest_server.live import get_teams
from rest_server.live import live_game
from rest_server.live import live_players
from rest_server.live import start_game
from rest_server.live import update_teams
from rest_server.monitoring import heartbeat
from rest_server.monitoring import index
from rest_server.system_management import reload_cache


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
    # System management
    ###########################################################################
    app.include_router(reload_cache.router)

    ###########################################################################
    # Live
    ###########################################################################
    app.include_router(get_teams.router)
    app.include_router(get_metrics.router)
    app.include_router(live_game.router)
    app.include_router(start_game.router)
    app.include_router(live_players.router)
    app.include_router(update_teams.router)
