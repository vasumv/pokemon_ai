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
        win_bonus = 0
        if self.is_over():
            if self.my_team.alive():
                win_bonus = 10000
            else:
                win_bonus = -10000
        my_team_health = sum([x.health/x.final_stats['hp'] for x in self.my_team.poke_list])
        opp_team_health = sum([x.health/x.final_stats['hp'] for x in self.opp_team.poke_list])
        my_team_death = len([x for x in self.my_team.poke_list if not x.alive])
        opp_team_death = len([x for x in self.opp_team.poke_list if not x.alive])
        if self.is_over():
            my_team_stages, opp_team_stages = 0, 0
        else:
            my_poke = self.my_team.primary()
            opp_poke = self.opp_team.primary()
            my_team_stages = my_poke.stages['spatk'] + my_poke.stages['patk']
            opp_team_stages = opp_poke.stages['spatk'] + opp_poke.stages['patk']
        return win_bonus + my_team_health - opp_team_health - 0.5 * my_team_death + 0.5 * opp_team_death# + 0.07 * (my_team_stages - opp_team_stages)

    def is_over(self):
        return not (self.my_team.alive() and self.opp_team.alive())

    def get_legal_actions(self, player):
        if player == 0:
            team = self.my_team
            my_poke = self.my_team.primary()
            opp_poke = self.opp_team.primary()
        else:
            team = self.opp_team
            my_poke = self.opp_team.primary()
            opp_poke = self.my_team.primary()

        if self.is_over():
            return []

        pokemon = range(len(team.poke_list))
        valid_switches = [i for i in pokemon if team.poke_list[i].alive and i != team.primary_poke]
        valid_backup_switches = valid_switches + [team.primary_poke]
        if len(valid_switches) == 0:
            valid_switches = [None]


        moves = []
        switches = []
        for move_index in range(len(my_poke.moveset.moves)):
            move_name = my_poke.moveset.moves[move_index]
            mega = my_poke.can_evolve()
            if my_poke.choiced:
                if move_name != my_poke.move_choice:
                    continue
            if move_name == "U-turn" or move_name == "Volt Switch":
                moves.extend([
                    Action("move", move_index=move_index, mega=mega, backup_switch=j, volt_turn=k)
                    for j in valid_switches for k in valid_switches if (j != k and j != None) or (j is None and k is None)
                ])
            else:
                moves.extend([
                    Action("move", move_index=move_index, mega=mega, backup_switch=j)
                    for j in valid_switches
                ])
        switches.extend([Action("switch", switch_index=i, backup_switch=j) for i in valid_switches for j in valid_backup_switches if j != i and i is not None])

        if opp_poke.ability == "Magnet Pull" and "Steel" in my_poke.typing and "Ghost" not in my_poke.typing:
            switches = []
        elif my_poke.ability == "Shadow Tag" and "Ghost" not in opp_poke.typing:
            switches = []
        return moves + switches

if __name__ == "__main__":
    with open("pokemon_team.txt") as f1, open("pokemon_team2.txt") as f2, open("data/poke.json") as f3:
        data = json.loads(f3.read())
        poke_dict = smogon.Smogon.convert_to_dict(data)
        my_team = Team.make_team(f1.read(), poke_dict)
        opp_team = Team.make_team(f2.read(), poke_dict)
        gamestate = GameState(my_team, opp_team)
