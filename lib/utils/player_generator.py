import json
import math
import random

import numpy as np

BATTING_TYPES = ("Left Hand Batsman", "Right Hand Batsman")

BOWLING_TYPES = (
    "Right Arm Fast",
    "Right Arm Medium",
    "Left Arm Fast",
    "Left Arm Medium",
    "Off Break",
    "Leg Break",
    "Slow Left Arm Orthodox",
)

ATTRIBUTE_LEVELS = (
    "Hopeless",
    "Poor",
    "Unreliable",
    "Decent",
    "Good",
    "Superb",
)

SKILL_LEVELS = (
    "Pathetic",
    "Horrible",
    "Useless",
    "Mediocre",
    "Average",
    "Reliable",
    "Talented",
    "Accomplished",
    "Remarkable",
    "Proficient",
    "Exemplary",
    "Fantastic",
    "Masterful",
    "Supreme",
    "Magnificent",
    "Phenomenal",
    "Legendary",
    "Demigod",
    "Magical",
    "Titan",
)

SKILL_COLORS = {
    "1": {"name": "Pathetic", "color": "#D3D0CB"},
    "2": {"name": "Horrible", "color": "#D3D0CB"},
    "3": {"name": "Useless", "color": "#D3D0CB"},
    "4": {"name": "Mediocre", "color": "#D3D0CB"},
    "5": {"name": "Average", "color": "#FFA500"},
    "6": {"name": "Reliable", "color": "#FFA500"},
    "7": {"name": "Talented", "color": "#FFA500"},
    "8": {"name": "Accomplished", "color": "#FFA500"},
    "9": {"name": "Remarkable", "color": "#3FA34D"},
    "10": {"name": "Proficient", "color": "#3FA34D"},
    "11": {"name": "Exemplary", "color": "#3FA34D"},
    "12": {"name": "Fantastic", "color": "#3FA34D"},
    "13": {"name": "Masterful", "color": "#52489C"},
    "14": {"name": "Supreme", "color": "#52489C"},
    "15": {"name": "Magnificent", "color": "#52489C"},
    "16": {"name": "Phenomenal", "color": "#52489C"},
    "17": {"name": "Legendary", "color": "#FF0000"},
    "18": {"name": "Demigod", "color": "#FF0000"},
    "19": {"name": "Magical", "color": "#FF0000"},
    "20": {"name": "Titan", "color": "#FF0000"},
}


def fill_skill_colors(player):
    """
    Fill skill names and skill colors for a player
    Also update the random traits - form and fitness
    """
    fielding_index = str(player["fielding_index"])
    player["fielding"] = SKILL_COLORS[fielding_index]["name"]
    player["fielding_color"] = SKILL_COLORS[fielding_index]["color"]

    wicket_keeping_index = str(player["wicket_keeping_index"])
    player["wicket_keeping"] = SKILL_COLORS[wicket_keeping_index]["name"]
    player["wicket_keeping_color"] = SKILL_COLORS[wicket_keeping_index][
        "color"
    ]

    batting_seam_index = str(player["batting_seam_index"])
    player["batting_seam"] = SKILL_COLORS[batting_seam_index]["name"]
    player["batting_seam_color"] = SKILL_COLORS[batting_seam_index]["color"]

    batting_spin_index = str(player["batting_spin_index"])
    player["batting_spin"] = SKILL_COLORS[batting_spin_index]["name"]
    player["batting_spin_color"] = SKILL_COLORS[batting_spin_index]["color"]

    bowling_main_index = str(player["bowling_main_index"])
    player["bowling_main"] = SKILL_COLORS[bowling_main_index]["name"]
    player["bowling_main_color"] = SKILL_COLORS[bowling_main_index]["color"]

    bowling_variation_index = str(player["bowling_variation_index"])
    player["bowling_variation"] = SKILL_COLORS[bowling_variation_index]["name"]
    player["bowling_variation_color"] = SKILL_COLORS[bowling_variation_index][
        "color"
    ]

    index = np.random.choice(
        np.arange(0, 6),
        p=[0.05, 0.15, 0.15, 0.4, 0.15, 0.1],
    )
    player["form"] = ATTRIBUTE_LEVELS[index]

    index = np.random.choice(
        np.arange(0, 6),
        p=[0.05, 0.15, 0.15, 0.4, 0.15, 0.1],
    )
    player["fitness"] = ATTRIBUTE_LEVELS[index]

    max_dob_ts = 1540660212998
    min_dob_ts = 1492276332458
    player["dob"] = random.randint(min_dob_ts, max_dob_ts)

    player["batting_rating"] = math.ceil(
        (player["batting_seam_index"] + player["batting_spin_index"]) / 4,
    )

    player["bowling_rating"] = math.ceil(
        (player["bowling_main_index"] + player["bowling_variation_index"]) / 4,
    )
    return player


def fill_player_skills(player):
    """
    Generate a new player with a set of unique skills
    """
    player_type = player["player_type"]

    max_dob_ts = 1540660212998
    min_dob_ts = 1492276332458
    player["dob"] = random.randint(min_dob_ts, max_dob_ts)

    # fielding
    index = random.randint(1, 9)
    player["fielding"] = SKILL_LEVELS[index]
    player["fielding_index"] = index

    # form
    index = np.random.choice(
        np.arange(0, 6),
        p=[0.05, 0.15, 0.15, 0.4, 0.15, 0.1],
    )
    player["form"] = ATTRIBUTE_LEVELS[index]

    # fitness
    index = np.random.choice(
        np.arange(0, 6),
        p=[0.05, 0.15, 0.15, 0.4, 0.15, 0.1],
    )
    player["fitness"] = ATTRIBUTE_LEVELS[index]

    # batting type
    index = np.random.choice(np.arange(0, 2), p=[0.65, 0.35])
    player["batting_type"] = BATTING_TYPES[index]

    # main skills
    if player_type == "batsman":
        index = random.randint(9, 19)
        player["batting_seam"] = SKILL_LEVELS[index]
        player["batting_seam_index"] = index + 1

        index = random.randint(9, 19)
        player["batting_spin"] = SKILL_LEVELS[index]
        player["batting_spin_index"] = index + 1

    elif player_type == "wicket-keeper":
        index = random.randint(9, 19)
        player["wicket_keeping"] = SKILL_LEVELS[index]
        player["wicket_keeping_index"] = index + 1

        index = random.randint(4, 14)
        player["batting_seam"] = SKILL_LEVELS[index]
        player["batting_seam_index"] = index + 1

        index = random.randint(4, 14)
        player["batting_spin"] = SKILL_LEVELS[index]
        player["batting_spin_index"] = index + 1

    elif player_type == "bowler":
        index = random.randint(9, 19)
        player["bowling_main"] = SKILL_LEVELS[index]
        player["bowling_main_index"] = index + 1

        index = random.randint(4, 14)
        player["bowling_variation"] = SKILL_LEVELS[index]
        player["bowling_variation_index"] = index + 1

        index = np.random.choice(
            np.arange(0, 7),
            p=[0.15, 0.125, 0.15, 0.125, 0.15, 0.15, 0.15],
        )
        player["bowling_type"] = BOWLING_TYPES[index]

        index = random.randint(0, 4)
        player["batting_seam"] = SKILL_LEVELS[index]
        player["batting_seam_index"] = index + 1

        index = random.randint(0, 4)
        player["batting_spin"] = SKILL_LEVELS[index]
        player["batting_spin_index"] = index + 1

    elif player_type == "all-rounder":
        index = random.randint(0, 4)
        player["wicket_keeping"] = SKILL_LEVELS[index]
        player["wicket_keeping_index"] = index + 1

        index = random.randint(4, 9)
        player["batting_seam"] = SKILL_LEVELS[index]
        player["batting_seam_index"] = index + 1

        index = random.randint(4, 9)
        player["batting_spin"] = SKILL_LEVELS[index]
        player["batting_spin_index"] = index + 1

        index = random.randint(9, 14)
        player["bowling_main"] = SKILL_LEVELS[index]
        player["bowling_main_index"] = index + 1

        index = random.randint(4, 8)
        player["bowling_variation"] = SKILL_LEVELS[index]
        player["bowling_variation_index"] = index + 1

        index = np.random.choice(
            np.arange(0, 7),
            p=[0.075, 0.125, 0.075, 0.125, 0.2, 0.2, 0.2],
        )
        player["bowling_type"] = BOWLING_TYPES[index]

    # secondary skills
    if player_type not in ("bowler", "all-rounder"):
        index = random.randint(0, 6)
        player["bowling_type"] = BOWLING_TYPES[index]

        index = random.randint(0, 3)
        player["bowling_main"] = SKILL_LEVELS[index]
        player["bowling_main_index"] = index + 1

        index = random.randint(0, 3)
        player["bowling_variation"] = SKILL_LEVELS[index]
        player["bowling_variation_index"] = index + 1

    if player_type != "wicket-keeper":
        index = random.randint(0, 5)
        player["wicket_keeping"] = SKILL_LEVELS[index]
        player["wicket_keeping_index"] = index + 1

    # ratings
    player["batting_rating"] = math.ceil(
        (player["batting_seam_index"] + player["batting_spin_index"]) / 4,
    )

    player["bowling_rating"] = math.ceil(
        (player["bowling_main_index"] + player["bowling_variation_index"]) / 4,
    )
    return player


def generate_players(names, id_gen=None):
    players = (
        [{"player_type": "batsman"} for _ in range(4)]
        + [{"player_type": "wicket-keeper"} for _ in range(1)]
        + [{"player_type": "all-rounder"} for _ in range(3)]
        + [{"player_type": "bowler"} for _ in range(3)]
    )
    player_names = random.sample(names, 11)
    final_players = {}

    for i, player in enumerate(players):
        if id_gen:
            player_id = next(id_gen)
        else:
            player_id = i

        player["player_name"] = player_names[i]
        player["player_id"] = player_id
        player = fill_player_skills(player=player)
        final_players[player_id] = player

    return final_players


if __name__ == "__main__":
    with open("final_names.json", encoding="UTF-8") as f:
        player_names = json.load(f)

    final_players = generate_players(names=player_names)
