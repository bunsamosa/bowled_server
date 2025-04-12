import pytest
from unittest.mock import patch, MagicMock

# Use absolute import from project root
from gamelib.turn_based_models import (
    GameState,
    PlayerScorecard,  # Includes BattingStats, BowlingStats
    OverSummary,
    BallData,
    GameStatus,
)

# Assume we have a function (or will refactor to create one)
# that handles the game state update logic after a ball is bowled.
# For now, the test will manually apply the expected updates
# based on the logic in bowl_next_ball.py and assert the result.
# Example: update_gamestate_after_ball(game_state, ball_outcome) -> GameState

def create_initial_game_state(
    striker_id="batsman1",
    non_striker_id="batsman2",
    bowler_id="bowler1",
    batting_team="team1",
    bowling_team="team2"
) -> GameState:
    """Helper function to create a basic GameState ready for the first ball."""

    # Create initial player scorecards
    scorecards = {
        striker_id: PlayerScorecard(player_id=striker_id),
        non_striker_id: PlayerScorecard(player_id=non_striker_id),
        bowler_id: PlayerScorecard(player_id=bowler_id),
        # Add other players if needed for substitutions etc.
    }

    # Minimal squad data (only IDs needed by current game state logic)
    team1_squad = [
        {"player_id": striker_id}, {"player_id": non_striker_id}
        # Add other players if needed
    ]
    team2_squad = [
        {"player_id": bowler_id}
        # Add other players if needed
    ]

    # Initial over summary for the first over (0-indexed)
    initial_over = OverSummary(innings=1, over_number=0, bowler_id=bowler_id)

    game_state = GameState(
        match_id="test_match",
        status=GameStatus.READY_FOR_BALL, # Set to ready for ball
        team1_id=batting_team if batting_team == "team1" else bowling_team,
        team2_id=bowling_team if bowling_team == "team2" else batting_team,
        team1_squad=team1_squad,
        team2_squad=team2_squad,
        current_innings=1,
        batting_team_id=batting_team,
        bowling_team_id=bowling_team,
        current_over=0, # Over 0
        current_ball_in_over=0, # No balls bowled yet in this over
        total_balls_bowled=0, # No balls bowled yet in innings
        score=0,
        wickets=0,
        batsman_on_strike_id=striker_id,
        batsman_off_strike_id=non_striker_id,
        current_bowler_id=bowler_id,
        player_scorecards=scorecards,
        over_summaries=[initial_over], # List containing the first over summary
        # Initialize other lists/optional fields as needed
        available_batsman_ids=[striker_id, non_striker_id], # Example
        available_bowler_ids=[bowler_id], # Example
    )
    return game_state

def test_update_score_on_single():
    """Test updating GameState when a single run is scored."""
    # --- Setup ---
    striker_id = "p1"
    non_striker_id = "p2"
    bowler_id = "p10"
    game_state = create_initial_game_state(
        striker_id=striker_id, non_striker_id=non_striker_id, bowler_id=bowler_id
    )

    # Simulate the outcome of a single run
    ball_outcome = {"outcome": 1, "commentary": "Single taken.", "is_wicket": False}

    # --- Action: Mimic logic from bowl_next_ball.py (Needs refactoring based on models) ---

    # TODO: Refactor this section to align with model structure
    # Get runs, wicket status etc. from ball_outcome
    runs_scored = ball_outcome["outcome"]
    is_wicket = ball_outcome["is_wicket"]
    commentary = ball_outcome["commentary"]

    # Get current state for updates
    inning = game_state.current_innings
    over_num = game_state.current_over
    ball_num_in_over = game_state.current_ball_in_over + 1 # This is the 1st ball
    total_balls = game_state.total_balls_bowled + 1

    # 1. Update overall state
    game_state.score += runs_scored
    game_state.current_ball_in_over = ball_num_in_over
    game_state.total_balls_bowled = total_balls
    # Overs calculation TBD (happens at end of over)

    # 2. Update PlayerScorecards (Nested models)
    batsman_card = game_state.player_scorecards[striker_id]
    bowler_card = game_state.player_scorecards[bowler_id]

    batsman_card.batting.runs_scored += runs_scored
    batsman_card.batting.balls_faced += 1
    # TODO: Update batsman fours/sixes if applicable

    bowler_card.bowling.runs_conceded += runs_scored
    bowler_card.bowling.balls_bowled += 1
    # TODO: Update bowler wickets if applicable
    # TODO: Calculate bowler overs_bowled (likely using total balls bowled by them)
    # Example (crude calculation, needs proper logic):
    b_balls = bowler_card.bowling.balls_bowled
    bowler_card.bowling.overs_bowled = round(b_balls // 6 + (b_balls % 6) / 10, 1)


    # 3. Create BallData and add to OverSummary
    ball_data = BallData(
        innings=inning,
        over=over_num, # 0-indexed
        ball_in_over=ball_num_in_over, # 1-indexed
        total_balls_bowled_innings=total_balls,
        batsman_on_strike_id=striker_id,
        bowler_id=bowler_id,
        outcome=str(runs_scored), # Store outcome string representation
        runs_scored=runs_scored,
        is_wicket=is_wicket,
        score_at_ball=game_state.score, # Score *after* this ball
        wickets_at_ball=game_state.wickets # Wickets *after* this ball (0 here)
        # Extras TBD
    )

    # Find the current over summary (should be the last one in the list)
    current_over_summary = game_state.over_summaries[-1]
    assert current_over_summary.over_number == over_num # Sanity check

    current_over_summary.balls_in_over.append(ball_data)
    current_over_summary.runs_conceded += runs_scored
    # TODO: Update wickets_taken in over summary if applicable

    # TODO: Handle strike rotation (since it was a single)
    # game_state.batsman_on_strike_id, game_state.batsman_off_strike_id = \
    #     game_state.batsman_off_strike_id, game_state.batsman_on_strike_id

    # --- End: Mimic logic ---


    # --- Assertions (Need to be updated) ---
    # Overall game state
    assert game_state.score == 1
    assert game_state.wickets == 0
    assert game_state.current_ball_in_over == 1
    assert game_state.total_balls_bowled == 1
    # TODO: Assert strike rotation

    # Batsman scorecard
    assert batsman_card.batting.runs_scored == 1
    assert batsman_card.batting.balls_faced == 1

    # Bowler scorecard
    assert bowler_card.bowling.runs_conceded == 1
    assert bowler_card.bowling.balls_bowled == 1
    assert bowler_card.bowling.overs_bowled == 0.1 # Based on crude calc
    assert bowler_card.bowling.wickets_taken == 0

    # Over summary
    assert len(current_over_summary.balls_in_over) == 1
    ball_record = current_over_summary.balls_in_over[0]
    assert ball_record.outcome == "1"
    assert ball_record.runs_scored == 1
    assert ball_record.batsman_on_strike_id == striker_id
    assert ball_record.is_wicket is False
    assert ball_record.score_at_ball == 1
    assert ball_record.wickets_at_ball == 0
    assert current_over_summary.runs_conceded == 1
    assert current_over_summary.wickets_taken == 0

def test_update_score_on_dot_ball():
    """Test updating GameState when a dot ball is bowled."""
    # --- Setup ---
    striker_id = "p1"
    non_striker_id = "p2"
    bowler_id = "p10"
    game_state = create_initial_game_state(
        striker_id=striker_id, non_striker_id=non_striker_id, bowler_id=bowler_id
    )
    batsman_card = game_state.player_scorecards[striker_id]
    bowler_card = game_state.player_scorecards[bowler_id]

    # Simulate the outcome
    ball_outcome = {"outcome": 0, "commentary": "No run.", "is_wicket": False}

    # --- Action: Mimic update logic ---
    runs_scored = 0
    is_wicket = False
    inning = game_state.current_innings
    over_num = game_state.current_over
    ball_num_in_over = game_state.current_ball_in_over + 1
    total_balls = game_state.total_balls_bowled + 1

    game_state.score += runs_scored # Score remains 0
    game_state.current_ball_in_over = ball_num_in_over
    game_state.total_balls_bowled = total_balls

    batsman_card.batting.runs_scored += runs_scored
    batsman_card.batting.balls_faced += 1

    bowler_card.bowling.runs_conceded += runs_scored
    bowler_card.bowling.balls_bowled += 1
    b_balls = bowler_card.bowling.balls_bowled
    bowler_card.bowling.overs_bowled = round(b_balls // 6 + (b_balls % 6) / 10, 1)

    ball_data = BallData(
        innings=inning, over=over_num, ball_in_over=ball_num_in_over,
        total_balls_bowled_innings=total_balls, batsman_on_strike_id=striker_id,
        bowler_id=bowler_id, outcome="0", runs_scored=runs_scored,
        is_wicket=is_wicket, score_at_ball=game_state.score,
        wickets_at_ball=game_state.wickets
    )
    current_over_summary = game_state.over_summaries[-1]
    current_over_summary.balls_in_over.append(ball_data)
    current_over_summary.runs_conceded += runs_scored
    # --- End: Mimic logic ---

    # --- Assertions ---
    assert game_state.score == 0
    assert game_state.wickets == 0
    assert game_state.current_ball_in_over == 1
    assert batsman_card.batting.runs_scored == 0
    assert batsman_card.batting.balls_faced == 1
    assert bowler_card.bowling.runs_conceded == 0
    assert bowler_card.bowling.balls_bowled == 1
    assert bowler_card.bowling.overs_bowled == 0.1
    assert len(current_over_summary.balls_in_over) == 1
    assert current_over_summary.runs_conceded == 0


def test_update_score_on_four():
    """Test updating GameState when four runs are scored."""
    # --- Setup ---
    striker_id = "p1"
    game_state = create_initial_game_state(striker_id=striker_id)
    batsman_card = game_state.player_scorecards[striker_id]
    bowler_card = game_state.player_scorecards[game_state.current_bowler_id]

    # Simulate the outcome
    ball_outcome = {"outcome": 4, "commentary": "FOUR!", "is_wicket": False}

    # --- Action: Mimic update logic ---
    runs_scored = 4
    is_wicket = False
    inning = game_state.current_innings
    over_num = game_state.current_over
    ball_num_in_over = game_state.current_ball_in_over + 1
    total_balls = game_state.total_balls_bowled + 1

    game_state.score += runs_scored
    game_state.current_ball_in_over = ball_num_in_over
    game_state.total_balls_bowled = total_balls

    batsman_card.batting.runs_scored += runs_scored
    batsman_card.batting.balls_faced += 1
    batsman_card.batting.fours += 1 # Increment fours

    bowler_card.bowling.runs_conceded += runs_scored
    bowler_card.bowling.balls_bowled += 1
    b_balls = bowler_card.bowling.balls_bowled
    bowler_card.bowling.overs_bowled = round(b_balls // 6 + (b_balls % 6) / 10, 1)

    ball_data = BallData(
        innings=inning, over=over_num, ball_in_over=ball_num_in_over,
        total_balls_bowled_innings=total_balls, batsman_on_strike_id=striker_id,
        bowler_id=game_state.current_bowler_id, outcome="4", runs_scored=runs_scored,
        is_wicket=is_wicket, score_at_ball=game_state.score,
        wickets_at_ball=game_state.wickets
    )
    current_over_summary = game_state.over_summaries[-1]
    current_over_summary.balls_in_over.append(ball_data)
    current_over_summary.runs_conceded += runs_scored
    # --- End: Mimic logic ---

    # --- Assertions ---
    assert game_state.score == 4
    assert game_state.wickets == 0
    assert game_state.current_ball_in_over == 1
    assert batsman_card.batting.runs_scored == 4
    assert batsman_card.batting.balls_faced == 1
    assert batsman_card.batting.fours == 1
    assert bowler_card.bowling.runs_conceded == 4
    assert bowler_card.bowling.balls_bowled == 1
    assert bowler_card.bowling.overs_bowled == 0.1
    assert len(current_over_summary.balls_in_over) == 1
    assert current_over_summary.runs_conceded == 4


def test_update_score_on_six():
    """Test updating GameState when six runs are scored."""
    # --- Setup ---
    striker_id = "p1"
    game_state = create_initial_game_state(striker_id=striker_id)
    batsman_card = game_state.player_scorecards[striker_id]
    bowler_card = game_state.player_scorecards[game_state.current_bowler_id]

    # Simulate the outcome
    ball_outcome = {"outcome": 6, "commentary": "SIX!", "is_wicket": False}

    # --- Action: Mimic update logic ---
    runs_scored = 6
    is_wicket = False
    inning = game_state.current_innings
    over_num = game_state.current_over
    ball_num_in_over = game_state.current_ball_in_over + 1
    total_balls = game_state.total_balls_bowled + 1

    game_state.score += runs_scored
    game_state.current_ball_in_over = ball_num_in_over
    game_state.total_balls_bowled = total_balls

    batsman_card.batting.runs_scored += runs_scored
    batsman_card.batting.balls_faced += 1
    batsman_card.batting.sixes += 1 # Increment sixes

    bowler_card.bowling.runs_conceded += runs_scored
    bowler_card.bowling.balls_bowled += 1
    b_balls = bowler_card.bowling.balls_bowled
    bowler_card.bowling.overs_bowled = round(b_balls // 6 + (b_balls % 6) / 10, 1)

    ball_data = BallData(
        innings=inning, over=over_num, ball_in_over=ball_num_in_over,
        total_balls_bowled_innings=total_balls, batsman_on_strike_id=striker_id,
        bowler_id=game_state.current_bowler_id, outcome="6", runs_scored=runs_scored,
        is_wicket=is_wicket, score_at_ball=game_state.score,
        wickets_at_ball=game_state.wickets
    )
    current_over_summary = game_state.over_summaries[-1]
    current_over_summary.balls_in_over.append(ball_data)
    current_over_summary.runs_conceded += runs_scored
    # --- End: Mimic logic ---

    # --- Assertions ---
    assert game_state.score == 6
    assert game_state.wickets == 0
    assert game_state.current_ball_in_over == 1
    assert batsman_card.batting.runs_scored == 6
    assert batsman_card.batting.balls_faced == 1
    assert batsman_card.batting.sixes == 1
    assert bowler_card.bowling.runs_conceded == 6
    assert bowler_card.bowling.balls_bowled == 1
    assert bowler_card.bowling.overs_bowled == 0.1
    assert len(current_over_summary.balls_in_over) == 1
    assert current_over_summary.runs_conceded == 6


def test_update_score_on_wicket():
    """Test updating GameState when a wicket falls (bowled)."""
    # --- Setup ---
    striker_id = "p1"
    non_striker_id = "p2"
    bowler_id = "p10"
    game_state = create_initial_game_state(
        striker_id=striker_id, non_striker_id=non_striker_id, bowler_id=bowler_id
    )
    batsman_card = game_state.player_scorecards[striker_id]
    bowler_card = game_state.player_scorecards[bowler_id]

    # Simulate the outcome
    ball_outcome = {"outcome": "W", "commentary": "Bowled him!", "is_wicket": True, "wicket_type": "bowled"}

    # --- Action: Mimic update logic ---
    runs_scored = 0 # No runs on a wicket typically
    is_wicket = True
    wicket_type = ball_outcome["wicket_type"]
    inning = game_state.current_innings
    over_num = game_state.current_over
    ball_num_in_over = game_state.current_ball_in_over + 1
    total_balls = game_state.total_balls_bowled + 1

    # 1. Update overall state
    game_state.wickets += 1 # Increment wickets
    game_state.current_ball_in_over = ball_num_in_over
    game_state.total_balls_bowled = total_balls
    game_state.status = GameStatus.REQUIRES_BATSMAN # Update status

    # 2. Update PlayerScorecards
    batsman_card.batting.balls_faced += 1
    batsman_card.batting.dismissed = True # Mark as dismissed
    # TODO: Could store how_out details (bowler_id, wicket_type) in scorecard

    bowler_card.bowling.balls_bowled += 1
    bowler_card.bowling.wickets_taken += 1 # Increment wickets
    # Runs conceded is 0 for this ball
    b_balls = bowler_card.bowling.balls_bowled
    bowler_card.bowling.overs_bowled = round(b_balls // 6 + (b_balls % 6) / 10, 1)

    # 3. Create BallData
    ball_data = BallData(
        innings=inning, over=over_num, ball_in_over=ball_num_in_over,
        total_balls_bowled_innings=total_balls, batsman_on_strike_id=striker_id,
        bowler_id=bowler_id, outcome="W", runs_scored=runs_scored,
        is_wicket=is_wicket, wicket_type=wicket_type, score_at_ball=game_state.score, # Score before wicket
        wickets_at_ball=game_state.wickets # Wickets *after* this ball
    )
    current_over_summary = game_state.over_summaries[-1]
    current_over_summary.balls_in_over.append(ball_data)
    current_over_summary.runs_conceded += runs_scored # Runs in over remains 0
    current_over_summary.wickets_taken += 1 # Increment wickets in over

    # Add dismissed batsman to list
    game_state.dismissed_batsman_ids.append(striker_id)
    # Remove from available list
    if striker_id in game_state.available_batsman_ids:
        game_state.available_batsman_ids.remove(striker_id)
    # Clear current striker
    game_state.batsman_on_strike_id = None

    # --- End: Mimic logic ---

    # --- Assertions ---
    assert game_state.score == 0
    assert game_state.wickets == 1
    assert game_state.current_ball_in_over == 1
    assert game_state.status == GameStatus.REQUIRES_BATSMAN
    assert game_state.batsman_on_strike_id is None
    assert striker_id in game_state.dismissed_batsman_ids
    assert striker_id not in game_state.available_batsman_ids

    assert batsman_card.batting.runs_scored == 0
    assert batsman_card.batting.balls_faced == 1
    assert batsman_card.batting.dismissed is True

    assert bowler_card.bowling.runs_conceded == 0
    assert bowler_card.bowling.balls_bowled == 1
    assert bowler_card.bowling.overs_bowled == 0.1
    assert bowler_card.bowling.wickets_taken == 1

    assert len(current_over_summary.balls_in_over) == 1
    assert current_over_summary.runs_conceded == 0
    assert current_over_summary.wickets_taken == 1
    ball_record = current_over_summary.balls_in_over[0]
    assert ball_record.outcome == "W"
    assert ball_record.runs_scored == 0
    assert ball_record.is_wicket is True
    assert ball_record.wicket_type == "bowled"
    assert ball_record.wickets_at_ball == 1

# TODO: Add tests for other outcomes (dot, 4, 6, wicket, extras?)
# TODO: Add tests for end-of-over logic (maiden check, bowler change, batsman swap?)
# TODO: Add tests for end-of-innings logic
# TODO: Consider refactoring scorekeeping logic from endpoint into a testable function
