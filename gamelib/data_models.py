import os

from pypika import Table

POSTGRES_SCHEMA = os.getenv(
    key="POSTGRES_SCHEMA",
    default="dev",
)


###############################################################################
# Postgres tables
###############################################################################

# Live Team data
live_teams = Table("live_teams", schema=POSTGRES_SCHEMA)
live_team_players = Table("live_team_players", schema=POSTGRES_SCHEMA)


# Player skills and attributes
skill_index_labels = Table("skill_index_labels", schema=POSTGRES_SCHEMA)
attribute_index_labels = Table(
    "attribute_index_labels",
    schema=POSTGRES_SCHEMA,
)
