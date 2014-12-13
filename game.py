import json
from smogon import Smogon
from team import Team
from gamestate import GameState
from simulator import Simulator
from gamestate import Action

cache = {}
def get_action(state, simulator, depth=2, path=()):
    if depth == 0:
        #print "Candidate", path, state.evaluate()
        return None, state.evaluate()
    my_legal_actions = state.get_legal_actions(0)
    opp_legal_actions = state.get_legal_actions(1)
    opp_v = float("inf")
    best_action = None
    for opp_action in opp_legal_actions:
        best_opp_action = None
        my_v = float("-inf")
        #log("If I use %s:" % (my_action), depth)
        for my_action in my_legal_actions:
            this_path = tuple(path)
            this_path += ((my_action, opp_action),)
            #print "Evaluating path:", this_path
            new_state = simulator.simulate(state, my_action, opp_action)
            tuple_state = new_state.to_tuple()
            if tuple_state in cache:
                new_action, state_value, _ = cache[tuple_state]
                #print "Hit:", _, state_value
            else:
                #print "Recursing:"
                new_action, state_value = get_action(new_state, simulator, depth=depth - 1, path=this_path)
                cache[tuple_state] = (my_action, state_value, this_path)
            if state_value > my_v:
                best_opp_action = my_action
                my_v = state_value
            print "Done evaluating path:", this_path, state_value
        log("My opponent will use %s" % best_opp_action, depth)
        if my_v < opp_v:
            best_action = best_opp_action
            opp_v = my_v
    return best_action, my_v

def log(msg, depth):
    depth = 2 - depth
    #print ''.join(['\t' for _ in range(depth)]), msg

with open("pokemon_team3.txt") as f1, open("pokemon_team4.txt") as f2, open("data/poke.json") as f3:
    data = json.loads(f3.read())
    poke_dict = Smogon.convert_to_dict(data)
    my_team = Team.make_team(f1.read(), poke_dict)
    opp_team = Team.make_team(f2.read(), poke_dict)
    gamestate = GameState(my_team, opp_team)
    simulator = Simulator()
    #my = Action.create("move 3 1")
    #opp = Action.create("move 2 1")
    #x = simulator.simulate(gamestate, my, opp)
    print get_action(gamestate, simulator)
