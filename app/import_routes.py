from fastapi import FastAPI
from apis import team, game


def import_routes(app: FastAPI) -> None:
    """
    Import routes from different modules and add them to the main application
    """
    app.include_router(team.router)
    app.include_router(game.router)
