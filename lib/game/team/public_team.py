from pypika.terms import Star

from lib.game.data_models import public_team_players
from lib.game.player.public_player import fill_skill_attribute_labels


async def get_players_by_team_id(team_id: str, ds_connection, cachestore):
    """
    This function returns players for a given team
    :param team_id: string team id
    :param ds_connection: datastore connection
    :param cachestore: cachestore connection
    """
    # Read skill and attribute labels from cachestore

    # Fetch players data from postgres
    data_query = public_team_players.select(Star()).where(
        public_team_players.team_id.eq(team_id),
    )
    data_query = data_query.get_sql()
    player_data = await ds_connection.fetch(data_query)

    # Fill skill and attribute labels
    team_players = []
    for player in player_data:
        filled_player = await fill_skill_attribute_labels(
            player=player,
            ds_connection=ds_connection,
            cachestore=cachestore,
        )
        team_players.append(filled_player)

    return team_players
