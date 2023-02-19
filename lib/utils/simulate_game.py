import json

import numpy as np

DELIVERY_OUTCOMES = ["0", "1", "2", "3", "4", "6", "W", "Wd"]
DELIVERY_OUTCOME_LABELS = {
    "0": "Dot",
    "1": "Single",
    "2": "Double",
    "3": "Triple",
    "4": "Four",
    "6": "Six",
    "W": "Wicket",
    "Wd": "Wide",
}

BATSMAN_DISTRIBUTION = [
    [0.35, 0.175, 0.1, 0.075, 0.05, 0.05, 0.2],
    [0.325, 0.2, 0.1, 0.075, 0.05, 0.05, 0.2],
    [0.3, 0.2, 0.125, 0.075, 0.075, 0.05, 0.175],
    [0.25, 0.2, 0.15, 0.075, 0.1, 0.075, 0.15],
    [0.25, 0.2, 0.175, 0.075, 0.1, 0.05, 0.15],
    [0.2, 0.2, 0.15, 0.075, 0.15, 0.1, 0.125],
    [0.175, 0.2, 0.125, 0.075, 0.225, 0.1, 0.1],
    [0.15, 0.2, 0.125, 0.075, 0.25, 0.125, 0.075],
    [0.1, 0.2, 0.125, 0.075, 0.25, 0.175, 0.075],
    [0.05, 0.225, 0.125, 0.075, 0.3, 0.175, 0.05],
]

BOWLER_DISTRIBUTION = [
    [0.05, 0.0725, 0.1225, 0.125, 0.3, 0.23, 0.025, 0.075],
    [0.05, 0.075, 0.15, 0.125, 0.3, 0.2, 0.025, 0.075],
    [0.05, 0.075, 0.15, 0.15, 0.275, 0.175, 0.05, 0.075],
    [0.075, 0.1, 0.15, 0.1, 0.25, 0.175, 0.075, 0.075],
    [0.1, 0.075, 0.15, 0.1, 0.275, 0.15, 0.075, 0.075],
    [0.15, 0.1, 0.15, 0.075, 0.225, 0.15, 0.075, 0.075],
    [0.2, 0.1, 0.125, 0.075, 0.2, 0.125, 0.1, 0.075],
    [0.2, 0.1, 0.125, 0.1, 0.15, 0.125, 0.125, 0.075],
    [0.25, 0.1, 0.125, 0.1, 0.125, 0.075, 0.15, 0.075],
    [0.25, 0.15, 0.125, 0.075, 0.1, 0.05, 0.175, 0.075],
]

TOTAL_OVERS = 20


def simulate_game(team1, team2, bowling_team1=None, bowling_team2=None):
    """
    Given 2 teams, simulate a T20 cricket game
    """
    match_commentary = []

    # Innings 1
    # Team 1 batting, Team 2 bowling
    for player in team1:
        player["balls_faced"] = 0
        player["runs"] = 0
        player["out"] = False

    bowling_lineup = []
    for player in team2:
        if player["player_type"] in ("bowler", "all-rounder"):
            bowling_lineup.append(player)

    if bowling_team2:
        bowling_lineup = bowling_team2

    total_bowlers = len(bowling_lineup)

    batting_team = team1
    bowling_team = bowling_lineup

    striker_index = 0
    non_striker_index = 1
    bowler_index = 0

    current_wickets = 0
    current_score = 0
    current_ball = 1

    innings_score = {}

    # play game till 120 balls or 10 wickets
    while current_ball < 121 and current_wickets < 10:
        current_over = current_ball // 6
        batsman_out = False
        over_ball = current_ball % 6

        # bowler and batsman profiles
        striker = dict(batting_team[striker_index])
        bowler = dict(bowling_lineup[bowler_index])

        # Fetch batsman and bower probability based on rating out of 10
        bowler_rating = bowler["bowling_rating"] - 1
        p_bowler = BOWLER_DISTRIBUTION[bowler_rating]

        batsman_rating = striker["batting_rating"] - 1
        p_batsman = BATSMAN_DISTRIBUTION[batsman_rating]
        p_batsman.append(p_batsman[-1])

        striker = {
            "player_name": striker["player_name"],
            "player_id": striker["player_id"],
            "balls_faced": striker["balls_faced"],
            "runs": striker["runs"],
            "out": striker["out"],
        }
        bowler = {
            "player_name": bowler["player_name"],
            "player_id": bowler["player_id"],
        }

        # generate probability of current outcome
        #   based on batsman and bowler skills
        outcome_probabilities = []
        for i in range(8):
            if i != 7:
                p_out = p_bowler[-1]
                p_outcome = (((1 - p_out) * p_batsman[i]) + p_bowler[i]) / 2
                outcome_probabilities.append(p_outcome)

        # add probability of getting out
        outcome_probabilities.append(p_bowler[-1])

        # generate outcome
        outcome_index = np.random.choice(
            np.arange(0, 8),
            p=outcome_probabilities,
        )
        outcome = DELIVERY_OUTCOMES[outcome_index]
        outcome_label = DELIVERY_OUTCOME_LABELS[outcome]

        # Update scores and wickets based on outcome

        # not wide
        if outcome_label != "Wide":
            striker["balls_faced"] += 1
            current_ball += 1

        # wide
        if outcome_label == "Wide":
            current_score += 1

        # out
        elif outcome_label == "Wicket":
            striker["out"] = True
            current_wickets += 1
            batsman_out = True

        # Six
        elif outcome_label == "Six":
            striker["runs"] += 6
            current_score += 6

        # four
        elif outcome_label == "Four":
            striker["runs"] += 4
            current_score += 4

        # triple
        elif outcome_label == "Triple":
            striker["runs"] += 3
            current_score += 3
            striker_index, non_striker_index = non_striker_index, striker_index

        # double
        elif outcome_label == "Double":
            striker["runs"] += 2
            current_score += 2

        # single
        elif outcome_label == "Single":
            striker["runs"] += 1
            current_score += 1
            striker_index, non_striker_index = non_striker_index, striker_index

        # Next batsman if out
        if batsman_out:
            striker_index += 1
            if striker_index == non_striker_index:
                striker_index += 1

        # Swap strikers at the end of the over
        if over_ball == 0:
            striker_index, non_striker_index = non_striker_index, striker_index
            print_over_ball = 6
            print_current_over = current_over - 1
            bowler_index += 1
            bowler_index = bowler_index % total_bowlers
        else:
            print_over_ball = over_ball
            print_current_over = current_over

        if print_current_over not in innings_score:
            innings_score[print_current_over] = []
        over_score = innings_score[print_current_over]
        over_score.append(outcome)

        print(f"{print_current_over}.{print_over_ball} -- {outcome_label}")
        print(f"{striker['player_name']}: {striker['runs']}")
        print(f"Team score: {current_score} / {current_wickets}")
        print()

        match_commentary.append(
            {
                "current_over": print_current_over,
                "current_ball": print_over_ball,
                "current_score": current_score,
                "current_wickets": current_wickets,
                "outcome": outcome,
                "outcome_label": outcome_label,
                "striker": striker,
                "striker_rating": batsman_rating,
                "bowler": bowler,
                "bowler_rating": bowler_rating,
                "over_score": list(over_score),
                "innings_over": False,
                "innings": "First",
            },
        )

        # End innings on all out
        if current_wickets == 10:
            break

    batting_team_data = {}
    for player in batting_team:
        batting_team_data[player["player_id"]] = player

    bowling_team_data = {}
    for player in bowling_team:
        bowling_team_data[player["player_id"]] = player

    first_innings = {
        "wickets": current_wickets,
        "score": current_score,
        "current_over": print_current_over,
        "current_ball": print_over_ball,
        "batting_team": batting_team_data,
        "bowling_team": bowling_team_data,
    }
    target_score = current_score + 1

    match_commentary[-1]["innings_over"] = True
    print("##################################################################")
    print("Score to win: ", target_score)
    print("##################################################################")

    # Innings 2
    # Team 2 batting, Team 1 bowling
    for player in team2:
        player["balls_faced"] = 0
        player["runs"] = 0
        player["out"] = False

    bowling_lineup = []
    for player in team1:
        if player["player_type"] in ("bowler", "all-rounder"):
            bowling_lineup.append(player)

    if bowling_team1:
        bowling_lineup = bowling_team1

    total_bowlers = len(bowling_lineup)
    batting_team = team2
    bowling_team = bowling_lineup

    striker_index = 0
    non_striker_index = 1
    bowler_index = 0

    current_wickets = 0
    current_score = 0
    current_ball = 1

    innings_score = {}

    # play game till 120 balls or 10 wickets
    while (
        current_ball < 121
        and current_wickets < 10
        and current_score < target_score
    ):
        current_over = current_ball // 6
        batsman_out = False
        over_ball = current_ball % 6

        # bowler and batsman profiles
        striker = batting_team[striker_index]
        bowler = bowling_lineup[bowler_index]

        # Fetch batsman and bower probability based on rating out of 10
        bowler_rating = bowler["bowling_rating"] - 1
        p_bowler = BOWLER_DISTRIBUTION[bowler_rating]

        batsman_rating = striker["batting_rating"] - 1
        p_batsman = BATSMAN_DISTRIBUTION[batsman_rating]
        p_batsman.append(p_batsman[-1])

        striker = {
            "player_name": striker["player_name"],
            "player_id": striker["player_id"],
            "balls_faced": striker["balls_faced"],
            "runs": striker["runs"],
            "out": striker["out"],
        }
        bowler = {
            "player_name": bowler["player_name"],
            "player_id": bowler["player_id"],
        }

        # generate probability of current outcome
        #   based on batsman and bowler skills
        outcome_probabilities = []
        for i in range(8):
            if i != 7:
                p_out = p_bowler[-1]
                p_outcome = (((1 - p_out) * p_batsman[i]) + p_bowler[i]) / 2
                outcome_probabilities.append(p_outcome)

        # add probability of getting out
        outcome_probabilities.append(p_bowler[-1])

        # generate outcome
        outcome_index = np.random.choice(
            np.arange(0, 8),
            p=outcome_probabilities,
        )
        outcome = DELIVERY_OUTCOMES[outcome_index]
        outcome_label = DELIVERY_OUTCOME_LABELS[outcome]

        # Update scores and wickets based on outcome

        # not wide
        if outcome_label != "Wide":
            striker["balls_faced"] += 1
            current_ball += 1

        # wide
        if outcome_label == "Wide":
            current_score += 1

        # out
        elif outcome_label == "Wicket":
            striker["out"] = True
            current_wickets += 1
            batsman_out = True

        # Six
        elif outcome_label == "Six":
            striker["runs"] += 6
            current_score += 6

        # four
        elif outcome_label == "Four":
            striker["runs"] += 4
            current_score += 4

        # triple
        elif outcome_label == "Triple":
            striker["runs"] += 3
            current_score += 3
            striker_index, non_striker_index = non_striker_index, striker_index

        # double
        elif outcome_label == "Double":
            striker["runs"] += 2
            current_score += 2

        # single
        elif outcome_label == "Single":
            striker["runs"] += 1
            current_score += 1
            striker_index, non_striker_index = non_striker_index, striker_index

        # Next batsman if out
        if batsman_out:
            striker_index += 1
            if striker_index == non_striker_index:
                striker_index += 1

        # Swap strikers at the end of the over
        if over_ball == 0:
            striker_index, non_striker_index = non_striker_index, striker_index
            bowler_index += 1
            bowler_index = bowler_index % total_bowlers
            print_over_ball = 6
            print_current_over = current_over - 1
        else:
            print_over_ball = over_ball
            print_current_over = current_over

        if print_current_over not in innings_score:
            innings_score[print_current_over] = []
        over_score = innings_score[print_current_over]
        over_score.append(outcome)

        print(f"{print_current_over}.{print_over_ball} -- {outcome_label}")
        print(f"{striker['player_name']}: {striker['runs']}")
        print(f"Team score: {current_score} / {current_wickets}")
        print()

        match_commentary.append(
            {
                "current_over": print_current_over,
                "current_ball": print_over_ball,
                "current_score": current_score,
                "current_wickets": current_wickets,
                "outcome": outcome,
                "outcome_label": outcome_label,
                "striker": striker,
                "striker_rating": batsman_rating,
                "bowler": bowler,
                "bowler_rating": bowler_rating,
                "over_score": list(over_score),
                "innings_over": False,
                "target": target_score,
                "innings": "Second",
            },
        )

        # End innings on all out
        if current_wickets == 10:
            break

    batting_team_data = {}
    for player in batting_team:
        batting_team_data[player["player_id"]] = player

    bowling_team_data = {}
    for player in bowling_team:
        bowling_team_data[player["player_id"]] = player

    second_innings = {
        "wickets": current_wickets,
        "score": current_score,
        "current_over": print_current_over,
        "current_ball": print_over_ball,
        "batting_team": batting_team_data,
        "bowling_team": bowling_team_data,
    }

    match_commentary[-1]["innings_over"] = True
    return {
        "first_innings": first_innings,
        "second_innings": second_innings,
        "match_commentary": match_commentary,
    }


if __name__ == "__main__":
    with open("team01.json", encoding="UTF-8") as f:
        t1 = json.load(f)

    with open("team02.json", encoding="UTF-8") as f:
        t2 = json.load(f)

    simulate_game(t1, t2)
