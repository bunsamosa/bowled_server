from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class GetUserResponse(BaseModel):
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
