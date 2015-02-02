from move_list import moves as MOVES
from mega_items import mega_items as MEGA_ITEMS
from naive_bayes import get_moves
from log import SimulatorLog
import json

import logging
logging.basicConfig()
MOVE_CORRECTIONS = {"ExtremeSpeed": "Extreme Speed",
                    "ThunderPunch": "Thunder Punch",
                    "SolarBeam": "Solar Beam",
                    "DynamicPunch": "Dynamic Punch"}
with open("data/graph.json") as fp:
    graph = json.loads(fp.read())

class Simulator():

    def __init__(self):
        self.log = SimulatorLog()

    def append_log(self, gamestate, lines, my_poke=None, opp_poke=None):
        for line in lines:
            event = self.log.add_event(line, my_poke=my_poke, opp_poke=opp_poke)
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
                if mega == name:
                    return item

        player = event.player
        type = event.type
        team = gamestate.get_team(player)
        poke = get_pokemon(team, event.poke)
        opp_poke = gamestate.get_team(1 - player).primary()

        if type == "faint":
            poke.health = 0
            poke.alive = False
            print "%s fainted." % (poke)
        elif type == "mega_evolve":
            poke.item = get_mega_item(event.details['mega'])
            team = gamestate.get_team(player)
            team.poke_list[team.primary_poke] = poke.mega_evolve()
            print poke.ability
            print "%s mega evolved!" % (poke)
        elif type == "damage":
            hp = poke.final_stats['hp']
            poke.damage(event.details['damage'] / 100 * hp)
            print "%s got damaged: %f" % (poke, event.details['damage'])
        elif type == "move":
            print "%s used %s." % (poke, event.details['move'])
            if player == 1:
                move = event.details['move']
                if move in MOVE_CORRECTIONS:
                    move = MOVE_CORRECTIONS[move]
                if move not in poke.moveset.known_moves:
                    poke.moveset.known_moves.append(move)
                    poke_name = poke.name
                    if poke_name == "Charizard-Mega-X" or poke_name == "Charizard-Mega-Y":
                        poke_name = "Charizard"
                    elif poke_name[:-5] == "-Mega":
                        poke_name = poke_name[:-5]
                    guess_moves = [x[0] for x in get_moves(poke_name, poke.moveset.known_moves, graph) if x[0] != "Hidden Power"][:4-len(poke.moveset.known_moves)]
                    poke.moveset.moves = poke.moveset.known_moves + guess_moves
            if poke.item in ["Choice Scarf", "Choice Specs", "Choice Band"]:
                moves = ["Hidden Power" if "Hidden Power" in m else m for m in poke.moveset.moves]
                try:
                    moves.index(event.details['move'])
                    poke.choiced = True
                    poke.move_choice = event.details['move']
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
            print "%s regained health" % poke
        elif type == "leftovers":
            poke.item = "Leftovers"
            poke.heal(1.0 / 16)
            print event
            print "%s regained health due to leftovers" % poke
        elif type == "life_orb":
            poke.item = "Life Orb"
            poke.damage_percent(1.0/10)
        elif type == "leech_seed":
            damage = poke.damage_percent(1.0 / 8)
            opp_poke.heal(damage)
            print "%s was sapped and %s gained health due to leech seed." % (poke, opp_poke)
        elif type == "rocks":
            gamestate.set_rocks(player, True)
            print "Player %u got rocked!" % player
        elif type == "spikes":
            gamestate.spikes[player] += 1
            print "Player %u now has %d spikes!" % (player, gamestate.spikes[player])
        elif type == "rocks_gone":
            gamestate.set_rocks(player, False)
            print "Player %u's rocks disappeared!" % player
        elif type == "burn":
            poke.set_status("burn")
        elif type == "paralyze":
            poke.set_status("paralyze")
            print "%s got burned!" % poke
        elif type == "hurt_burn":
            poke.damage_percent(1.0 / 8)
            print "%s got hurt due to its burn!" % poke
        elif type == "float_balloon":
            poke.item = "Air Balloon"
            print "%s has an air balloon!" % poke
        elif type == "pop_balloon":
            poke.item = None
            print "%s's air balloon was popped!" % poke
        elif type == "new_item":
            poke.item = event.details['item']
            print "%s got a %s" % (poke, event.details['item'])
        elif type == "lost_item":
            poke.item = None
            poke.choiced = False
            print "%s lost its item!" % poke
        elif type == "belly_drum":
            poke.increase_stage('patk', 9999)
        elif type == "mold_breaker":
            print poke
            poke.ability = "Mold Breaker"
            print "%s has mold breaker!" % poke
        elif type == "disabled":
            poke.ability = "Mold Breaker"
            move = event.details['move']
            print "%s has mold breaker!" % poke



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

        my_paralyze = 0.25 if my_poke.status == "paralyze" else 1.0
        opp_paralyze = 0.25 if opp_poke.status == "paralyze" else 1.0

        my_final_speed = my_poke.get_stat("spe") * my_spe_multiplier * my_paralyze
        opp_final_speed = opp_poke.get_stat("spe") * opp_spe_multiplier * opp_paralyze

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
        if my_poke.ability == "Prankster":
            if my_move.category != "Physical" and my_move.category != "Special":
                my_move.priority += 1
        if opp_poke.ability == "Prankster":
            if opp_move.category != "Physical" and opp_move.category != "Special":
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
            action = actions[i]
            if action.mega:
                team.poke_list[team.primary_poke] = team.primary().mega_evolve(log=log)
                gamestate.switch_pokemon(team.primary_poke, i, log=log, hazards=False)

        for i in [first, 1 - first]:
            team = gamestate.get_team(i)
            other_team = gamestate.get_team(1 - i)

            move = moves[i]
            action = actions[i]
            other_action = actions[1 - i]
            damage = move.handle(gamestate, i, log=log)
            if log:
                print ("%s used %s and dealt %u damage." % (
                    team.primary(),
                    move.name,
                    damage
                ))
            if damage > 0 and other_team.primary().item == "Air Balloon":
                other_team.primary().item = None
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
