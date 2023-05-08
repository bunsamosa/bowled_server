from typing import Tuple

from pypika.terms import Star

from gamelib.data_models import live_team_players
from gamelib.data_models import live_teams
from gamelib.player.live_player import fill_skill_attribute_labels
from lib.core.server_context import Context


async def get_players_by_team_id(team_id: str, context: Context):
    """
    This function returns players for a given team
    :param team_id: string team id
    :param context: server context
    """
    # Read skill and attribute labels from cachestore

    # Fetch players data from postgres
    data_query = live_team_players.select(Star()).where(
        live_team_players.team_id.eq(team_id),
    )
    data_query = data_query.get_sql()
    player_data = await context.ds_connection.fetch(data_query)

    # Fill skill and attribute labels
    team_players = []
    for player in player_data:
        filled_player = await fill_skill_attribute_labels(
            player=player,
            context=context,
        )
        team_players.append(filled_player)

    return team_players


async def get_all_teams(context: Context) -> Tuple[dict]:
    """
    This function returns all teams
    :param context: server context
    """
    # Fetch teams data from postgres
    data_query = live_teams.select(Star())
    data_query = data_query.get_sql()
    team_data = await context.ds_connection.fetch(data_query)

    return tuple(map(dict, team_data))


async def get_team_by_id(team_id: str, context: Context) -> dict:
    """
    This function returns team data for a given team id
    :param team_id: string team id
    :param context: server context
    """
    # Fetch teams data from postgres
    data_query = live_teams.select(Star()).where(
        live_teams.team_id.eq(team_id),
    )
    data_query = data_query.get_sql()
    team_data = await context.ds_connection.fetchrow(data_query)

    return dict(team_data)
