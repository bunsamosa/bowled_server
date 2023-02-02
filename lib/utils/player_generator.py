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
FITNESS_LEVELS = ("Poor", "Decent", "Good", "Superb")
SKILL_LEVELS = (
    "Non-existent",
    "Horrible",
    "Hopeless",
    "Useless",
    "Mediocre",
    "Average",
    "Reliable",
    "Accomplished",
    "Remarkable",
    "Brilliant",
    "Exemplary",
    "Prodigious",
    "Fantastic",
    "Magnificent",
    "Masterful",
    "Legendary",
    "Supreme",
    "Magical",
    "Demigod",
    "Titan",
)

PLAYER_FORMS = ("Poor", "Decent", "Good", "Excellent")

SKILL_COLORS = {
    "1": {"name": "Non-existent", "color": "#D3D0CB"},
    "2": {"name": "Horrible", "color": "#D3D0CB"},
    "3": {"name": "Hopeless", "color": "#D3D0CB"},
    "4": {"name": "Useless", "color": "#D3D0CB"},
    "5": {"name": "Mediocre", "color": "#FFA500"},
    "6": {"name": "Average", "color": "#FFA500"},
    "7": {"name": "Reliable", "color": "#FFA500"},
    "8": {"name": "Accomplished", "color": "#FFA500"},
    "9": {"name": "Remarkable", "color": "#3FA34D"},
    "10": {"name": "Brilliant", "color": "#3FA34D"},
    "11": {"name": "Exemplary", "color": "#3FA34D"},
    "12": {"name": "Prodigious", "color": "#3FA34D"},
    "13": {"name": "Fantastic", "color": "#52489C"},
    "14": {"name": "Magnificent", "color": "#52489C"},
    "15": {"name": "Masterful", "color": "#52489C"},
    "16": {"name": "Legendary", "color": "#52489C"},
    "17": {"name": "Supreme", "color": "#FF0000"},
    "18": {"name": "Magical", "color": "#FF0000"},
    "19": {"name": "Demigod", "color": "#FF0000"},
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

    index = np.random.choice(np.arange(0, 4), p=[0.1, 0.4, 0.4, 0.1])
    player["form"] = PLAYER_FORMS[index]

    index = np.random.choice(np.arange(0, 4), p=[0.1, 0.4, 0.35, 0.15])
    player["fitness"] = FITNESS_LEVELS[index]

    max_dob_ts = 1540660212998
    min_dob_ts = 1492276332458
    player["dob"] = random.randint(min_dob_ts, max_dob_ts)

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
    index = np.random.choice(np.arange(0, 4), p=[0.1, 0.4, 0.4, 0.1])
    player["form"] = PLAYER_FORMS[index]

    # fitness
    index = np.random.choice(np.arange(0, 4), p=[0.1, 0.4, 0.35, 0.15])
    player["fitness"] = FITNESS_LEVELS[index]

    # batting type
    index = np.random.choice(np.arange(0, 2), p=[0.7, 0.3])
    player["batting_type"] = BATTING_TYPES[index]

    # main skills
    if player_type == "batsman":
        index = random.randint(4, 9)
        player["batting_seam"] = SKILL_LEVELS[index]
        player["batting_seam_index"] = index

        index = random.randint(4, 9)
        player["batting_spin"] = SKILL_LEVELS[index]
        player["batting_spin_index"] = index

    elif player_type == "wicket-keeper":
        index = random.randint(4, 9)
        player["wicket_keeping"] = SKILL_LEVELS[index]
        player["wicket_keeping_index"] = index

        index = random.randint(0, 8)
        player["batting_seam"] = SKILL_LEVELS[index]
        player["batting_seam_index"] = index

        index = random.randint(4, 8)
        player["batting_spin"] = SKILL_LEVELS[index]
        player["batting_spin_index"] = index

    elif player_type == "bowler":
        index = random.randint(4, 9)
        player["bowling_main"] = SKILL_LEVELS[index]
        player["bowling_main_index"] = index

        index = random.randint(4, 9)
        player["bowling_variation"] = SKILL_LEVELS[index]
        player["bowling_variation_index"] = index

        index = np.random.choice(
            np.arange(0, 7),
            p=[0.15, 0.125, 0.15, 0.125, 0.15, 0.15, 0.15],
        )
        player["bowling_type"] = BOWLING_TYPES[index]

        index = random.randint(0, 4)
        player["batting_seam"] = SKILL_LEVELS[index]
        player["batting_seam_index"] = index

        index = random.randint(0, 4)
        player["batting_spin"] = SKILL_LEVELS[index]
        player["batting_spin_index"] = index

    elif player_type == "all-rounder":
        index = random.randint(0, 4)
        player["wicket_keeping"] = SKILL_LEVELS[index]
        player["wicket_keeping_index"] = index

        index = random.randint(4, 8)
        player["batting_seam"] = SKILL_LEVELS[index]
        player["batting_seam_index"] = index

        index = random.randint(4, 8)
        player["batting_spin"] = SKILL_LEVELS[index]
        player["batting_spin_index"] = index

        index = random.randint(4, 8)
        player["bowling_main"] = SKILL_LEVELS[index]
        player["bowling_main_index"] = index

        index = random.randint(4, 8)
        player["bowling_variation"] = SKILL_LEVELS[index]
        player["bowling_variation_index"] = index

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
        player["bowling_main_index"] = index

        index = random.randint(0, 3)
        player["bowling_variation"] = SKILL_LEVELS[index]
        player["bowling_variation_index"] = index

    if player_type != "wicket-keeper":
        index = random.randint(0, 5)
        player["wicket_keeping"] = SKILL_LEVELS[index]
        player["wicket_keeping_index"] = index

    # ratings
    player["batting_rating"] = math.ceil(
        (player["batting_seam_index"] + player["batting_spin_index"]) / 2 + 1,
    )

    player["bowling_rating"] = math.ceil(
        (player["bowling_main_index"] + player["bowling_variation_index"]) / 2
        + 1,
    )
    return player


def generate_players(names, id_gen=None):
    players = (
        [{"player_type": "batsman"} for _ in range(5)]
        + [{"player_type": "wicket-keeper"} for _ in range(2)]
        + [{"player_type": "all-rounder"} for _ in range(3)]
        + [{"player_type": "bowler"} for _ in range(5)]
    )
    player_names = random.sample(names, 15)
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
    print(json.dumps(final_players))
