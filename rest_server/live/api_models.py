from typing import List

from pydantic import BaseModel


class LiveGameInput(BaseModel):
    team_id: str
    batting_lineup: List[str]
    bowling_lineup: List[str]
