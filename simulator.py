from move_list import moves
import random

class Simulator():

    def simulate(self, gamestate, my_action, opp_action):
        gamestate = gamestate.deep_copy()

        if my_action.is_switch():
            #print "I switched out %s for %s." % (
                #gamestate.my_team.primary().name,
                #gamestate.my_team[my_action.switch_index].name
            #)
            gamestate.my_team.primary_poke = my_action.switch_index
            my_move = moves["Noop"]
        if opp_action.is_switch():
            #print "Opponent switched out %s for %s." % (
                #gamestate.opp_team.primary().name,
                #gamestate.opp_team[opp_action.switch_index].name
            #)
            gamestate.opp_team.primary_poke = opp_action.switch_index
            opp_move = moves["Noop"]

        if my_action.is_move():
            my_move = moves[gamestate.my_team.primary().moveset.moves[my_action.move_index]]
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
            #print "I(%s) used %s." % (
                #gamestate.my_team.primary(),
                #my_move.name
            #)
            my_move.handle(gamestate, True)
            #print "Opp(%s) used %s." % (
                #gamestate.opp_team.primary(),
                #opp_move.name
            #)
            opp_move.handle(gamestate, False)
        else:
            #print "Opp(%s) used %s." % (
                #gamestate.opp_team.primary(),
                #opp_move.name
            #)
            opp_move.handle(gamestate, False)
            #print "I(%s) used %s." % (
                #gamestate.my_team.primary(),
                #my_move.name
            #)
            my_move.handle(gamestate, True)

class Action():
    def __init__(self, type, move_index=None, switch_index=None, backup_switch=""):
        self.type = type
        self.move_index = move_index
        self.switch_index = switch_index
        self.backup_switch = backup_switch

    def is_move(self):
        return self.type == "move"
    def is_switch(self):
        return self.type == "switch"

    @staticmethod
    def create(move_string):
        type, index = move_string.split()
        index = int(index)
        return Action(type, move_index=index, switch_index=index)

    def __repr__(self):
        if self.type == "move":
            return "%s(%u, %u)" % (self.type, self.move_index, self.backup_switch)
        elif self.type == "switch":
            return "%s(%u, %u)" % (self.type, self.switch_index, self.backup_switch)
