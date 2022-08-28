import numpy as np
import math


class GameEngine:
    def __init__(self, id, team1, team2, first_batting):
        print("--------------------Initiating Game-------------------")
        self.game_id = id
        team1["player_scores"] = []
        team2["player_scores"] = []

        self.game_results = {
            "winner": None,
            "innings1": {"team_id": None, "runs": 0, "wickets": 0},
            "innings2": {"team_id": None, "runs": 0, "wickets": 0},
        }

        self.__current_batting = None
        self.__innings_number = 0

        if first_batting == team1["team_id"]:
            self.__batting_team = team1
            self.__bowling_team = team2
        else:
            self.__batting_team = team2
            self.__bowling_team = team1

        self.__delivery_outcomes = ["0", "1", "2", "3", "4", "6", "W", "Wd"]
        self.__striker = None
        self.__non_striker = None
        self.__batsman_ratings_prob = [
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

        self.__bowler_ratings_prob = [
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

        # for i in range(10):
        #     if sum(self.__batsman_ratings_prob[i]) != 1.0 or sum(self.__bowler_ratings_prob[i]) != 1.0:
        #         print(i, sum(self.__batsman_ratings_prob[i]), sum(self.__bowler_ratings_prob[i]))

        self.start_inings()

        if self.__innings_number == 2:
            print("\n\n\n###################### GAME OVER ###########################\n")
            if self.game_results["innings1"]["runs"] > self.game_results["innings2"]["runs"]:
                print("\n\nTeam {} Rocks!!!".format(self.game_results["innings1"]["batting_team_name"]))
                print("\nTeam {} GEGE!!!".format(self.game_results["innings2"]["batting_team_name"]))
                self.game_results["winner"] = self.game_results["innings1"]["batting_team_name"]
            else:
                print("\n\nTeam {} Rocks!!!".format(self.game_results["innings2"]["batting_team_name"]))
                print("\nTeam {} GEGE!!!".format(self.game_results["innings1"]["batting_team_name"]))
                self.game_results["winner"] = self.game_results["innings2"]["batting_team_name"]

        print(self.game_results)

    def start_inings(self):
        self.__total_overs = 20
        self.__current_over = 0
        self.__current_ball = 0
        self.__current_wicket = 0
        self.__current_runs = 0

        self.__current_innings = {
            "runs": 0,
            "wickets": 0,
            "current_over": 0,
            "current_ball": 0,
            "player_scores": [],
            "team_id": None,
            "team_name": None,
        }
        self.__current_scores = {"runs": [], "balls": []}
        self.__innings_number += 1
        self.__striker = self.__batting_team["batting_lineup"][0]
        self.__non_striker = self.__batting_team["batting_lineup"][1]
        self.__striker["runs"] = 0
        self.__striker["balls_faced"] = 0
        self.__non_striker["runs"] = 0
        self.__non_striker["balls_faced"] = 0
        self.__current_innings["team_id"] = self.__batting_team["team_id"]
        self.__current_innings["team_name"] = self.__batting_team["team_name"]

        # Bowler index in bowling lineup
        self.__current_bowler = self.__bowling_team["bowling_lineup"][0]
        self.__bowlers_count = len(self.__bowling_team["bowling_lineup"])

        while self.__current_over <= self.__total_overs and self.__current_wicket < 10:
            self.__current_ball = 0
            self.play_over()
            if self.__innings_number == 2:
                if self.__current_runs > self.game_results["innings1"]["runs"]:
                    break
            if self.__current_wicket == 10:
                break

        if self.__striker["balls_faced"] == 0:
            self.__striker["strike_rate"] = 0
        else:
            self.__striker["strike_rate"] = self.__striker["runs"] * 100 / self.__striker["balls_faced"]

        if self.__non_striker["balls_faced"] == 0:
            self.__non_striker["strike_rate"] = 0
        else:
            self.__striker["strike_rate"] = self.__non_striker["runs"] * 100 / self.__non_striker["balls_faced"]

        self.__current_innings["player_scores"].append(self.__striker)
        self.__current_innings["player_scores"].append(self.__non_striker)

        if self.__innings_number == 1:
            self.game_results["innings1"]["player_scores"] = self.__current_innings["player_scores"]
            self.game_results["innings1"]["batting_team_name"] = self.__current_innings["team_name"]

            # self.game_results['innings1']['batting_team'] = self.__batting_team
            # self.game_results['innings1']['bowling_team'] = self.__bowling_team
            self.game_results["innings1"]["runs"] = self.__current_runs
            self.game_results["innings1"]["wickets"] = self.__current_wicket
            self.game_results["innings1"]["overs"] = self.__current_over
            self.game_results["innings1"]["balls"] = self.__current_ball

        elif self.__innings_number == 2:
            self.game_results["innings2"]["player_scores"] = self.__current_innings["player_scores"]
            self.game_results["innings2"]["batting_team_name"] = self.__current_innings["team_name"]
            # self.game_results['innings2']['batting_team'] = self.__batting_team
            # self.game_results['innings2']['bowling_team'] = self.__bowling_team
            self.game_results["innings2"]["runs"] = self.__current_runs
            self.game_results["innings2"]["wickets"] = self.__current_wicket
            self.game_results["innings2"]["overs"] = self.__current_over
            self.game_results["innings2"]["balls"] = self.__current_ball

        if self.__innings_number < 2:
            self.__batting_team, self.__bowling_team = self.__bowling_team, self.__batting_team
            self.start_inings()

            # Check draw

    def play_over(self):

        while self.__current_ball <= 5 and self.__current_wicket < 10:

            self.play_ball()
            if self.__innings_number == 2:
                if self.__current_runs > self.game_results["innings1"]["runs"]:
                    break
            if self.__current_wicket >= 10:
                break

        self.__current_over += 1
        self.__current_bowler = self.__bowling_team["bowling_lineup"][self.__current_over % self.__bowlers_count]
        print("\nCurrent score:")
        print(
            "Team {} {}-{} ({}.{})".format(
                self.__batting_team["team_name"],
                self.__current_runs,
                self.__current_wicket,
                self.__current_over,
                self.__current_ball,
            )
        )
        print(
            self.__striker["player_name"],
            self.__striker["runs"],
            self.__non_striker["player_name"],
            self.__non_striker["runs"],
        )

    def play_ball(self):
        if not "batting_prob" in self.__striker:
            batting_prob = self.__striker["batting_prob"] = self.__batsman_ratings_prob[
                self.__striker["batting_rating"] - 1
            ]
        else:
            batting_prob = self.__striker["batting_prob"]

        if not "bowling_prob" in self.__current_bowler:
            bowling_prob = self.__current_bowler["bowling_prob"] = self.__bowler_ratings_prob[
                self.__current_bowler["bowling_rating"] - 1
            ]
        else:
            bowling_prob = self.__current_bowler["bowling_prob"]

        if len(batting_prob) == 7:
            batting_prob.append(batting_prob[-1])
        else:
            batting_prob[7] = bowling_prob[-1]

        # outcome_prob = [round((batting_prob[i] + bowling_prob[i])/2,3) for i in range(8)]
        # print(outcome_prob)
        outcome_prob = []
        for i in range(8):
            if i != 7:
                outcome_prob.append((((1 - bowling_prob[-1]) * batting_prob[i]) + bowling_prob[i]) / 2)
        outcome_prob.append(bowling_prob[-1])

        # try:
        outcome = np.random.choice(np.arange(0, 8), p=outcome_prob)
        # except:
        #     print(outcome_prob)

        self.__current_scores["balls"].append(self.__delivery_outcomes[outcome])
        # try:
        if outcome != 7:
            self.__striker["balls_faced"] += 1
            self.__current_ball += 1

        if outcome == 7:
            self.__current_scores["runs"].append(1)
            self.__current_runs += 1

        elif outcome == 6:
            self.__striker["out"] = True
            if self.__striker["balls_faced"] == 0:
                self.__striker["strike_rate"] = 0
            else:
                self.__striker["strike_rate"] = self.__striker["runs"] * 100 / self.__striker["balls_faced"]

            # self.__striker['wicket_by'] = self.__current_bowler
            self.__current_innings["player_scores"].append(self.__striker)
            self.__current_wicket += 1
            if self.__current_wicket < 10:
                self.__striker = self.__batting_team["batting_lineup"][self.__current_wicket + 1]
                self.__striker["runs"] = 0
                self.__striker["balls_faced"] = 0

            self.__current_scores["runs"].append(0)
        elif outcome == 5:
            self.__current_runs += 6
            self.__striker["runs"] += 6
            self.__current_scores["runs"].append(6)
        elif outcome == 4:
            self.__current_runs += 4
            self.__striker["runs"] += 4
            self.__current_scores["runs"].append(4)
        elif outcome == 3:
            self.__current_runs += 3
            self.__striker["runs"] += 3
            self.__current_scores["runs"].append(3)
            self.__striker, self.__non_striker = self.__non_striker, self.__striker
        elif outcome == 2:
            self.__current_runs += 2
            self.__striker["runs"] += 2
            self.__current_scores["runs"].append(2)

        elif outcome == 1:
            self.__current_runs += 1
            self.__striker["runs"] += 1
            self.__current_scores["runs"].append(1)
            self.__striker, self.__non_striker = self.__non_striker, self.__striker

        else:
            self.__current_scores["runs"].append(0)

        # print('outcome',outcome, self.__striker['player_name'], self.__non_striker['player_name'])
        # except Exception as e:
        #     print(self.__current_innings, str(e))
        #     print(outcome_prob)

        print(
            "{}.{} \t {} \t {}(Bat) \t {} (Bowl) \t {}-{}".format(
                self.__current_over,
                self.__current_ball,
                self.__delivery_outcomes[outcome],
                self.__striker["player_name"],
                self.__current_bowler["player_name"],
                self.__current_runs,
                self.__current_wicket,
            )
        )


# team1 = {
#     'team_id': 'a',
#     'team_name': 'RCB',
#     'batting_lineup': [
#         {
#             "player_name":"Kohli",
#             "batting_rating": 1,
#             "bowling_rating": 2,
#             "team_name":"RCB"
#         },
#         {
#             "player_name":"Raina",
#             "batting_rating": 1,
#             "bowling_rating": 1,
#             "team_name":"RCB"
#         },
#         {
#             "player_name":"Rahul",
#             "batting_rating": 2,
#             "bowling_rating": 2,
#             "team_name":"RCB"
#         }
#     ],
#     'bowling_lineup': [
#         {
#             "player_name":"Kohli",
#             "batting_rating": 1,
#             "bowling_rating": 2,
#             "team_name":"RCB"
#         },
#         {
#             "player_name":"Raina",
#             "batting_rating": 1,
#             "bowling_rating": 1,
#             "team_name":"RCB"
#         },
#         {
#             "player_name":"Rahul",
#             "batting_rating": 2,
#             "bowling_rating": 2,
#             "team_name":"RCB"
#         }
#     ],
# }

# team2 = {
#     'team_id': 'b',
#     "team_name":"CSK",
#  'batting_lineup': [
#         {
#             "player_name":"Dhoni",
#             "batting_rating": 1,
#             "bowling_rating": 1,
#             "team_name":"CSK"
#         },
#         {
#             "player_name":"Dhawan",
#             "batting_rating": 1,
#             "bowling_rating": 2,
#             "team_name":"CSK"
#         },
#         {
#             "player_name":"Rahane",
#             "batting_rating": 2,
#             "bowling_rating": 1,
#             "team_name":"CSK"
#         }
#     ],
#     'bowling_lineup': [
#         {
#             "player_name":"Dhoni",
#             "batting_rating": 1,
#             "bowling_rating": 1,
#             "team_name":"CSK"
#         },
#         {
#             "player_name":"Dhawan",
#             "batting_rating": 1,
#             "bowling_rating": 2,
#             "team_name":"CSK"
#         },
#         {
#             "player_name":"Rahane",
#             "batting_rating": 2,
#             "bowling_rating": 1,
#             "team_name":"CSK"
#         }
#     ]
# }

# gg = GameEngine('id', team1, team2, team1['team_id'])
