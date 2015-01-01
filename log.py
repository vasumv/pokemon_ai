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

POKE_NAME = '((?P<pokename>[^ ]+?)|(?P<nickname>.+?) \((?P<pokename2>[^ ]+?)\))'

BATTLE_STARTED = r'Battle between (.*?) and (.*?) started!'

MY_SWITCH = r'Go! %s!' % POKE_NAME
OPP_SWITCH = r'.+? sent out %s!' % POKE_NAME
MOVE = r'(?P<opposing>The opposing )?(?P<poke>.+?) used (?P<move>.+?)!'
MEGA_EVOLVE = r"(?P<opposing>The opposing )?(?P<poke>.+?) has Mega Evolved into Mega (?P<mega>.+?)!"
TURN = r'Turn (.+?)'
OPP_KNOCK_OFF = r"The opposing (.+?) knocked off (.+?)'s (.+?)!"
DAMAGE = r'(.*[\.!] )?(?P<opposing>The opposing )?(?P<poke>.+?) lost (?P<damage>[0-9]+(\.[0-9]+)?)% of its health!'
FAINTED = r'(?P<opposing>The opposing )?(?P<poke>.+?) fainted!'
GAIN_HEALTH = r'(?P<opposing>The opposing )?(?P<poke>.+?) regained health!'
LEFTOVERS = r'(?P<opposing>The opposing )?(?P<poke>.+?) restored a little HP using its (?P<item>.+?)!'
LEECH_SEED = r"(?P<opposing>The opposing )?(?P<poke>.+?)'s health is sapped by Leech Seed!"
ROCKS = r"Pointed stones float in the air around (?P<opposing>your|the opposing) team!"
BURN = r"(?P<opposing>The opposing )?(?P<poke>.+?) was burned!"
HURT_BURN = r"(?P<opposing>The opposing )?(?P<poke>.+?) was hurt by its burn!"
FLOAT_BALLOON = r"(?P<opposing>The opposing )?(?P<poke>.+?) floats in the air with its Air Balloon!"
POP_BALLOON = r"(?P<opposing>The opposing )?(?P<poke>.+?)'s Air Balloon popped!"
NEW_ITEM = r"(?P<opposing>The opposing )?(?P<poke>.+?) obtained one (?P<item>.+?)."
class SimulatorLog():

    def __init__(self):
        self.events = []
        self.event_count = 0
        self.nicknames = [{}, {}]

    def __iter__(self):
        return iter(self.events)

    def handle_line(self, line):
        event = {}
        line = line.strip()

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
            event['type'] = 'leftovers'
            poke = match.group('poke')
            player = 1 if match.group('opposing') is not None else 0
            poke = self.nicknames[player][poke]
            event['player'] = player
            event['poke'] = poke
            details = {}
            event['details'] = details
            return SimulatorEvent.from_dict(event)

        match = re.match(ROCKS, line)
        if match:
            self.event_count += 1
            event['index'] = self.event_count
            event['type'] = 'rocks'
            player = 1 if match.group('opposing') is not None else 0
            event['player'] = player
            event['poke'] = None
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
            if len(mega) == 1:
                self.nicknames[player][old_poke] = self.nicknames[player][old_poke] + "-Mega"
            else:
                self.nicknames[player][old_poke] = self.nicknames[player][old_poke] + "-Mega"+mega[1]
            return SimulatorEvent.from_dict(event)

    def add_event(self, line):
        event = self.handle_line(line)
        if event:
            self.events.append(event)
        return event

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
