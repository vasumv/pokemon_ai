import random
from type import get_multiplier
from math import floor

def void_handler(gamestate, my=True):
    pass

class Move:
    def __init__(self, name,
                       power=None,
                       category=None,
                       priority=0,
                       type=None,
                       accuracy=1.0,
                       handler=void_handler
                 ):
        self.name = name
        self.power = power
        self.category = category
        self.type = type
        self.accuracy = accuracy
        self.handler = handler

    def handle(self, gamestate, my=True):
        return self.handler(gamestate, my=my)

class DamagingMove(Move):

    def handle(self, gamestate, my=True):
        if my:
            attacker = gamestate.my_team.primary()
            defender = gamestate.opp_team.primary()
        else:
            attacker = gamestate.opp_team.primary()
            defender = gamestate.my_team.primary()
        if self.category == "Physical":
            attack = attacker.get_stat("patk")
            defense = defender.get_stat("pdef")
        else:
            attack = attacker.get_stat("spatk")
            defense = defender.get_stat("spdef")
        stab = 1.5 if self.type in attacker.typing else 1
        type = 1
        type_multipliers = [get_multiplier(x, self.type) for x in defender.typing]
        for x in type_multipliers:
            type *= x
        critical = 1
        other = 1
        r = 1
        modifier = stab * type * critical * other * r
        damage = (((42.0) * attack/defense * self.power)/50 + 2) * modifier
        print "%s took %f damage" % (
            defender.name,
            damage
        )
        print "%s has %f attack" % (
            attacker.name,
            attack
        )
        print "%s has %f defense" % (
            defender.name,
            defense
        )
        defender.health -= damage
        defender.health = floor(defender.health)
        print "%s has %f health." % (
            defender.name,
            defender.health
        )
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

