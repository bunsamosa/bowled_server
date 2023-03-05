import random
from typing import Dict
from typing import List

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


async def generate_skill_index(player: Dict) -> Dict:
    """
    This function generates skill index for a player
    :param player: player dictionary
    :return: player dictionary with skill indices
    """
    player_type = player["player_type"]
    filled_player = dict(player)

    max_dob_ts = 1540660212998
    min_dob_ts = 1492276332458
    filled_player["dob"] = random.randint(min_dob_ts, max_dob_ts)

    # fielding
    filled_player["fielding_index"] = random.randint(1, 9)

    # form
    filled_player["form_index"] = np.random.choice(
        np.arange(0, 6),
        p=[0.05, 0.15, 0.15, 0.4, 0.15, 0.1],
    )

    # fitness
    filled_player["fitness_index"] = np.random.choice(
        np.arange(0, 6),
        p=[0.05, 0.15, 0.15, 0.4, 0.15, 0.1],
    )

    # batting type
    batting_type = np.random.choice(np.arange(0, 2), p=[0.65, 0.35])
    filled_player["batting_type"] = BATTING_TYPES[batting_type]

    # bowling type
    bowling_type = np.random.choice(
        np.arange(0, 7),
        p=[0.15, 0.125, 0.15, 0.125, 0.15, 0.15, 0.15],
    )
    # secondary skills
    filled_player["bowling_type"] = BOWLING_TYPES[bowling_type]
    filled_player["wicket_keeping_index"] = random.randint(1, 3)
    filled_player["batting_seam_index"] = random.randint(1, 6)
    filled_player["batting_spin_index"] = random.randint(1, 6)
    filled_player["bowling_main_index"] = random.randint(1, 6)
    filled_player["bowling_variation_index"] = random.randint(1, 3)

    # main skills
    if player_type == "batsman":
        index = random.randint(9, 20)
        filled_player["batting_seam_index"] = index

        index = random.randint(9, 20)
        filled_player["batting_spin_index"] = index

    elif player_type == "wicket-keeper":
        filled_player["player_type"] = "batsman"
        index = random.randint(9, 20)
        filled_player["wicket_keeping_index"] = index

        index = random.randint(9, 20)
        filled_player["batting_seam_index"] = index

        index = random.randint(9, 20)
        filled_player["batting_spin_index"] = index

    elif player_type == "bowler":
        index = random.randint(9, 20)
        filled_player["bowling_main_index"] = index

        index = random.randint(9, 14)
        filled_player["bowling_variation_index"] = index

    elif player_type == "all-rounder":
        index = random.randint(9, 15)
        filled_player["batting_seam_index"] = index

        index = random.randint(9, 15)
        filled_player["batting_spin_index"] = index

        index = random.randint(9, 15)
        filled_player["bowling_main_index"] = index

        index = random.randint(4, 8)
        filled_player["bowling_variation_index"] = index
    return filled_player


async def generate_random_players(
    player_names: List,
    team_id: str,
    number_of_players: int = 11,
) -> Dict:
    """
    This function generates random players
    :param number_of_players: number of players to generate
    :param context: server context
    :return: a dictionary of players
    """
    # Generate players based on types
    # min 5 bowlers including all rounders
    # min 5 batsmen including all rounders
    # min 1 wicket keeper batsman
    # total of 11 players
    players = (
        [{"player_type": "batsman"} for _ in range(4)]
        + [{"player_type": "wicket-keeper"}]
        + [{"player_type": "all-rounder"} for _ in range(3)]
        + [{"player_type": "bowler"} for _ in range(3)]
    )

    # additional players
    while len(players) < number_of_players:
        players.append({"player_type": "batsman"})
        players.append({"player_type": "bowler"})
        players.append({"player_type": "all-rounder"})
        players.append({"player_type": "wicket-keeper"})
    players = players[:number_of_players]

    # sample player names
    player_names = random.sample(player_names, number_of_players)
    id_start = 999999999
    all_players = {}

    for i, player in enumerate(players):
        player = await generate_skill_index(player)
        player_id = str(id_start - i)
        player["player_name"] = player_names[i]
        player["player_id"] = player_id
        player["team_id"] = team_id
        all_players[player_id] = player

    return all_players
