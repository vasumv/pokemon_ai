from team import Team
import json
import smogon
from simulator import Action

class GameState():
    def __init__(self, my_team, opp_team):
        self.my_team = my_team
        self.opp_team = opp_team

    def deep_copy(self):
        state = GameState(self.my_team.copy(), self.opp_team.copy())
        return state

    def to_tuple(self):
        return (self.my_team.to_tuple(), self.opp_team.to_tuple())

    def evaluate(self):
        return sum([x.health/x.final_stats['hp'] for x in self.my_team.poke_list]) - sum([x.health/x.final_stats['hp'] for x in self.opp_team.poke_list])

    def get_legal_actions(self, player):
        if player == 0:
            team = self.my_team
        else:
            team = self.opp_team

        pokemon = range(len(team.poke_list))
        valid_switches = [i for i in pokemon if team.poke_list[i].alive and i != team.primary_poke]

        moves = [Action("move",
                        move_index=i,
                        backup_switch=j, mega=True if team.primary().can_evolve() else False)
                 for i in range(len(team.primary().moveset.moves))
                 for j in valid_switches]
        switches = [Action("switch", switch_index=i, backup_switch=j)
                    for i in valid_switches for j in [x for x in pokemon if x != i]]
        return moves + switches

with open("pokemon_team.txt") as f1, open("pokemon_team2.txt") as f2, open("data/poke.json") as f3:
    data = json.loads(f3.read())
    poke_dict = smogon.Smogon.convert_to_dict(data)
    my_team = Team.make_team(f1.read(), poke_dict)
    opp_team = Team.make_team(f2.read(), poke_dict)
    gamestate = GameState(my_team, opp_team)
