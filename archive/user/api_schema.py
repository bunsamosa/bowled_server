from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class CreateUser(BaseModel):
    """
    JSON Schema for creating a user
    """

    manager_name: str = Field(description="Team manager name", min_length=3)
    team_name: str = Field(description="Team name", min_length=3)


class User(BaseModel):
    """
    JSON Schema for fetching User
    """

    signup_complete: bool = Field(
        description="Whether signup is complete",
        default=False,
    )
    user_id: Optional[str] = Field(description="User ID")
    manager_name: Optional[str] = Field(description="Team manager name")
    team_name: Optional[str] = Field(description="Team name")
    ens_address: Optional[str] = Field(description="ENS address of the team")
