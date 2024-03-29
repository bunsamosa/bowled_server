import math

import numpy as np

from lib.core.server_context import Context


async def fill_skill_attribute_labels(
    player,
    context: Context,
) -> dict:
    """
    This function fills skill and attribute labels for a player
    :param player: player data - postgres row or dictionary
    :param context: server context
    :return: player data with skill and attribute labels
    """
    # fetch skill and attribute labels
    skill_labels = context.cache_store.get_dictionary("skill_labels")
    attribute_labels = context.cache_store.get_dictionary("attribute_labels")

    filled_player_data = dict(player)

    # Fielding
    fielding_index = int(filled_player_data.pop("fielding_index"))
    filled_player_data["fielding_index"] = fielding_index
    filled_player_data["fielding"] = skill_labels[fielding_index]["label"]
    filled_player_data["fielding_color"] = skill_labels[fielding_index][
        "color"
    ]

    # Wicket keeping
    wicket_keeping_index = int(filled_player_data.pop("wicket_keeping_index"))
    filled_player_data["wicket_keeping_index"] = wicket_keeping_index
    filled_player_data["wicket_keeping"] = skill_labels[wicket_keeping_index][
        "label"
    ]
    filled_player_data["wicket_keeping_color"] = skill_labels[
        wicket_keeping_index
    ]["color"]

    # Batting seam
    batting_seam_index = int(filled_player_data.pop("batting_seam_index"))
    filled_player_data["batting_seam_index"] = batting_seam_index
    filled_player_data["batting_seam"] = skill_labels[batting_seam_index][
        "label"
    ]
    filled_player_data["batting_seam_color"] = skill_labels[
        batting_seam_index
    ]["color"]

    # Batting spin
    batting_spin_index = int(filled_player_data.pop("batting_spin_index"))
    filled_player_data["batting_spin_index"] = batting_spin_index
    filled_player_data["batting_spin"] = skill_labels[batting_spin_index][
        "label"
    ]
    filled_player_data["batting_spin_color"] = skill_labels[
        batting_spin_index
    ]["color"]

    # Bowling main
    bowling_main_index = int(filled_player_data.pop("bowling_main_index"))
    filled_player_data["bowling_main_index"] = bowling_main_index
    filled_player_data["bowling_main"] = skill_labels[bowling_main_index][
        "label"
    ]
    filled_player_data["bowling_main_color"] = skill_labels[
        bowling_main_index
    ]["color"]

    # Bowling variation
    bowling_variation_index = int(
        filled_player_data.pop("bowling_variation_index"),
    )
    filled_player_data["bowling_variation_index"] = bowling_variation_index
    filled_player_data["bowling_variation"] = skill_labels[
        bowling_variation_index
    ]["label"]
    filled_player_data["bowling_variation_color"] = skill_labels[
        bowling_variation_index
    ]["color"]

    # form
    form_index = int(
        np.random.choice(
            np.arange(1, 7),
            p=[0.05, 0.15, 0.15, 0.4, 0.15, 0.1],
        ),
    )
    filled_player_data["form_index"] = form_index
    filled_player_data["form"] = attribute_labels[form_index]["label"]

    # Fitness
    fitness_index = int(
        np.random.choice(
            np.arange(1, 7),
            p=[0.05, 0.15, 0.15, 0.4, 0.15, 0.1],
        ),
    )
    filled_player_data["fitness_index"] = fitness_index
    filled_player_data["fitness"] = attribute_labels[fitness_index]["label"]

    # Calculate batting rating out of 10
    # TODO Consider fitness and form parameters
    batting_rating = math.ceil((batting_seam_index + batting_spin_index) / 4)
    filled_player_data["batting_rating"] = batting_rating

    # Calculate bowling rating out of 10
    # TODO Consider fitness and form parameters
    bowling_rating = math.ceil(
        (bowling_main_index + bowling_variation_index) / 4,
    )
    filled_player_data["bowling_rating"] = bowling_rating

    return filled_player_data
