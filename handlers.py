def void_handler(gamestate, damage, who):
    return 0

def handle_draco_meteor(gamestate, damage, who):
    gamestate.get_team(who).primary().decrease_stage('spatk', 2)
def handle_superpower(gamestate, damage, who):
    gamestate.get_team(who).primary().decrease_stage('patk', 1)
    gamestate.get_team(who).primary().decrease_stage('pdef', 1)
def handle_icy_wind(gamestate, damage, who):
    gamestate.get_team(1 - who).primary().decrease_stage('spe', 1)
def handle_knock_off(gamestate, damage, who):
    gamestate.get_team(1 - who).primary().item = None
def handle_close_combat(gamestate, damage, who):
    gamestate.get_team(who).primary().decrease_stage('spdef', 1)
    gamestate.get_team(who).primary().decrease_stage('pdef', 1)

def handle_stealth_rock(gamestate, damage, who):
    gamestate.set_rocks(1 - who, True)
    return 0

def handle_defog(gamestate, damage, who):
    gamestate.rocks = [False, False]
    gamestate.spikes = [0, 0]
    return 0

def handle_giga_drain(gamestate, damage, who):
    pass
def handle_explosion(gamestate, damage, who):
    gamestate.get_team(who).primary().health = 0
def handle_willowisp(gamestate, damage, who):
    opp_poke = gamestate.get_team(1 - who).primary()
    if "Fire" not in opp_poke.typing:
        opp_poke.set_status("burn")
    return 0
def handle_seismic_toss(gamestate, damage, who):
    opp_poke = gamestate.get_team(1 - who).primary()
    opp_poke.damage(100.0)
def handle_spikes(gamestate, damage, who):
    gamestate.add_spikes(1 - who)
def handle_heal_bell(gamestate, damage, who):
    my_team = gamestate.get_team(who)
    for poke in my_team.poke_list:
        poke.reset_status()
def handle_aromatherapy(gamestate, damage, who):
    my_team = gamestate.get_team(who)
    for poke in my_team.poke_list:
        poke.reset_status()
def power_gyro_ball(gamestate, who):
    my_poke = gamestate.get_team(who).primary()
    opp_poke = gamestate.get_team(1 - who).primary()
    return 25.0 * (opp_poke.get_stat('spe') / my_poke.get_stat('spe'))

#TODO: grass knot and low kick, add weights to smogon
