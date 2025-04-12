import pytest
import httpx
import json
import uuid # Keep uuid import if needed elsewhere, or remove
from pathlib import Path
import asyncio # Import asyncio for sleep

# Import GameStatus for assertions
from gamelib.turn_based_models import GameStatus

# Define the base URL for the running server
BASE_URL = "http://127.0.0.1:9009"
OVERS_PER_INNINGS = 20  # Define overs for the test match
BALLS_PER_INNINGS = OVERS_PER_INNINGS * 6

# Load sample team data
# Adjust the path relative to the root where pytest is run
# If running pytest from within bowled_server dir, the path is relative to that
sample_data_path = Path("tests/sample_teams.json")
if not sample_data_path.exists():
    pytest.fail(f"Sample team data not found at {sample_data_path}", pytrace=False)

with open(sample_data_path, "r") as f:
    SAMPLE_TEAMS_DATA = json.load(f)

# Create a mapping from player_id to player_name for pretty printing
ALL_PLAYERS = SAMPLE_TEAMS_DATA["team1_players"] + SAMPLE_TEAMS_DATA["team2_players"]
PLAYER_ID_TO_NAME = {
    str(p["player_id"]): p["player_name"] for p in ALL_PLAYERS
}

# Helper function to format scorecard (optional, but keeps test cleaner)
def format_scorecard(player_id, scorecard_data):
    name = PLAYER_ID_TO_NAME.get(str(player_id), f"Player {player_id}")
    batting = scorecard_data.get("batting", {})
    bowling = scorecard_data.get("bowling", {})

    batted = (
        batting.get("balls_faced", 0) > 0 or
        batting.get("runs_scored", 0) > 0 or
        batting.get("dismissed", False)
    )
    bowled = bowling.get("balls_bowled", 0) > 0

    parts = [f"  {name}:"]
    if batted:
        runs = batting.get("runs_scored", 0)
        balls = batting.get("balls_faced", 0)
        dismissed = "" if batting.get("dismissed", False) else "*" # Corrected logic for '*' not out
        # Simplified dismissal info - could add how_out if model supports
        parts.append(f" Batting: {runs}({balls}){dismissed}")

    if bowled:
        overs = bowling.get("overs_bowled", 0.0)
        maidens = bowling.get("maidens", 0)
        runs_conceded = bowling.get("runs_conceded", 0)
        wickets = bowling.get("wickets_taken", 0)
        parts.append(
            f" Bowling: {overs:.1f}-{maidens}-{runs_conceded}-{wickets}"
        )

    # Only return a string if player batted or bowled
    return "".join(parts) if batted or bowled else None

# Helper function to simulate one innings
async def simulate_innings(
    client, match_id, innings_num, max_balls,
    batting_team_player_ids, bowling_team_player_ids
):
    """Helper to simulate balls within an innings until it concludes or max balls are bowled."""
    print(f"--- Simulating Innings {innings_num} (up to {max_balls} balls) ---")
    state_after_ball = None
    balls_bowled_count = 0
    max_attempts = max_balls + 20  # Safety break: Allow for extras

    for attempt in range(max_attempts):
        # Get current status before deciding to bowl
        get_url = f"/matches/{match_id}"
        response = await client.get(get_url)
        assert response.status_code == 200
        current_state = response.json()
        current_status = current_state.get("status")

        # Check termination conditions
        if current_status == GameStatus.INNINGS_BREAK:
            print(f"Innings {innings_num} ended naturally (INNINGS_BREAK).")
            state_after_ball = current_state
            break
        if current_status == GameStatus.COMPLETED:
            print(f"Match COMPLETED during Innings {innings_num}.")
            state_after_ball = current_state
            break

        # Handle intermediate states before bowling
        if current_status == GameStatus.REQUIRES_BATSMAN:
            print(" Wicket fell!")
            wickets_fallen = current_state.get("wickets", 0)
            next_batsman_index = wickets_fallen + 1 # Simple selection logic

            if next_batsman_index < len(batting_team_player_ids):
                next_batsman_id = batting_team_player_ids[next_batsman_index]
                print(f" Selecting next batsman: {next_batsman_id}")
                select_batsman_url = f"/matches/{match_id}/select-next-batsman"
                select_batsman_payload = {"next_batsman_id": next_batsman_id}
                response = await client.post(select_batsman_url, json=select_batsman_payload)
                assert response.status_code == 200
                current_state = response.json() # Update state
                current_status = current_state.get("status")
                assert current_status == GameStatus.READY_FOR_BALL
            else:
                print(f"Ran out of batsmen during Innings {innings_num}.")
                state_after_ball = current_state
                break  # Innings effectively over

        elif current_status == GameStatus.REQUIRES_BOWLER:
            print(" Over ended. Selecting new bowler...")
            # Cycle through bowlers at indices 7, 8, 9, 10
            num_bowlers_to_cycle = 4
            base_bowler_index = 7
            over_number = current_state.get("current_over", 0)
            bowler_list_index = (
                base_bowler_index + (over_number % num_bowlers_to_cycle)
            )

            if bowler_list_index < len(bowling_team_player_ids):
                next_bowler_id = bowling_team_player_ids[bowler_list_index]
                print(
                    f" Selecting next bowler: {next_bowler_id} "
                    f"(Index: {bowler_list_index})"
                )
                bowler_url = f"/matches/{match_id}/select-bowler"
                select_bowler_payload = {"bowler_id": next_bowler_id}
                response = await client.post(bowler_url, json=select_bowler_payload)
                assert response.status_code == 200
                current_state = response.json()  # Update state
                current_status = current_state.get("status")
                assert current_status == GameStatus.READY_FOR_BALL
            else:
                print(f"Error calculating bowler index: {bowler_list_index}, "
                      f"cannot select bowler.")
                state_after_ball = current_state
                break  # Cannot continue

        # Only proceed to bowl if ready
        if current_status == GameStatus.READY_FOR_BALL:
            bowl_url = f"/matches/{match_id}/bowl-next-ball"
            response = await client.post(bowl_url)
            assert response.status_code == 200
            bowl_data = response.json()
            outcome_str = bowl_data.get('ball_outcome')
            state_after_ball = bowl_data.get('updated_game_state', {})
            new_status = state_after_ball.get('status')

            # Check if it was a legal delivery to increment counter
            # Note: This relies on the outcome string. A more robust check
            # might involve comparing total_balls_bowled before/after.
            if outcome_str not in ["wide", "noball"]:
                 balls_bowled_count += 1

            print(f" Inn {innings_num} Attempt {attempt+1} (Legal Ball #{balls_bowled_count}): Outcome={outcome_str}, "
                  f"Score={state_after_ball.get('score')}/{state_after_ball.get('wickets')}, "
                  f"Status={new_status}")

            # Optional: Break if max legal balls bowled? (Current logic runs until status changes)
            # if balls_bowled_count >= max_balls:
            #     print(f"Max legal balls ({max_balls}) reached for Innings {innings_num}.")
            #     break
        else:
            # Should not happen if logic above is correct, but indicates an issue
            print(f"Unexpected status before bowling attempt: {current_status}. "
                  f"Stopping simulation.")
            state_after_ball = current_state  # Use state before the failed attempt
            break

    else: # This else clause executes if the loop finishes without a break
        print(f"Warning: Simulation loop reached max attempts ({max_attempts}) without innings conclusion.")
        # Get the final state one last time
        get_url = f"/matches/{match_id}"
        response = await client.get(get_url)
        if response.status_code == 200:
            state_after_ball = response.json()

    print(f"--- Innings {innings_num} simulation loop finished (Actual Legal Balls: {balls_bowled_count}) ---")
    # Return the last known state after the loop
    if state_after_ball is None:
         # If the loop never ran or failed to get state, fetch final state
        get_url = f"/matches/{match_id}"
        response = await client.get(get_url)
        if response.status_code == 200:
            state_after_ball = response.json()
        else:
            # Fallback or raise error
            print("Error: Could not retrieve final state after loop.")
            state_after_ball = {}

    return state_after_ball


@pytest.mark.asyncio
async def test_full_match_simulation_flow():
    """Tests the flow of a full (short) match via API calls."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # --- 1. Start Match ---
        team1_player_ids = [str(p["player_id"]) for p in SAMPLE_TEAMS_DATA["team1_players"]]
        team2_player_ids = [str(p["player_id"]) for p in SAMPLE_TEAMS_DATA["team2_players"]]

        start_match_payload = {
            "team1_id": SAMPLE_TEAMS_DATA["team1_id"],
            "team2_id": SAMPLE_TEAMS_DATA["team2_id"],
            "overs": OVERS_PER_INNINGS, # Pass the defined overs
            "team1_squad_player_ids": team1_player_ids,
            "team2_squad_player_ids": team2_player_ids,
        }
        response = await client.post("/matches", json=start_match_payload)
        assert response.status_code == 201
        start_data = response.json()
        match_id = start_data.get("match_id")
        assert match_id is not None
        assert start_data.get("status") == GameStatus.REQUIRES_OPENERS
        print(f"Match started: {match_id}")

        # Initialize potential variables to avoid linter warning
        batting_team_player_ids_inn1 = []
        bowling_team_player_ids_inn1 = []
        batting_team_player_ids_inn2 = []
        bowling_team_player_ids_inn2 = []

        batting_team_id_inn1 = start_data.get("batting_team_id")
        bowling_team_id_inn1 = start_data.get("bowling_team_id")
        print(f"Innings 1: Batting={batting_team_id_inn1}, Bowling={bowling_team_id_inn1}")

        if batting_team_id_inn1 == SAMPLE_TEAMS_DATA["team1_id"]:
            batting_team_player_ids_inn1 = team1_player_ids
            bowling_team_player_ids_inn1 = team2_player_ids
            # Set teams for Innings 2
            batting_team_player_ids_inn2 = team2_player_ids
            bowling_team_player_ids_inn2 = team1_player_ids
        elif batting_team_id_inn1 == SAMPLE_TEAMS_DATA["team2_id"]:
            batting_team_player_ids_inn1 = team2_player_ids
            bowling_team_player_ids_inn1 = team1_player_ids
            # Set teams for Innings 2
            batting_team_player_ids_inn2 = team1_player_ids
            bowling_team_player_ids_inn2 = team2_player_ids
        else:
            pytest.fail(f"Unexpected batting_team_id in response: {batting_team_id_inn1}")

        # --- 2. Innings 1 Setup ---
        # Select Openers
        select_openers_payload = {
            "batsman_on_strike_id": batting_team_player_ids_inn1[0],
            "batsman_off_strike_id": batting_team_player_ids_inn1[1]
        }
        openers_url = f"/matches/{match_id}/select-openers"
        response = await client.post(openers_url, json=select_openers_payload)
        assert response.status_code == 200
        assert response.json().get("status") == GameStatus.REQUIRES_BOWLER
        print("Innings 1: Openers selected")

        # Select First Bowler
        select_bowler_payload = {"bowler_id": bowling_team_player_ids_inn1[7]}
        bowler_url = f"/matches/{match_id}/select-bowler"
        response = await client.post(bowler_url, json=select_bowler_payload)
        assert response.status_code == 200
        assert response.json().get("status") == GameStatus.READY_FOR_BALL
        print("Innings 1: First bowler selected")

        # --- 3. Simulate Innings 1 ---
        state_after_inn1 = await simulate_innings(
            client, match_id, 1, BALLS_PER_INNINGS, # Pass max balls
            batting_team_player_ids_inn1, bowling_team_player_ids_inn1
        )
        assert state_after_inn1 is not None
        inn1_status = state_after_inn1.get("status")
        print(f"Innings 1 Final Status: {inn1_status}")

        # --- 4. Handle Innings Break / Start Innings 2 ---
        final_status = inn1_status # Initialize final_status
        if inn1_status == GameStatus.INNINGS_BREAK:
            print("Starting Innings 2 setup...")
            start_inn2_url = f"/matches/{match_id}/start-second-innings"
            response = await client.post(start_inn2_url)
            assert response.status_code == 200
            state_after_inn2_start = response.json()
            assert state_after_inn2_start.get("status") == GameStatus.REQUIRES_OPENERS
            assert state_after_inn2_start.get("current_innings") == 2
            print("Innings 2 ready for openers.")

            # Add a small delay to allow cache to potentially update
            await asyncio.sleep(0.2) # Sleep for 200ms

            # Select Openers for Innings 2
            select_openers_payload_inn2 = {
                "batsman_on_strike_id": batting_team_player_ids_inn2[0],
                "batsman_off_strike_id": batting_team_player_ids_inn2[1]
            }
            response = await client.post(openers_url, json=select_openers_payload_inn2)
            assert response.status_code == 200
            assert response.json().get("status") == GameStatus.REQUIRES_BOWLER
            print("Innings 2: Openers selected")

            # Select First Bowler for Innings 2
            select_bowler_payload_inn2 = {"bowler_id": bowling_team_player_ids_inn2[7]}
            response = await client.post(bowler_url, json=select_bowler_payload_inn2)
            assert response.status_code == 200
            assert response.json().get("status") == GameStatus.READY_FOR_BALL
            print("Innings 2: First bowler selected")

            # --- 5. Simulate Innings 2 ---
            state_after_inn2 = await simulate_innings(
                client, match_id, 2, BALLS_PER_INNINGS, # Pass max balls
                batting_team_player_ids_inn2, bowling_team_player_ids_inn2
            )
            assert state_after_inn2 is not None
            final_status = state_after_inn2.get("status")
        # else:
            # Match completed after first innings or stopped early
            # final_status remains inn1_status

        # --- 6. Final Assertions ---
        print(f"Final Match Status: {final_status}")
        assert final_status == GameStatus.COMPLETED

        # Fetch the very final state to ensure scorecards are up-to-date
        get_url = f"/matches/{match_id}"
        response = await client.get(get_url)
        assert response.status_code == 200
        final_state_for_scorecard = response.json()

        print("\n--- Final Scorecards ---")
        scorecards = final_state_for_scorecard.get("player_scorecards", {})
        if scorecards:
            # Group by team for clarity
            team1_id = SAMPLE_TEAMS_DATA["team1_id"]
            team2_id = SAMPLE_TEAMS_DATA["team2_id"]
            print(f"\nTeam {team1_id}:") # Added newline before team name
            for p_id, p_data in scorecards.items():
                # Check which team the player belongs to
                is_team1 = any(
                    str(p["player_id"]) == p_id
                    for p in SAMPLE_TEAMS_DATA["team1_players"]
                )
                if is_team1:
                    formatted_line = format_scorecard(p_id, p_data)
                    if formatted_line:
                        print(formatted_line)

            print(f"\nTeam {team2_id}:") # Added newline before team name
            for p_id, p_data in scorecards.items():
                is_team2 = any(
                    str(p["player_id"]) == p_id
                    for p in SAMPLE_TEAMS_DATA["team2_players"]
                )
                if is_team2:
                    formatted_line = format_scorecard(p_id, p_data)
                    if formatted_line:
                        print(formatted_line)
        else:
            print("  Scorecards not found in final state.")

        print("\nFull match flow test completed successfully.")

# Note: This test relies on the server running at BASE_URL.
# Outcomes vary due to randomness.
