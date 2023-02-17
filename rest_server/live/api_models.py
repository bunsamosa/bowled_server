from typing import List

from pydantic import BaseModel


class PublicTeam(BaseModel):
    """
    This model represents a public team
    """

    team_id: str
    team_logo: str
    team_name: str


class LiveGameInput(BaseModel):
    team_id: str
    batting_lineup: List[int]
    bowling_lineup: List[int]
