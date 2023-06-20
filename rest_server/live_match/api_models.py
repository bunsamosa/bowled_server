from typing import List

from pydantic import BaseModel
from pydantic import Field


class MatchInputs(BaseModel):
    """
    Parameters required to start a match
    """

    team_id: str = Field(description="Team ID to start the game", min_length=2)
    playing_xi: List[int] = Field(
        description="List of 11 player IDs to play the game",
        min_items=11,
        max_items=11,
    )


class ScoreBanner(BaseModel):
    """
    Score banner
    """

    name: str = Field(description="Team name")
    score: int = Field(description="Runs scored")
    wickets: int = Field(description="Wickets lost")
    overs: float = Field(description="Overs played")
    toss_banner: str = Field(description="Toss banner")
    current_over_outcomes: List[str] = Field(
        description="Outcomes in the current over",
    )


class TossInfo(BaseModel):
    """
    Toss information
    """

    caller: str = Field(description="Team ID of the caller")
    side_picked: str = Field(description="Side picked by the caller")
    result: str = Field(description="Toss result")
    winner: str = Field(description="Toss winner")
    strategy_picked: str = Field(description="Strategy picked by the winner")
    banner: str = Field(description="Toss banner")


class MatchInfo(BaseModel):
    """
    Match information
    """

    team1_id: str = Field(description="Team 1 ID")
    team2_id: str = Field(description="Team 2 ID")

    team1_name: str = Field(description="Team 1 name")
    team2_name: str = Field(description="Team 2 name")

    team1_score_banner: ScoreBanner = Field(description="Team 1 score banner")
    team2_score_banner: ScoreBanner = Field(description="Team 2 score banner")

    toss_info: TossInfo = Field(description="Toss information", default=None)
    match_id: str = Field(description="Match ID", default=None)
