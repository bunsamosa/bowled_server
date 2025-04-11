from pydantic import BaseModel, Field
from typing import List

# Import GameState for type hinting
from gamelib.turn_based_models import GameState


class StartMatchInput(BaseModel):
    """Input data required to start a new turn-based match."""
    team1_id: str = Field(..., description="ID of the first team")
    team2_id: str = Field(..., description="ID of the second team")
    overs: int = Field(..., description="Number of overs per innings", gt=0)
    team1_squad_player_ids: List[str] = Field(
        ...,
        description="List of 11 player IDs for team 1's squad",
        min_items=11,
        max_items=11,
    )
    team2_squad_player_ids: List[str] = Field(
        ...,
        description="List of 11 player IDs for team 2's squad",
        min_items=11,
        max_items=11,
    )

# --- Other API input/output models will go here ---

class SelectOpenersInput(BaseModel):
    """Input data required to select the opening batsmen."""
    batsman_on_strike_id: str = Field(
        ..., description="ID of the batsman taking the first strike"
    )
    batsman_off_strike_id: str = Field(
        ..., description="ID of the batsman at the non-striker's end"
    )


class SelectBowlerInput(BaseModel):
    """Input data required to select the bowler for the next over."""
    bowler_id: str = Field(
        ..., description="ID of the player selected to bowl the over"
    )


class SelectBatsmanInput(BaseModel):
    """Input data required to select the next batsman after a wicket."""
    next_batsman_id: str = Field(
        ..., description="ID of the player coming in to bat"
    )


class BowlResultOutput(BaseModel):
    """Output returned after simulating a ball."""
    ball_outcome: str = Field(
        ...,
        description="The outcome of the simulated ball (e.g., 'dot', 'wicket', 'four')",
    )
    updated_game_state: GameState = Field(
        ..., description="The game state after the ball was bowled"
    )
