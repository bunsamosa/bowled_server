from typing import List

from pydantic import BaseModel
from pydantic import Field


class PublicTeam(BaseModel):
    """
    This model represents a public team
    """

    team_id: str = Field(description="Team ID")
    team_logo: str = Field(description="URL to team logo image")
    team_name: str = Field(description="Team name")


class PublicTeamPlayer(BaseModel):
    """
    This model represents a public team player
    """

    player_id: int = Field(description="Player ID")
    team_id: str = Field(description="Team ID")
    player_name: str = Field(description="Player name")
    player_type: str = Field(description="Player type")
    dob: str = Field(description="Date of birth in milliseconds")
    fitness: str = Field(description="Fitness attribute level")
    form: str = Field(description="Form attribute level")
    batting_type: str = Field(description="Batting type")
    bowling_type: str = Field(description="Bowling type")

    fielding_index: int = Field(description="Fielding skill index")
    fielding: str = Field(description="Fielding skill level")
    fielding_color: str = Field(description="Fielding skill color")

    wicket_keeping_index: int = Field(description="Wicket keeping skill index")
    wicket_keeping: str = Field(description="Wicket keeping skill level")
    wicket_keeping_color: str = Field(description="Wicket keeping skill color")

    batting_seam_index: int = Field(description="Batting seam skill index")
    batting_seam: str = Field(description="Batting seam skill level")
    batting_seam_color: str = Field(description="Batting seam skill color")

    batting_spin_index: int = Field(description="Batting spin skill index")
    batting_spin: str = Field(description="Batting spin skill level")
    batting_spin_color: str = Field(description="Batting spin skill color")

    bowling_main_index: int = Field(description="Bowling main skill index")
    bowling_main: str = Field(description="Bowling main skill level")
    bowling_main_color: str = Field(description="Bowling main skill color")

    bowling_variation_index: int = Field(
        description="Bowling variation skill index",
    )
    bowling_variation: str = Field(description="Bowling variation skill level")
    bowling_variation_color: str = Field(
        description="Bowling variation skill color",
    )

    batting_rating: int = Field(description="Batting rating")
    bowling_rating: int = Field(description="Bowling rating")


class LiveMetrics(BaseModel):
    """
    This model represents live metrics such as games live and total games
    """

    games_played: int = Field(default=0, description="Total games played")
    games_live: int = Field(default=0, description="Games live now")


class LiveGameInput(BaseModel):
    team_id: str
    batting_lineup: List[int]
    bowling_lineup: List[int]
