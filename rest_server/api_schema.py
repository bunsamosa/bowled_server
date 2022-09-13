from pydantic import BaseModel
from pydantic import Field


class SampleInput(BaseModel):
    """
    JSON schema for input data
    """

    input_name: str = Field(min_length=3, description="Name")
