from team import Team
import json
import smogon
class GameState():
    def __init__(self, my_team, opp_team):
        self.my_team = my_team
        self.opp_team = opp_team

    def deep_copy(self):
        state = GameState(self.my_team.copy(), self.opp_team.copy())
        return state

with open("pokemon_team.txt") as f1, open("pokemon_team2.txt") as f2, open("data/poke.json") as f3:
    data = json.loads(f3.read())
    poke_dict = smogon.Smogon.convert_to_dict(data)
    my_team = Team.make_team(f1.read(), poke_dict)
    opp_team = Team.make_team(f2.read(), poke_dict)
    gamestate = GameState(my_team, opp_team)
