from team import Pokemon
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
    gamestate.get_team(1 - who).primary().choiced = False
def handle_close_combat(gamestate, damage, who):
    gamestate.get_team(who).primary().decrease_stage('spdef', 1)
    gamestate.get_team(who).primary().decrease_stage('pdef', 1)

def handle_stealth_rock(gamestate, damage, who):
    opp_poke = gamestate.get_team(1 - who).primary()
    if opp_poke.ability == "Magic Bounce":
        gamestate.set_rocks(who, True)
    else:
        gamestate.set_rocks(1 - who, True)
    return 0

def handle_defog(gamestate, damage, who):
    gamestate.rocks = [False, False]
    gamestate.spikes = [0, 0]
    return 0

def handle_giga_drain(gamestate, damage, who):
    my_poke = gamestate.get_team(who).primary()
    my_poke.heal((damage / 2.0) / my_poke.final_stats['hp'])
def handle_explosion(gamestate, damage, who):
    gamestate.get_team(who).primary().health = 0
def handle_willowisp(gamestate, damage, who):
    opp_poke = gamestate.get_team(1 - who).primary()
    if "Fire" not in opp_poke.typing:
        opp_poke.set_status("burn")
    return 0
def handle_thunder_wave(gamestate, damage, who):
    opp_poke = gamestate.get_team(1 - who).primary()
    if "Electric" not in opp_poke.typing:
        opp_poke.set_status("paralyze")
    return 0
def handle_seismic_toss(gamestate, damage, who):
    opp_poke = gamestate.get_team(1 - who).primary()
    opp_poke.damage(100.0)
def handle_night_shade(gamestate, damage, who):
    opp_poke = gamestate.get_team(1 - who).primary()
    opp_poke.damage(100.0)
def handle_spikes(gamestate, damage, who):
    gamestate.add_spikes(1 - who)
    return 0
def handle_heal_bell(gamestate, damage, who):
    my_team = gamestate.get_team(who)
    for poke in my_team.poke_list:
        poke.reset_status()
    return 0
def handle_vcreate(gamestate, damage, who):
    my_poke = gamestate.get_team(who).primary()
    my_poke.decrease_stage('pdef', 1)
    my_poke.decrease_stage('spdef', 1)
    my_poke.decrease_stage('spe', 1)
def handle_aromatherapy(gamestate, damage, who):
    my_team = gamestate.get_team(who)
    for poke in my_team.poke_list:
        poke.reset_status()
    return 0
def handle_pain_split(gamestate, damage, who):
    my_poke = gamestate.get_team(who).primary()
    opp_poke = gamestate.get_team(1 - who).primary()
    ave_health = (my_poke.health + opp_poke.health) / 2.0
    my_poke.health = min(my_poke.final_stats['hp'], ave_health)
    opp_poke.health = min(opp_poke.final_stats['hp'], ave_health)
    return 0
def handle_endeavor(gamestate, damage, who):
    my_health = gamestate.get_team(who).primary().health
    gamestate.get_team(1 - who).primary().health = my_health
    return 0
def handle_brave_bird(gamestate, damage, who):
    poke = gamestate.get_team(who).primary()
    poke.damage(damage / 3)
    return 0
def handle_flare_blitz(gamestate, damage, who):
    poke = gamestate.get_team(who).primary()
    poke.damage(damage / 3)
    return 0
def handle_relic_song(gamestate, damage, who):
    my_poke = gamestate.get_team(who).primary()
    my_poke.meloetta_evolve()


def handle_powerup_punch(gamestate, damage, who):
    my_poke = gamestate.get_team(who).primary()
    my_poke.increase_stage("patk", 1)

def power_stored_power(gamestate, who):
    my_poke = gamestate.get_team(who).primary()
    stages = sum([stage for stage in my_poke.stages.values() if stage > 0])
    return 20 + 20 * stages

def power_gyro_ball(gamestate, who):
    my_poke = gamestate.get_team(who).primary()
    opp_poke = gamestate.get_team(1 - who).primary()
    return 25.0 * (opp_poke.get_stat('spe') / my_poke.get_stat('spe'))

#TODO: grass knot and low kick, add weights to smogon
