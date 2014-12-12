import json
from smogon import Smogon
from team import Team
from gamestate import GameState
from simulator import Simulator
from gamestate import Action

def get_action(state, simulator, depth=2):
    if depth == 0:
        return None, state.evaluate()
    my_legal_actions = state.get_legal_actions(0)
    opp_legal_actions = state.get_legal_actions(1)

    my_v = float("-inf")
    best_action = None
    for my_action in my_legal_actions:
        print "My Action:", my_action
        opp_v = float("inf")
        for opp_action in opp_legal_actions:
            print "I'm trying", my_action, opp_action
            new_state = simulator.simulate(state, my_action, opp_action)
            _, state_value = get_action(new_state, simulator, depth - 1)
            print "Value:", state_value
            opp_v = min(state_value, opp_v)
        if opp_v > my_v:
            best_action = my_action
            my_v = opp_v
        print "Better", best_action, my_v
    return best_action, my_v

with open("pokemon_team3.txt") as f1, open("pokemon_team2.txt") as f2, open("data/poke.json") as f3:
    data = json.loads(f3.read())
    poke_dict = Smogon.convert_to_dict(data)
    my_team = Team.make_team(f1.read(), poke_dict)
    opp_team = Team.make_team(f2.read(), poke_dict)
    gamestate = GameState(my_team, opp_team)
    simulator = Simulator()
    my = Action.create("move 3")
    opp = Action.create("move 2")
    x = simulator.simulate(gamestate, my, opp)
    print get_action(gamestate, simulator)
