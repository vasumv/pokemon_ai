import re

stat_map = {'Attack': 'patk',
            'Special Attack': 'spatk',
            'Defense': 'pdef',
            'Special Defense': 'spdef',
            'Speed': 'spe'}
modifier_map = {None: 1,
                'harshly': 2,
                'sharply': 2,
                'drastically': 3}
direction_map = {'fell': -1,
                 'rose': 1,
                 'lowered': -1,
                 'raised': 1}

STATS = '|'.join(list(stat_map.keys()))
STAT_MODIFIER = r"sharply |drastically |harshly "
ABILITY_STAT_DIRECTION = r"lowered|raised"
MOVE_STAT_DIRECTION = r"fell|rose"

ABILITY_STAT_CHANGE = r"(?P<opposing>The opposing )?(?P<poke>.+?)'s (?P<ability>.+?) (?P<modifier>%s)?(?P<direction>%s) its (?P<stat>%s)!" % (STAT_MODIFIER, ABILITY_STAT_DIRECTION, STATS)
MOVE_STAT_CHANGE = r"(?P<opposing2>The opposing )?(?P<poke2>.+?)'s (?P<stat2>%s) (?P<modifier2>%s)?(?P<direction2>%s)!" % (STATS, STAT_MODIFIER, MOVE_STAT_DIRECTION)

STAT_CHANGE = r'%s|%s' % (ABILITY_STAT_CHANGE, MOVE_STAT_CHANGE)
CRITICAL_HIT = r"(A critical hit! )"
DAMAGE_MODIFIER = "(It's not very effective... |It's super effective! )"

POKE_NAME = '((?P<pokename>[^ ]+?)|(?P<nickname>.+?) \((?P<pokename2>[^ ]+?)\))'

BATTLE_STARTED = r'Battle between (.*?) and (.*?) started!'
TEAM = r"(?P<username>.+?)'s team:"
POKES = r"(.+?) / (.+?) / (.+?)"
MY_SWITCH = r'Go! %s!' % POKE_NAME
OPP_SWITCH = r'.+? sent out %s!' % POKE_NAME
MOVE = r'(?P<opposing>The opposing )?(?P<poke>.+?) used (?P<move>.+?)!'
MEGA_EVOLVE = r"(?P<opposing>The opposing )?(?P<poke>.+?) has Mega Evolved into Mega (?P<mega>.+?)!"
TURN = r'Turn (.+?)'
LOST_ITEM = r".+? knocked off (?P<opposing>the opposing )?(?P<poke>.+?)'s .+?!"
DAMAGE = r"%s?%s?(?P<opposing>The opposing )?(?P<poke>.+?) lost (?P<damage>[0-9]+(\.[0-9]+)?)%% of its health!" % (DAMAGE_MODIFIER, CRITICAL_HIT)
FAINTED = r'(?P<opposing>The opposing )?(?P<poke>.+?) fainted!'
GAIN_HEALTH = r'(?P<opposing>The opposing )?(?P<poke>.+?) regained health!'
LEFTOVERS = r'(?P<opposing>The opposing )?(?P<poke>.+?) restored a little HP using its (?P<item>.+?)!'
LEECH_SEED = r"(?P<opposing>The opposing )?(?P<poke>.+?)'s health is sapped by Leech Seed!"
ROCKS = r"Pointed stones float in the air around (?P<opposing>your|the opposing) team!"
SPIKES = r"Spikes were scattered all around the feet of (?P<opposing>your|the opposing) team!"
ROCKS_GONE = r"The pointed stones disappeared from around (?P<opposing>your|the opposing )? team!"
BURN = r"(?P<opposing>The opposing )?(?P<poke>.+?) was burned!"
PARALYZE = r"(?P<opposing>The opposing )?(?P<poke>.+?) was paralyzed! It may be unable to move!"
HURT_BURN = r"(?P<opposing>The opposing )?(?P<poke>.+?) was hurt by its burn!"
FLOAT_BALLOON = r"(?P<opposing>The opposing )?(?P<poke>.+?) floats in the air with its Air Balloon!"
DRAGGED_OUT = r"(?P<opposing>The opposing )?(?P<nickname>.+?) (\((?P<poke>.+?)\))? was dragged out!"
POP_BALLOON = r"(?P<opposing>The opposing )?(?P<poke>.+?)'s Air Balloon popped!"
NEW_ITEM = r"(?P<opposing>The opposing )?(?P<poke>.+?) obtained one (?P<item>.+)."
BELLY_DRUM = r"(?P<opposing>The opposing )?(?P<poke>.+?) cut its own HP and maximized its Attack!"
MOLD_BREAKER = r"(?P<opposing>The opposing )?(?P<poke>.+?) breaks the mold!"
LIFE_ORB = r"(?P<opposing>The opposing )?(?P<poke>.+?) lost some of its HP!"
TAUNT = r"(?P<opposing>The opposing )?(?P<poke>.+?) fell for the taunt!"
ENCORE = r"(?P<opposing>The opposing )?(?P<poke>.+?) received an encore!"
DISABLED = r"(?P<opposing>The opposing )?(?P<poke>.+?)'s (?P<move>.+?) was disabled!"
NOT_DISABLED = r"(?P<opposing>The opposing )?(?P<poke>.+?) is disabled no more!"
IS_OVER = r"(?P<username>.+?) won the battle!"
DISCONNECTED = r".+? disconnected and has a minute to reconnect!"
LADDER = r"(?P<username>.+?)'s rating: .+? (?P<ladder>\d+)"
class SimulatorLog():

    def __init__(self):
        self.events = []
        self.event_count = 0
        self.nicknames = [{}, {}]
        self.detected_team = (False, None)

    def __iter__(self):
        return iter(self.events)

    def handle_line(self, line, my_poke=None, opp_poke=None):
        event = {}
        line = line.strip()

        if self.detected_team[0]:
            self.event_count += 1
            event['type'] = 'team'
            event['index'] = self.event_count
            event['player'] = 0
            event['poke'] = None
            team = [poke.strip() for poke in line.split("/")]
            event['details'] = {'team': team, 'username': self.detected_team[1]}
            self.detected_team = (False, None)
            return SimulatorEvent.from_dict(event)


        match = re.match(TEAM, line)
        if match:
            self.event_count += 1
            event['type'] = 'team_detect'
            event['index'] = self.event_count
            username = match.group('username')
            event['player'] = 0
            event['poke'] = None
            details = {'username': username}
            event['details'] = details
            self.detected_team = (True, username)
            return SimulatorEvent.from_dict(event)

        match = re.match(STAT_CHANGE, line)
        if match:
            details = {}
            if match.group('ability'):
                poke = match.group('poke')
                player = 1 if match.group('opposing') is not None else 0
                poke = self.nicknames[player][poke]
                modifier = match.group('modifier')
                stat = match.group('stat')
                direction = match.group('direction')
            else:
                poke = match.group('poke2')
                player = 1 if match.group('opposing2') is not None else 0
                poke = self.nicknames[player][poke]
                modifier = match.group('modifier2')
                stat = match.group('stat2')
                direction = match.group('direction2')
            event['player'] = player
            modifier = modifier.strip() if modifier is not None else modifier
            event['poke'] = poke
            details['stat'] = stat_map[stat]
            details['stages'] = modifier_map[modifier] * direction_map[direction]
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'stat_change'
            event['details'] = details
            return SimulatorEvent.from_dict(event)



        match = re.match(DAMAGE, line)
        if match:
            self.event_count += 1
            event['type'] = 'damage'
            event['index'] = self.event_count
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            damage = float(match.group('damage'))
            event['player'] = player

            event['poke'] = poke
            details = {'damage': damage}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(MOVE, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'move'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            move = match.group('move')
            event['player'] = player
            event['poke'] = poke
            details = {'move': move}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(FAINTED, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'faint'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(GAIN_HEALTH, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'regain_health'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(LEFTOVERS, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'leftovers'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(LIFE_ORB, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'life_orb'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(TAUNT, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'taunt'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(ENCORE, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'encore'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(DISABLED, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'disabled'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {'move': match.group('move')}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(NOT_DISABLED, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'not_disabled'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(BURN, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'burn'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(PARALYZE, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'paralyze'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(HURT_BURN, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'hurt_burn'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(FLOAT_BALLOON, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'float_balloon'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(NEW_ITEM, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'new_item'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {'item': match.group('item')}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(LOST_ITEM, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'lost_item'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(POP_BALLOON, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'pop_balloon'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(LEECH_SEED, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'leech_seed'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(DISCONNECTED, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'disconnected'
            details = {}
            event['details'] = details
            event['player'] = None
            event['poke'] = None
            return SimulatorEvent.from_dict(event)

        match = re.match(IS_OVER, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'over'
            username = match.group('username')
            details = {'username': username}
            event['details'] = details
            event['player'] = None
            event['poke'] = None
            return SimulatorEvent.from_dict(event)

        match = re.match(ROCKS, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'rocks'
            player = 1 if match.group('opposing') != "your" else 0
            event['player'] = player
            event['poke'] = None
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(SPIKES, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'spikes'
            player = 1 if match.group('opposing') != "your" else 0
            event['player'] = player
            event['poke'] = None
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(ROCKS_GONE, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'rocks_gone'
            player = 1 if match.group('opposing') != "your" else 0
            event['player'] = player
            event['poke'] = None
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(BELLY_DRUM, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'belly_drum'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(OPP_SWITCH, line)
        if match:
            if match.group('nickname'):
                self.nicknames[1][match.group('nickname')] = match.group('pokename2')
            else:
                self.nicknames[1][match.group('pokename')] = match.group('pokename')
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'switch'
            poke = match.group('pokename') or match.group('pokename2')
            event['player'] = 1
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(MY_SWITCH, line)
        if match:
            if match.group('nickname'):
                self.nicknames[0][match.group('nickname')] = match.group('pokename2')
            else:
                self.nicknames[0][match.group('pokename')] = match.group('pokename')
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'switch'
            poke = match.group('pokename') or match.group('pokename2')
            event['player'] = 0
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(DRAGGED_OUT, line)
        if match:
            self.event_count += 1
            player = 1 if match.group('opposing') is not None else 0
            event['index'] = self.event_count
            event['type'] = 'switch'
            if match.group('poke'):
                self.nicknames[0][match.group('nickname')] = match.group('poke')
            nickname = match.group('nickname')
            poke = self.nicknames[player][nickname]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(MOLD_BREAKER, line)
        if match:
            self.event_count += 1
            player = 1 if match.group('opposing') is not None else 0
            event['index'] = self.event_count
            event['type'] = 'mold_breaker'
            poke = match.group('poke')
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(MEGA_EVOLVE, line)
        if match:
            self.event_count += 1
            index = self.event_count
            type = "mega_evolve"
            poke = match.group('poke')
            mega = match.group('mega')
            mega = mega.split()
            player = 1 if match.group('opposing') is not None else 0
            old_poke = poke

            if poke not in self.nicknames[player]:
                player = 1 - player
            poke = self.nicknames[player][poke]
            event['player'] = player
            details = {}
            event['index'] = index
            event['type'] = type
            event['details'] = details
            event['poke'] = poke
            mega_name = None
            if player == 1:
                if opp_poke == "charizard-mega-x":
                    mega_name = "Charizard-Mega-X"
                elif opp_poke == "charizard-mega-y":
                    mega_name = "Charizard-Mega-Y"
                elif opp_poke == "mewtwo-mega-x":
                    mega_name = "Mewtwo-Mega-X"
                elif opp_poke == "mewtwo-mega-y":
                    mega_name = "Mewtwo-Mega-Y"
                else:
                    mega_name = self.nicknames[player][old_poke] + "-Mega"
            if player == 0:
                if my_poke == "charizard-mega-x":
                    mega_name = "Charizard-Mega-X"
                elif my_poke == "charizard-mega-y":
                    mega_name = "Charizard-Mega-Y"
                elif my_poke == "mewtwo-mega-x":
                    mega_name = "Mewtwo-Mega-X"
                elif my_poke == "mewtwo-mega-y":
                    mega_name = "Mewtwo-Mega-Y"
                else:
                    mega_name = self.nicknames[player][old_poke] + "-Mega"
            self.nicknames[player][old_poke] = mega_name
            event['details']['mega'] = mega_name
            return SimulatorEvent.from_dict(event)

        match = re.match(LADDER, line)
        if match:
            self.event_count += 1
            event['type'] = 'ladder'
            event['index'] = self.event_count
            username = match.group('username')
            event['player'] = 0
            event['poke'] = None
            details = {'username': username, 'ladder': match.group("ladder")}
            event['details'] = details
            self.detected_team = (True, username)
            return SimulatorEvent.from_dict(event)

    def add_event(self, line, my_poke=None, opp_poke=None):
        event = self.handle_line(line, my_poke=my_poke, opp_poke=opp_poke)
        if event:
            self.events.append(event)
        return event

    def is_over(self):
        for event in self.events:
            if event.type == "over":
                return True, event
        return False, None

    def disconnected(self):
        for event in self.events:
	    if event.type == "disconnected":
	        return True
	return False

    def reset(self):
        self.events = []
        self.event_count = 0
        self.nicknames = [{}, {}]

    @staticmethod
    def parse(text):
        log = SimulatorLog()
        for line in text.split('\n'):
            log.add_event(line)
        return log

class SimulatorEvent():
    def __init__(self, index, type, player, poke, details):
        self.index = index
        self.type = type
        self.player = player
        self.poke = poke
        self.details = details

    def __repr__(self):
        return "Event(%s, %s, %s, %s)" % (self.type, self.player, self.poke, self.details)

    @staticmethod
    def from_dict(dictionary):
        return SimulatorEvent(
            dictionary['index'],
            dictionary['type'],
            dictionary['player'],
            dictionary['poke'],
            dictionary['details']
        )

if __name__ == "__main__":
    from argparse import ArgumentParser
    argparser = ArgumentParser()
    argparser.add_argument('team1')
    argparser.add_argument('team2')

    args = argparser.parse_args()

    import json
    from smogon import Smogon
    from team import Team
    from gamestate import GameState
    with open('log.txt', 'r') as fp:
        log_text = fp.read()

    log = SimulatorLog.parse(log_text)

    with open(args.team1) as f1, open(args.team2) as f2, open("data/poke2.json") as f3:
        data = json.loads(f3.read())
        poke_dict = Smogon.convert_to_dict(data)
        teams = [Team.make_team(f1.read(), poke_dict), Team.make_team(f2.read(), poke_dict)]

    gamestate = GameState(teams)

    from simulator import Simulator
    simulator = Simulator()
    for event in log.events:
        simulator.handle_event(gamestate, event)
