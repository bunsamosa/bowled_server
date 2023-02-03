from typing import List

from pydantic import BaseModel


class LiveGameInput(BaseModel):
    team_id: str
    batting_lineup: List[int]
    bowling_lineup: List[int]
