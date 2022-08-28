import random
import numpy as np
import csv
import math
import random


class TeamBuilder:
    def __init__(self, team_owner):
        self.__owner = team_owner
        __names_file = open("engine/player_names.csv", "r")
        # self.__reader = csv.reader(__names_file)
        self.__total_names = 14845
        self.__name_lines = __names_file.readlines()
        # Gen id
        # self.__team_id = 'id'

        # self.__team_size = 15
        # self.__batsmen_count = 5
        # self.__allrounder_count = 3
        # self.__wk_count = 2
        # self.__bowler_count = 5
        # self.__min_spin = 2
        # self.__min_pacers = 3
        # self.__min_left_hander = 1
        # self.__min_right_hander = 1

        # self.__team = {
        #     'id': self.__team_id,
        #     'wk_count': 0,
        #     'batsmen_count': 0,
        #     'bowler_count': 0,
        #     'all_rounder_count': 0,
        #     'spinner_count': 0,
        #     'pacer_count': 0,
        #     'left_hander_count': 0,
        #     'right_hander_count': 0,
        # }

        self.__batting_types = ("Left hand batsman", "Right hand batsman")
        self.__bowling_types = (
            "Right arm fast",
            "Right arm medium",
            "Left arm fast",
            "Left arm medium",
            "Off break",
            "Leg break",
            "Slow left arm orthodox",
        )
        self.__fitness_levels = ("Poor", "Decent", "Good", "Superb")
        self.__skill_levels = (
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
            "Magnificient",
            "Masterful",
            "Legendary",
            "Supreme",
            "Magical",
            "Demigod",
            "Godlike",
        )
        self.__player_forms = ("Poor", "Decent", "Good", "Excellent")
        self.__players = []

    def build_new_team(self, team_name):
        print("Building new team")
        self.__team_name = team_name
        self.__team_id = team_name

        self.__players = (
            [{"player_type": "batter"} for i in range(5)]
            + [{"player_type": "wicket-keeper"} for i in range(2)]
            + [{"player_type": "allrounder"} for i in range(3)]
            + [{"player_type": "bowler"} for i in range(5)]
        )

        for i, player in enumerate(self.__players):
            self.__players[i] = self.get_new_player(player)

        return {"players": self.__players}

    def get_new_player(self, player):
        player_type = player["player_type"]
        n = random.randint(2, self.__total_names)
        # print(n)
        # name_line = next((x for i, x in enumerate(self.__reader) if i == n), None)
        # print(name_line)
        try:
            name_arr = self.__name_lines[n].split(",")[0].split(" ")

            if len(name_arr) >= 2:
                name = " ".join([name_arr[0], name_arr[1]])
            else:
                name = "".join(name_arr)
        except Exception:
            name = "Bot"

        player["player_name"] = name.title()
        player["country"] = "India"
        max_dob_ts = 1540660212998
        min_dob_ts = 1492276332458
        player["dob"] = random.randint(min_dob_ts, max_dob_ts)
        # player['experience']

        index = random.randint(1, 9)
        player["fielding"] = self.__skill_levels[index]

        index = np.random.choice(np.arange(0, 4), p=[0.1, 0.4, 0.4, 0.1])
        player["form"] = self.__player_forms[index]

        index = np.random.choice(np.arange(0, 4), p=[0.1, 0.4, 0.35, 0.15])
        player["fitness"] = self.__fitness_levels[index]

        index = np.random.choice(np.arange(0, 2), p=[0.7, 0.3])
        player["batting_type"] = self.__batting_types[index]

        if player_type == "batter":
            index = random.randint(4, 9)
            player["batting_seam"] = self.__skill_levels[index]
            index = random.randint(4, 9)
            player["batting_spin"] = self.__skill_levels[index]

        if player_type == "wicket-keeper":
            index = random.randint(4, 9)
            player["wicket_keeping"] = self.__skill_levels[index]
            index = random.randint(0, 8)
            player["batting_seam"] = self.__skill_levels[index]
            index = random.randint(4, 8)
            player["batting_spin"] = self.__skill_levels[index]
            index = random.randint(4, 8)

        if player_type == "bowler":
            index = random.randint(4, 9)
            player["bowling_main"] = self.__skill_levels[index]
            index = random.randint(4, 9)
            player["bowling_variation"] = self.__skill_levels[index]
            index = np.random.choice(np.arange(0, 7), p=[0.15, 0.125, 0.15, 0.125, 0.15, 0.15, 0.15])
            player["bowling_type"] = self.__bowling_types[index]
            index = random.randint(0, 4)
            player["batting_seam"] = self.__skill_levels[index]
            index = random.randint(0, 4)
            player["batting_spin"] = self.__skill_levels[index]

        if player_type == "allrounder":
            index = random.randint(0, 4)
            player["wicket_keeping"] = self.__skill_levels[index]
            index = random.randint(4, 8)
            player["batting_seam"] = self.__skill_levels[index]
            index = random.randint(4, 8)
            player["batting_spin"] = self.__skill_levels[index]
            index = random.randint(4, 8)
            player["bowling_main"] = self.__skill_levels[index]
            index = random.randint(4, 8)
            player["bowling_variation"] = self.__skill_levels[index]
            index = np.random.choice(np.arange(0, 7), p=[0.075, 0.125, 0.075, 0.125, 0.2, 0.2, 0.2])
            player["bowling_type"] = self.__bowling_types[index]

        if player_type not in ("bowler", "allrounder"):
            index = random.randint(0, 6)
            player["bowling_type"] = self.__bowling_types[index]
            index = random.randint(0, 3)
            player["bowling_main"] = self.__skill_levels[index]
            index = random.randint(0, 3)
            player["bowling_variation"] = self.__skill_levels[index]

        if player_type != "wicket-keeper":
            index = random.randint(0, 5)
            player["wicket_keeping"] = self.__skill_levels[index]

        player["batting_rating"] = math.ceil(
            (self.__skill_levels.index(player["batting_seam"]) + self.__skill_levels.index(player["batting_spin"])) / 2
            + 1
        )
        player["bowling_rating"] = math.ceil(
            (self.__skill_levels.index(player["bowling_main"]) + self.__skill_levels.index(player["bowling_variation"]))
            / 2
            + 1
        )
        return player


def get_batting_bowling_lineup(team):
    playing_eleven = (
        random.sample(team["players"][0:5], 4)
        + random.sample(team["players"][5:7], 1)
        + random.sample(team["players"][7:10], 2)
        + random.sample(team["players"][10:15], 4)
    )
    batting_lineup = playing_eleven
    bowling_lineup = [player for player in playing_eleven if player["player_type"] in ("bowler", "allrounder")]

    return batting_lineup, bowling_lineup
