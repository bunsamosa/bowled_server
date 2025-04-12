import pytest

from bowled_match_engine.match_engine.ball_simulator import simulate_ball

# Define expected possible string outcomes from the simulator
POSSIBLE_OUTCOMES = {
    "dot", "single", "double", "triple", "four", "five", "six",
    "wicket", "noball", "wide"
    # Add any other potential string outcomes if known
}


@pytest.mark.asyncio
async def test_simulate_ball_basic():
    """Test the basic functionality of simulate_ball."""
    batsman = {"batting_rating": 70}
    bowler = {"bowling_rating": 65}

    outcome_str = await simulate_ball(batsman, bowler)

    # Assert outcome is a string and one of the expected types
    assert isinstance(outcome_str, str)
    assert outcome_str in POSSIBLE_OUTCOMES


@pytest.mark.parametrize(
    "batsman_rating, bowler_rating",
    [
        (80, 60),    # Good batsman, avg bowler
        (60, 80),    # Avg batsman, good bowler
        (90, 50),    # V.Good batsman, poor bowler
        (50, 90),    # Poor batsman, v.good bowler
        (70, 70),    # Equal ratings
    ],
)
@pytest.mark.asyncio
async def test_simulate_ball_parametrized(
    batsman_rating, bowler_rating
):
    """Test simulate_ball with various rating combinations."""
    batsman = {"batting_rating": batsman_rating}
    bowler = {"bowling_rating": bowler_rating}
    outcome_str = await simulate_ball(batsman, bowler)

    # Assert outcome is a string and one of the expected types
    assert isinstance(outcome_str, str)
    assert outcome_str in POSSIBLE_OUTCOMES


@pytest.mark.parametrize(
    "batsman_rating, bowler_rating",
    [
        (1, 99),     # Edge case: Min batsman, Max bowler
        (99, 1),     # Edge case: Max batsman, Min bowler
        (0, 100),    # Assuming 0-100 is possible range
        (100, 0),    # Assuming 0-100 is possible range
        (1, 1),      # Edge case: Min ratings
        (100, 100),  # Edge case: Max ratings
                     # (adjust if scale is different)
    ],
)
@pytest.mark.asyncio
async def test_simulate_ball_edge_cases(batsman_rating, bowler_rating):
    """Test simulate_ball with edge case ratings."""
    batsman = {"batting_rating": batsman_rating}
    bowler = {"bowling_rating": bowler_rating}
    outcome_str = await simulate_ball(batsman, bowler)

    # Assert outcome is a string and one of the expected types
    assert isinstance(outcome_str, str)
    assert outcome_str in POSSIBLE_OUTCOMES

# Note: Testing the *probability* distribution of outcomes would require
# running the simulation many times and checking statistics, which is more
# complex. These tests primarily ensure the function handles different
# inputs gracefully and returns an expected string outcome.
