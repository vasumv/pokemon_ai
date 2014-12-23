import json
from smogon import Smogon
from team import Team
from gamestate import GameState
from simulator import Simulator
from gamestate import Action

cache = {}
def get_pess_action(state, simulator, depth=1, path=()):
    if state.is_over() or depth == 0:
        return None, state.evaluate()
    my_legal_actions = state.get_legal_actions(0)
    opp_legal_actions = state.get_legal_actions(1)
    my_v = float("-inf")
    best_action = None
    for my_action in my_legal_actions:
        opp_v = float("inf")
        for opp_action in opp_legal_actions:
            this_path = tuple(path)
            this_path += ((my_action, opp_action),)
            new_state = simulator.simulate(state, my_action, opp_action)
            tuple_state = new_state.to_tuple()
            if tuple_state in cache:
                new_action, state_value, _ = cache[tuple_state]
            else:
                new_action, state_value = get_pess_action(new_state, simulator, depth=depth - 1, path=this_path)
                cache[tuple_state] = (my_action, state_value, this_path)
            if opp_v >= state_value:
                opp_v = state_value
        if opp_v > my_v:
            best_action = my_action
            my_v = opp_v
    return best_action, my_v

def get_player_action(gamestate):
    valid = False
    my_legal = gamestate.get_legal_actions(1)
    while not valid:
        action_string = raw_input('> ')
        try:
            my_action = Action.create(action_string)
            if my_action not in my_legal:
                print "Illegal move", my_action, my_legal
                assert False
            valid = True
        except:
            pass
    return my_action
from argparse import ArgumentParser

argparser = ArgumentParser()
argparser.add_argument('team1')
argparser.add_argument('team2')
argparser.add_argument('--depth', type=int, default=2)

args = argparser.parse_args()
with open(args.team1) as f1, open(args.team2) as f2, open("data/poke2.json") as f3:
    data = json.loads(f3.read())
    poke_dict = Smogon.convert_to_dict(data)
    my_team = Team.make_team(f2.read(), poke_dict)
    opp_team = Team.make_team(f1.read(), poke_dict)
    gamestate = GameState(my_team, opp_team)
    simulator = Simulator()
    while not gamestate.is_over():
        print "=========================================================================================="
        print "My primary:", gamestate.opp_team.primary()
        print "Their primary:", gamestate.my_team.primary()

        print
        print "My moves:", [m for m in gamestate.opp_team.primary().moveset.moves]
        print "My switches:", [(m, i) for i, m in enumerate(gamestate.opp_team.poke_list) if m != gamestate.opp_team.primary()]
        my_action = get_player_action(gamestate)
        #import random
        #my_action = random.choice(gamestate.get_legal_actions(1))
        opp_action = get_pess_action(gamestate, simulator, depth=args.depth)[0]
        gamestate = simulator.simulate(gamestate, opp_action, my_action, log=True)
    if gamestate.opp_team.alive():
        print "You win!"
        print "Congrats to", gamestate.opp_team
        print "Sucks for", gamestate.my_team
    else:
        print "You lose!"
        print "Congrats to", gamestate.my_team
        print "Sucks for", gamestate.opp_team
