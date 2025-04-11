from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

# TODO: Import specific player/team data models if needed
# from gamelib.player.player_data import PlayerData # Example
# from gamelib.team.team_data import TeamData     # Example

# --- Scorecard Models ---

class BallData(BaseModel):
    """Represents data for a single ball bowled in the match."""
    innings: int
    over: int  # 0-indexed over number
    ball_in_over: int  # 1-indexed ball number within the over (1-6, extras don't count)
    total_balls_bowled_innings: int  # Overall legal ball number in the innings
    batsman_on_strike_id: str
    bowler_id: str
    outcome: str  # e.g., "dot", "single", "four", "wicket", "wide", "noball"
    runs_scored: int = 0
    is_wicket: bool = False
    wicket_type: Optional[str] = None  # e.g., "bowled", "caught", "lbw" (optional detail)
    extras_type: Optional[Literal["wide", "noball", "legbye", "bye"]] = None
    extras_runs: int = 0
    score_at_ball: int  # Total score *after* this ball
    wickets_at_ball: int  # Total wickets *after* this ball

class BattingStats(BaseModel):
    """Individual batting stats."""
    runs_scored: int = 0
    balls_faced: int = 0
    fours: int = 0
    sixes: int = 0
    dismissed: bool = False
    # Optional: Add bowler_id, wicket_type when dismissed

class BowlingStats(BaseModel):
    """Individual bowling stats."""
    overs_bowled: float = 0.0  # Represent as 1.5 for 1 over and 5 balls etc.
    balls_bowled: int = 0  # Legal deliveries
    runs_conceded: int = 0
    wickets_taken: int = 0
    maidens: int = 0
    wides: int = 0
    noballs: int = 0

class PlayerScorecard(BaseModel):
    """Combined stats for a player in the match."""
    player_id: str
    batting: BattingStats = Field(default_factory=BattingStats)
    bowling: BowlingStats = Field(default_factory=BowlingStats)

class OverSummary(BaseModel):
    """Summary of events within a single over."""
    innings: int
    over_number: int # 0-indexed
    bowler_id: str
    runs_conceded: int = 0
    wickets_taken: int = 0
    balls_in_over: List[BallData] = Field(default_factory=list) # Store ball-by-ball details for the over

class GameStatus(str, Enum):
    """Represents the current status and required action for a turn-based match."""
    INITIALIZING = "initializing"
    REQUIRES_OPENERS = "requires_openers"
    REQUIRES_BOWLER = "requires_bowler"
    READY_FOR_BALL = "ready_for_ball"
    REQUIRES_BATSMAN = "requires_batsman"
    INNINGS_BREAK = "innings_break"
    COMPLETED = "completed"
    ERROR = "error"

class GameState(BaseModel):
    """Represents the complete state of a turn-based match.
    Stored in cache (Redis) between turns.
    """
    match_id: str
    status: GameStatus
    team1_id: str
    team2_id: str
    team1_squad: List[Dict]  # Using Dict as player data structure is handled elsewhere
    team2_squad: List[Dict]
    total_overs: int
    current_innings: int = 1
    batting_team_id: Optional[str] = None
    bowling_team_id: Optional[str] = None

    # Using 0-indexed overs for internal logic simplicity
    current_over: int = 0
    current_ball_in_over: int = 0  # Ball number within the current over (1-6)
    # Overall balls bowled in the current innings
    total_balls_bowled: int = 0

    score: int = 0
    wickets: int = 0
    target: Optional[int] = None  # For 2nd innings

    batsman_on_strike_id: Optional[str] = None
    batsman_off_strike_id: Optional[str] = None
    current_bowler_id: Optional[str] = None
    previous_over_bowler_id: Optional[str] = None # Added to track previous bowler

    # Lists of player IDs available for selection
    available_batsman_ids: List[str] = Field(default_factory=list)
    available_bowler_ids: List[str] = Field(default_factory=list)

    # Tracking player status
    dismissed_batsman_ids: List[str] = Field(default_factory=list)
    bowlers_used_this_innings: List[str] = Field(default_factory=list)

    # Detailed Scorecards
    player_scorecards: Dict[str, PlayerScorecard] = Field(default_factory=dict)
    over_summaries: List[OverSummary] = Field(default_factory=list)
    # Optional: ball_by_ball list if needed for full commentary replay outside of overs
    # ball_by_ball_log: List[BallData] = Field(default_factory=list)

    last_ball_outcome: Optional[str] = None  # Store outcome string
    commentary: Optional[str] = None  # Optional: Add simple commentary text
    # Store error messages if status is ERROR
    error_message: Optional[str] = None

    class Config:
        use_enum_values = True  # Ensures Enum values are used in serialization
