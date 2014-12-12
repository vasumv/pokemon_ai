import random
from type import get_multiplier
from math import floor

def void_handler(gamestate, my=True):
    pass

class Move:
    def __init__(self, name,
                 power=0,
                 category=None,
                 priority=0,
                 type=None,
                 accuracy=1.0,
                 handler=void_handler,
                 backup_switch=""
                 ):
        self.name = name
        self.power = power
        self.category = category
        self.type = type
        self.accuracy = accuracy
        self.handler = handler
        self.backup_switch = backup_switch

    def handle(self, gamestate, my=True):
        return self.handler(gamestate, my=my)


class BoostingMove(Move):
    def __init__(self, name,
                 boosts={},
                 category=None,
                 priority=0,
                 type=None,
                 accuracy=1.0,
                 handler=void_handler,
                 ):
        Move.__init__(self, name,
                      category=category,
                      priority=priority,
                      type=type,
                      accuracy=accuracy,
                      handler=handler
                      )
        self.boosts = boosts

    def handle(self, gamestate, my=True):
        if my:
            poke = gamestate.my_team.primary()
        else:
            poke = gamestate.opp_team.primary()

        for boost, amount in self.boosts.items():
            increase = poke.stages[boost] + amount
            if increase < -6 or increase > 6:
                continue
            poke.stages[boost] = increase
            #print "%s increased %s by %d stages and is now at stage %d" % (
                        #poke.name,
                        #boost,
                        #amount,
                        #poke.stages[boost]
                        #)

class DamagingMove(Move):

    def handle(self, gamestate, my=True):
        if my:
            attacker = gamestate.my_team.primary()
            defender = gamestate.opp_team.primary()
        else:
            attacker = gamestate.opp_team.primary()
            defender = gamestate.my_team.primary()
        if self.category == "Physical":
            atks = "patk"
            defs = "pdef"
        else:
            atks = "spatk"
            defs = "spdef"
        attack = attacker.get_stat(atks)
        defense = defender.get_stat(defs)
        abs_atk_buffs = 1.0 + 0.5 * attacker.stages[atks]
        abs_def_buffs = 1.0 + 0.5 * defender.stages[defs]
        atk_stage_multiplier = abs_atk_buffs if attacker.stages[atks] > 0 else 1 / abs_atk_buffs
        def_stage_multiplier = abs_def_buffs if defender.stages[defs] > 0 else 1 / abs_def_buffs
        stab = 1.5 if self.type in attacker.typing else 1
        accuracy = self.accuracy
        r_acc = random.random()
        type = 1
        type_multipliers = [get_multiplier(x, self.type) for x in defender.typing]
        for x in type_multipliers:
            type *= x
        critical = 1
        other = 1.0 * atk_stage_multiplier / def_stage_multiplier
        r = 1
        modifier = stab * type * critical * other * r
        damage = (((42.0) * attack/defense * self.power)/50 + 2) * modifier
        if r_acc < accuracy:
            #print "%s has %f attack" % (
                #attacker.name,
                #attack
            #)
            #print "%s has %f defense" % (
                #defender.name,
                #defense
            #)
            #print "%s took %f damage" % (
                #defender.name,
                #damage
            #)
            defender.health -= damage
            defender.health = floor(defender.health)
            #print "%s has %f health." % (
                #defender.name,
                #defender.health
            #)
        #else:
            #print "%s missed!" % (
                #attacker.name
            #)
        return self.handler(gamestate, my=my)

def default_handler(gamestate, my=True):
    pass

def handle_ice_beam(gamestate, my=True):
    val = random.random()
    if val < 0.1:
        if my:
            gamestate.opp_team.primary().set_status("frozen")
        else:
            gamestate.my_team.primary().set_status("frozen")

