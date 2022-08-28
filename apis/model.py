from pydantic import BaseModel
from pydantic import Field


class Team(BaseModel):
    """
    JSON schema for input data
    """

    userID: str = Field(min_length=3, description="User ID")
    teamName: str = Field(min_length=3, description="Team Name")
    manager: str = Field(min_length=3, description="Manager Name")
    country: str = Field(min_length=3, description="Country")
