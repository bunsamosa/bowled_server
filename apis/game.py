import imp
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request
from engine.team_generation import TeamBuilder, get_batting_bowling_lineup
from engine.game_engine import GameEngine

# Create fast API router
router = APIRouter()


@router.get(
    path="/game/{teamID}",
)
async def play_game(request: Request, teamID: str):
    """
    Play game against a random team
    """
    current_team = request.app.cachestore.get_dictionary(teamID)
    current_team = dict(current_team)

    # Build random team
    name = "Army Ants"
    team = TeamBuilder(name)
    team1 = team.build_new_team(name)
    team1["manager"] = "Stumped BOT"
    team1["team_name"] = name
    team1["team_id"] = name
    team1["country"] = current_team["country"]

    team1["batting_lineup"], team1["bowling_lineup"] = get_batting_bowling_lineup(team1)
    current_team["batting_lineup"], current_team["bowling_lineup"] = get_batting_bowling_lineup(current_team)

    gg = GameEngine("id", current_team, team1, current_team["team_id"])
    response = dict(gg.game_results)

    return JSONResponse(response)
