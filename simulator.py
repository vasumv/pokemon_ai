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
        if my_move.priority > opp_move.priority:
            self.make_move(gamestate, my_move, opp_move, my_action, opp_action, True)
        elif opp_move.priority > my_move.priority:
            self.make_move(gamestate, my_move, opp_move, my_action, opp_action, False)
        else:
        #print "My speed", my_speed
        #print "Opp speed", opp_speed
            if my_speed > opp_speed:
                self.make_move(gamestate, my_move, opp_move, my_action, opp_action, True)
            elif my_speed < opp_speed:
                self.make_move(gamestate, my_move, opp_move, my_action, opp_action, False)
            else:
                if random.random() < 0.5:
                    self.make_move(gamestate, my_move, opp_move, my_action, opp_action, True)
                else:
                    self.make_move(gamestate, my_move, opp_move, my_action, opp_action, False)

        return gamestate

    def make_move(self, gamestate, my_move, opp_move, my_action, opp_action, my=True):
        if my:
            attacker = gamestate.my_team
            attacker_move = my_move
            attacker_action = my_action

            defender = gamestate.opp_team
            defender_move = opp_move
            defender_action = opp_action
        else:
            attacker = gamestate.opp_team
            attacker_move = opp_move
            attacker_action = opp_action

            defender = gamestate.my_team
            defender_move = my_move
            defender_action = my_action

        if attacker_action.mega:
            poke = attacker.primary().mega_evolve()
            attacker.poke_list[attacker.primary_poke] = poke

        if defender_action.mega:
            poke = defender.primary().mega_evolve()
            defender.poke_list[defender.primary_poke] = poke

        attacker_move.handle(gamestate, my)
        #print "%s used %s." % (
            #attacker.primary(),
            #attacker_move.name
        #)
        if not defender.primary().alive:
            #print "%s fainted." % defender.primary()
            defender.set_primary(defender_action.backup_switch)
            defender_move = moves['Noop']

        defender_move.handle(gamestate, not my)
        #print "%s used %s." % (
            #defender.primary(),
            #defender_move.name
        #)
        if not attacker.primary().alive:
            #print "%s fainted." % attacker.primary()
            attacker.set_primary(attacker_action.backup_switch)

class Action():
    def __init__(self, type, move_index=None, switch_index=None, mega=False, backup_switch=None):
        self.type = type
        self.move_index = move_index
        self.switch_index = switch_index
        self.backup_switch = backup_switch
        self.mega = mega
        assert backup_switch != None

    def is_move(self):
        return self.type == "move"
    def is_switch(self):
        return self.type == "switch"

    @staticmethod
    def create(move_string):
        type, index, backup, str_mega = move_string.split()
        index = int(index)
        backup = int(backup)
        mega = bool(str_mega)
        return Action(type, move_index=index, switch_index=index, mega=mega, backup_switch=backup)
    def __repr__(self):
        if self.type == "move":
                return "%s(%u, %u, %s)" % (self.type, self.move_index, self.backup_switch, self.mega)
        elif self.type == "switch":
            return "%s(%u, %u)" % (self.type, self.switch_index, self.backup_switch)
