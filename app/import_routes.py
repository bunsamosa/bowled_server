from fastapi import FastAPI

from rest_server.live import get_metrics
from rest_server.live import get_players
from rest_server.live import get_teams
from rest_server.live import live_game
from rest_server.live import start_game
from rest_server.monitoring import heartbeat
from rest_server.monitoring import index
from rest_server.system_management import reload_cache

# Import the new turn-based routers
from rest_server.turn_based_match import start_match as tb_start_match
from rest_server.turn_based_match import select_openers as tb_select_openers
from rest_server.turn_based_match import select_bowler as tb_select_bowler
from rest_server.turn_based_match import select_batsman as tb_select_batsman
from rest_server.turn_based_match import bowl_next_ball as tb_bowl_next_ball
from rest_server.turn_based_match import get_state as tb_get_state
from rest_server.turn_based_match import stream_state as tb_stream_state
from rest_server.turn_based_match import (
    start_second_innings as tb_start_second_innings
)


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
    app.include_router(get_players.router)

    ###########################################################################
    # Turn Based Match (New)
    ###########################################################################
    app.include_router(tb_start_match.router)
    app.include_router(tb_select_openers.router)
    app.include_router(tb_select_bowler.router)
    app.include_router(tb_select_batsman.router)
    app.include_router(tb_bowl_next_ball.router)
    app.include_router(tb_get_state.router)
    app.include_router(tb_stream_state.router)
    app.include_router(tb_start_second_innings.router)
