from team import Team
from gamestate import GameState
from smogon import Smogon
from move_list import moves
import random
import json

class Simulator():

    def simulate(self, gamestate, my_action, opp_action):
        gamestate = gamestate.deep_copy()

        if my_action.is_switch():
            print "I switched out %s for %s." % (
                gamestate.my_team.primary().name,
                gamestate.my_team[my_action.switch_index].name
            )
            gamestate.my_team.primary_poke = my_action.switch_index
        if opp_action.is_switch():
            print "Opponent switched out %s for %s." % (
                gamestate.opp_team.primary().name,
                gamestate.opp_team[opp_action.switch_index].name
            )
            gamestate.opp_team.primary_poke = opp_action.switch_index

        if my_action.is_move():
            my_move = moves[gamestate.my_team.primary().moveset.moves[my_action.move_index]]
            opp_move = moves["Noop"]
        if opp_action.is_move():
            opp_move = moves[gamestate.opp_team.primary().moveset.moves[opp_action.move_index]]


        my_speed = gamestate.my_team.primary().get_stat("spe")
        opp_speed = gamestate.opp_team.primary().get_stat("spe")
        if my_speed > opp_speed:
            self.make_move(gamestate, my_move, opp_move, True)
        elif my_speed < opp_speed:
            self.make_move(gamestate, my_move, opp_move, False)
        else:
            if random.random() < 0.5:
                self.make_move(gamestate, my_move, opp_move, True)
            else:
                self.make_move(gamestate, my_move, opp_move, False)




        return gamestate

    def make_move(self, gamestate, my_move, opp_move, my=True):
        if my:
            print "I(%s) used %s." % (
                gamestate.my_team.primary(),
                my_move.name
            )
            my_move.handle(gamestate, True)
            print "Opp(%s) used %s." % (
                gamestate.opp_team.primary(),
                opp_move.name
            )
            opp_move.handle(gamestate, False)
        else:
            print "Opp(%s) used %s." % (
                gamestate.opp_team.primary(),
                opp_move.name
            )
            opp_move.handle(gamestate, False)
            print "I(%s) used %s." % (
                gamestate.my_team.primary(),
                my_move.name
            )
            my_move.handle(gamestate, True)
class Action():
    def __init__(self, type, move_index=None, switch_index=None):
        self.type = type
        self.move_index = move_index
        self.switch_index = switch_index

    def is_move(self):
        return self.type == "move"
    def is_switch(self):
        return self.type == "switch"

    @staticmethod
    def create(move_string):
        type, index = move_string.split()
        index = int(index)
        return Action(type, move_index=index, switch_index=index)

with open("pokemon_team.txt") as f1, open("pokemon_team2.txt") as f2, open("data/poke.json") as f3:
    data = json.loads(f3.read())
    poke_dict = Smogon.convert_to_dict(data)
    my_team = Team.make_team(f1.read(), poke_dict)
    opp_team = Team.make_team(f2.read(), poke_dict)
    gamestate = GameState(my_team, opp_team)
    simulator = Simulator()
    my = Action.create("move 0")
    opp = Action.create("switch 3")
    x = simulator.simulate(gamestate, my, opp)
    my = Action.create("move 2")
    opp = Action.create("move 0")
    x = simulator.simulate(x, my, opp)
