import os

from pypika import Table

POSTGRES_SCHEMA = os.getenv(
    key="POSTGRES_SCHEMA",
    default="dev",
)


###############################################################################
# Postgres tables
###############################################################################

# Public Team data
public_teams = Table("public_teams", schema=POSTGRES_SCHEMA)
public_team_players = Table("public_team_players", schema=POSTGRES_SCHEMA)


# Player skills and attributes
skill_index_labels = Table("skill_index_labels", schema=POSTGRES_SCHEMA)
attribute_index_labels = Table(
    "attribute_index_labels",
    schema=POSTGRES_SCHEMA,
)
