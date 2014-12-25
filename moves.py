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
                 ):
        self.name = name
        self.power = power
        self.category = category
        self.type = type
        self.accuracy = accuracy
        self.handler = handler
        self.priority = priority

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
        abs_atk_buffs = 1.0 + 0.5 * abs(attacker.stages[atks])
        abs_def_buffs = 1.0 + 0.5 * abs(defender.stages[defs])
        atk_stage_multiplier = abs_atk_buffs if attacker.stages[atks] > 0 else 1 / abs_atk_buffs
        def_stage_multiplier = abs_def_buffs if defender.stages[defs] > 0 else 1 / abs_def_buffs
        accuracy = self.accuracy
        r_acc = random.random()
        type = 1
        move_type = self.type
        other = 1.0 * atk_stage_multiplier / def_stage_multiplier

        if attacker.ability == "Pixilate":
            if move_type == "Normal":
                move_type = "Fairy"
                other *= 1.3
        elif attacker.ability == "Aerilate":
            if move_type == "Normal":
                move_type = "Flying"
                other *= 1.3
        elif attacker.ability == "Protean":
            attacker.typing = [move_type]
        elif defender.ability == "Levitate" and move_type == "Ground":
            other *= 0
        elif attacker.ability == "Technician" and self.power <= 60:
            other *= 1.5

        if self.name == "Knock Off" and defender.item is not None:
            other *= 1.5

        if attacker.item in set(["Choice Scarf", "Choice Band", "Choice Specs"]):
            attacker.choiced = True
            attacker.move_choice = self.name
        if attacker.item == "Choice Band" and self.category == "Physical":
            other *= 1.5
        if attacker.item == "Choice Specs" and self.category == "Special":
            other *= 1.5
        if defender.item == "Assault Vest" and self.category == "Special":
            defense *= 1.5

        stab = 1.5 if move_type in attacker.typing else 1
        if attacker.ability == "Adaptability" and stab == 1.5:
            stab = 2
        type_multipliers = [get_multiplier(x, move_type) for x in defender.typing]
        for x in type_multipliers:
            type *= x
        critical = 1
        r = 1
        modifier = stab * type * critical * other * r
        if attacker.ability == "Huge Power" or attacker.ability == "Pure Power":
            attack *= 2
        damage = (((42.0) * attack/defense * self.power)/50 + 2) * modifier
        if 0 < accuracy:
            defender.health -= damage
            if defender.health <= 0:
                defender.health = 0.0
                defender.alive = False
            defender.health = floor(defender.health)
        self.handler(gamestate, my=my)
        return damage

class HealingMove(Move):
    def __init__(self, name,
                 category=None,
                 priority=0,
                 type=None,
                 accuracy=1.0,
                 handler=void_handler,
                 healing_percent=0
                 ):
        Move.__init__(self, name,
                      category=category,
                      priority=priority,
                      type=type,
                      accuracy=accuracy,
                      handler=handler
                      )
        self.healing_percent = healing_percent

    def handle(self, gamestate, my=True):
        if my:
            poke = gamestate.my_team.primary()
        else:
            poke = gamestate.opp_team.primary()
        poke.health = min(self.healing_percent * poke.final_stats['hp'],
                           poke.final_stats['hp'])
        return self.handler(gamestate, my=my)


def default_handler(gamestate, my=True):
    pass

