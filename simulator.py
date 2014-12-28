from move_list import moves as MOVES
from mega_items import mega_items as MEGA_ITEMS
from log import SimulatorLog

import logging
logging.basicConfig()


class Simulator():

    def __init__(self):
        self.log = SimulatorLog()

    def append_log(self, gamestate, lines):
        for line in lines:
            event = self.log.add_event(line)
            if not event:
                continue
            self.handle_event(gamestate, event)

    def handle_event(self, gamestate, event):
        def get_pokemon(team, name):
            for poke in team:
                if poke.name == name:
                    return poke
        def get_mega_item(name):
            for item, (premega, mega) in MEGA_ITEMS.items():
                if premega == name:
                    return item

        player = event.player
        type = event.type
        team = gamestate.get_team(player)
        poke = get_pokemon(team, event.poke)

        if type == "faint":
            poke.health = 0
            poke.alive = False
            print "%s fainted." % (poke)
        elif type == "mega_evolve":
            poke.item = get_mega_item(poke.name)
            team = gamestate.get_team(player)
            team.poke_list[team.primary_poke] = poke.mega_evolve()
            print "%s mega evolved!" % (poke)
        elif type == "damage":
            hp = poke.final_stats['hp']
            poke.damage(event.details['damage'] / 100 * hp)
            print "%s got damaged: %f" % (poke, event.details['damage'])
        elif type == "move":
            print "%s used %s." % (poke, event.details['move'])
            if poke.item in ["Choice Scarf", "Choice Specs", "Choice Band"]:
                moves = ["Hidden Power" if "Hidden Power" in m else m for m in poke.moveset.moves]
                try:
                    move_index = moves.index(event.details['move'])
                    poke.choiced = True
                    poke.move_choice = move_index
                    print "%s is choiced to %s" % (poke, event.details['move'])
                except:
                    pass

        elif type == "stat_change":
            stages = event.details['stages']
            if stages > 0:
                poke.increase_stage(event.details['stat'], abs(stages))
                print "%s increased its %s by %d stages" % (poke, event.details['stat'], stages)
            else:
                poke.decrease_stage(event.details['stat'], abs(stages))
                print "%s decreased its %s by %d stages" % (poke, event.details['stat'], stages)
        elif type == "switch":
            team.set_primary(team.poke_list.index(poke))
            print "Player %d switched in %s" % (player, poke)
        elif type == "regain_health":
            poke.heal(0.5)
        elif type == "leftovers":
            poke.heal(1.0 / 16)

    def simulate(self, gamestate, actions, who, log=False):
        assert not gamestate.is_over()
        gamestate = gamestate.deep_copy()


        my_team = gamestate.get_team(who)
        opp_team = gamestate.get_team(1 - who)

        my_poke = my_team.primary()
        opp_poke = opp_team.primary()

        my_action = actions[who]
        opp_action = actions[1 - who]

        my_speed = my_poke.get_stage('spe')
        opp_speed = opp_poke.get_stage('spe')

        my_spe_buffs = 1.0 + 0.5 * abs(my_speed)
        opp_spe_buffs = 1.0 + 0.5 * abs(opp_speed)

        my_spe_multiplier = my_spe_buffs if my_speed > 0 else 1 / my_spe_buffs
        opp_spe_multiplier = opp_spe_buffs if opp_speed > 0 else 1 / opp_spe_buffs


        if my_poke.item == "Choice Scarf":
            my_spe_multiplier *= 1.5
        if opp_poke.item == "Choice Scarf":
            opp_spe_multiplier *= 1.5


        my_final_speed = my_poke.get_stat("spe") * my_spe_multiplier
        opp_final_speed = opp_poke.get_stat("spe") * opp_spe_multiplier

        if my_action.is_switch():
            gamestate.switch_pokemon(my_action.switch_index, who, log=log)
            my_move = MOVES["Noop"]
            my_poke = my_team.primary()
        if opp_action.is_switch():
            gamestate.switch_pokemon(opp_action.switch_index, 1 - who, log=log)
            opp_move = MOVES["Noop"]
            opp_poke = opp_team.primary()

        if my_action.is_move():
            my_move = MOVES[my_poke.moveset.moves[my_action.move_index]]
        if opp_action.is_move():
            opp_move = MOVES[opp_poke.moveset.moves[opp_action.move_index]]

        if my_poke.ability == "Gale Wings":
            if my_move.type == "Flying":
                my_move.priority += 1
        if opp_poke.ability == "Gale Wings":
            if opp_move.type == "Flying":
                opp_move.priority += 1

        first = None
        if log:
            print "Player 1 speed", my_final_speed
            print "Player 2 speed", opp_final_speed
        if my_move.priority > opp_move.priority:
            first = who
        elif opp_move.priority > my_move.priority:
            first = 1 - who
        else:
            if my_final_speed > opp_final_speed:
                first = who
            elif opp_final_speed > my_final_speed:
                first = 1 - who
            else:
                first = 1#who

        moves = [None, None]
        moves[who] = my_move
        moves[1 - who] = opp_move
        self.make_move(gamestate, moves, actions, first, who, log=log)
        return gamestate

    def make_move(self, gamestate, moves, actions, first, who, log=False):

        for i in [first, 1 - first]:
            team = gamestate.get_team(i)
            other_team = gamestate.get_team(1 - i)

            move = moves[i]
            action = actions[i]
            if action.mega:
                team.poke_list[team.primary_poke] = team.primary().mega_evolve(log=log)
                gamestate.switch_pokemon(team.primary_poke, i, log=log)

            other_action = actions[1 - i]
            damage = move.handle(gamestate, i, log=log)
            if log:
                print ("%s used %s and dealt %u damage." % (
                    team.primary(),
                    move.name,
                    damage
                ))
            if damage > 0 and move.name in ["U-turn", "Volt Switch"] and action.volt_turn is not None:
                gamestate.switch_pokemon(action.volt_turn, i, log=log)

            if other_team.primary().health == 0:
                other_team.primary().alive = False
                if log:
                    print (
                        "%s fainted." % other_team.primary()
                    )

            if gamestate.is_over():
                return

            if not other_team.primary().alive:
                gamestate.switch_pokemon(other_action.backup_switch, 1 - i, log=log)
                break

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
