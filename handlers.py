def handle_draco_meteor(gamestate, my=True):
    if my:
        poke = gamestate.my_team.primary()
    else:
        poke = gamestate.opp_team.primary()
    poke.stages['spatk'] = max(-6, poke.stages['spatk'] - 2)
def handle_superpower(gamestate, my=True):
    if my:
        poke = gamestate.my_team.primary()
    else:
        poke = gamestate.opp_team.primary()
    poke.stages['patk'] = max(-6, poke.stages['patk'] - 1)
    poke.stages['pdef'] = max(-6, poke.stages['pdef'] - 1)
def handle_icy_wind(gamestate, my=True):
    if my:
        poke = gamestate.opp_team.primary()
    else:
        poke = gamestate.my_team.primary()
    poke.stages['spe'] = max(-6, poke.stages['spe'] - 1)
def handle_knock_off(gamestate, my=True):
    if my:
        poke = gamestate.opp_team.primary()
    else:
        poke = gamestate.my_team.primary()
    poke.item = None
def handle_close_combat(gamestate, my=True):
    if my:
        poke = gamestate.my_team.primary()
    else:
        poke = gamestate.opp_team.primary()
    poke.stages['spdef'] = max(-6, poke.stages['spdef'] - 1)
    poke.stages['pdef'] = max(-6, poke.stages['pdef'] - 1)
