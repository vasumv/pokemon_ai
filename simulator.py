from move_list import moves
import random

class Simulator():

    def simulate(self, gamestate, my_action, opp_action, log=False):
        assert not gamestate.is_over()
        gamestate = gamestate.deep_copy()

        my_spe_buffs = 1.0 + 0.5 * abs(gamestate.my_team.primary().stages['spe'])
        opp_spe_buffs = 1.0 + 0.5 * abs(gamestate.opp_team.primary().stages['spe'])
        my_spe_multiplier = my_spe_buffs if gamestate.my_team.primary().stages['spe'] > 0 else 1 / my_spe_buffs
        opp_spe_multiplier = opp_spe_buffs if gamestate.opp_team.primary().stages['spe'] > 0 else 1 / opp_spe_buffs

        if gamestate.my_team.primary().item == "Choice Scarf":
            my_spe_multiplier *= 1.5
        if gamestate.opp_team.primary().item == "Choice Scarf":
            opp_spe_multiplier *= 1.5


        my_speed = gamestate.my_team.primary().get_stat("spe") * my_spe_multiplier
        opp_speed = gamestate.opp_team.primary().get_stat("spe") * opp_spe_multiplier

        if my_action.is_switch():
            gamestate.my_team.set_primary(my_action.switch_index)
            my_move = moves["Noop"]
            if gamestate.my_team.primary().ability == "Intimidate":
                if log: print gamestate.opp_team.primary(), "got intimidated."
                gamestate.opp_team.primary().stages['patk'] -= 1
        if opp_action.is_switch():
            gamestate.opp_team.set_primary(opp_action.switch_index)
            opp_move = moves["Noop"]
            if not my_action.is_switch() and gamestate.opp_team.primary().ability == "Intimidate":
                gamestate.my_team.primary().stages['patk'] -= 1
                if log: print gamestate.my_team.primary(), "got intimidated."

        if my_action.is_move():
            my_move = moves[gamestate.my_team.primary().moveset.moves[my_action.move_index]]
        if opp_action.is_move():
            opp_move = moves[gamestate.opp_team.primary().moveset.moves[opp_action.move_index]]

        if gamestate.my_team.primary().ability == "Gale Wings":
            if my_move.type == "Flying":
                my_move.priority += 1
        if gamestate.opp_team.primary().ability == "Gale Wings":
            if opp_move.type == "Flying":
                opp_move.priority += 1
        if my_move.priority > opp_move.priority:
            self.make_move(gamestate, my_move, opp_move, my_action, opp_action, True, log=log)
        elif opp_move.priority > my_move.priority:
            self.make_move(gamestate, my_move, opp_move, my_action, opp_action, False, log=log)
        else:
            if my_speed > opp_speed:
                self.make_move(gamestate, my_move, opp_move, my_action, opp_action, True, log=log)
            elif my_speed < opp_speed:
                self.make_move(gamestate, my_move, opp_move, my_action, opp_action, False, log=log)
            else:
                if random.random() < 0.5:
                    self.make_move(gamestate, my_move, opp_move, my_action, opp_action, True, log=log)
                else:
                    self.make_move(gamestate, my_move, opp_move, my_action, opp_action, False, log=log)

        return gamestate

    def make_move(self, gamestate, my_move, opp_move, my_action, opp_action, my=True, log=False):
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

        attacker_damage = attacker_move.handle(gamestate, my)
        if log:
            print "%s used %s." % (
                attacker.primary(),
                attacker_move.name
            )
        if attacker_damage > 0 and (attacker_move.name == "U-turn" or attacker_move.name == "Volt Switch") and attacker_action.volt_turn is not None:
            attacker.set_primary(attacker_action.volt_turn)
            if attacker.primary() and attacker.primary().ability == "Intimidate":
                if log: print defender.primary(), "got intimidated."
                defender.primary().stages['patk'] -= 1

        if defender.primary().health <= 0:
            if log:
                print "%s fainted." % defender.primary()
            defender.primary().alive = False
            defender.set_primary(defender_action.backup_switch)
            defender_move = moves['Noop']
            if defender.primary() and defender.primary().ability == "Intimidate":
                if log: print attacker.primary(), "got intimidated."
                attacker.primary().stages['patk'] -= 1

        if gamestate.is_over():
            return

        defender_damage = defender_move.handle(gamestate, not my)
        if log:
            print "%s used %s." % (
                defender.primary(),
                defender_move.name
            )
        if defender_damage > 0 and (defender_move.name == "U-turn" or defender_move.name == "Volt Switch") and defender_action.volt_turn is not None:
            defender.set_primary(defender_action.volt_turn)
            if defender.primary() and defender.primary().ability == "Intimidate":
                if log: print attacker.primary(), "got intimidated."
                attacker.primary().stages['patk'] -= 1
        if attacker.primary().health <= 0:
            if log:
                print "%s fainted." % attacker.primary()
            attacker.primary().alive = False
            attacker.set_primary(attacker_action.backup_switch)
            if attacker.primary() and attacker.primary().ability == "Intimidate":
                if log: print defender.primary(), "got intimidated."
                defender.primary().stages['patk'] -= 1

        if gamestate.is_over():
            return

class Action():
    def __init__(self, type, move_index=None, switch_index=None, mega=False, backup_switch=None, volt_turn=None):
        self.type = type
        self.move_index = move_index
        self.switch_index = switch_index
        self.backup_switch = backup_switch
        self.mega = mega
        self.volt_turn = volt_turn

    def is_move(self):
        return self.type == "move"
    def is_switch(self):
        return self.type == "switch"

    def __eq__(self, other):
        if self.type != other.type:
            return False
        if self.type == "move":
            return (self.move_index == other.move_index and self.backup_switch == other.backup_switch and self.mega == other.mega and self.volt_turn == other.volt_turn)
        if self.type == "switch":
            return (self.switch_index == other.switch_index and self.backup_switch == other.backup_switch)
        return False

    def __hash__(self):
        if self.type == "move":
            return hash(self.type, self.move_index, self.backup_switch, self.mega)
        if self.type == "switch":
            return (self.type, self.switch_index, self.backup_switch)

    @staticmethod
    def create(move_string):
        splt = move_string.strip().split()
        if len(splt) == 4:
            volt_turn = None
            type, index, backup, str_mega = splt
        if len(splt) == 5:
            type, index, backup, str_mega, volt_turn = splt
        index = int(index)
        backup = None if backup == "None" else int(backup)
        mega = True if str_mega == "True" else False
        volt_turn = int(volt_turn) if volt_turn is not None else None
        return Action(type, move_index=index, switch_index=index, mega=mega, backup_switch=backup, volt_turn=volt_turn)
    def __repr__(self):
        if self.type == "move":
            if self.volt_turn is None:
                return "%s(%u, %s, %s)" % (self.type, self.move_index, self.backup_switch, self.mega)
            else:
                return "%s(%u, %s, %s, %u)" % (self.type, self.move_index, self.backup_switch, self.mega, self.volt_turn)
        elif self.type == "switch":
            return "%s(%s, %s)" % (self.type, self.switch_index, self.backup_switch)
