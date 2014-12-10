import smogon
import json
import re

from math import floor

class Pokemon():
    def __init__(self, name, typing, stats, moveset, alive=True, status=None, backup_switch=""):
        self.name = name
        self.typing = typing
        self.stats = stats
        self.moveset = moveset
        self.final_stats = {}
        self.alive = alive
        self.item = moveset.item
        self.status = status
        self.backup_switch = backup_switch
        self.stages = {
            'patk': 0,
            'spatk': 0,
            'pdef': 0,
            'spdef': 0,
            'spe': 0,
            'acc': 0,
            'eva': 0
        }
        for stat_name, value in self.stats.items():
            if stat_name != 'hp':
                self.final_stats[stat_name] = floor(floor((2 * value + 31 + moveset.evs[stat_name] / 4.0) + 5) * moveset.nature[stat_name])
            else:
                self.final_stats[stat_name] = floor((2 * value + 31 + moveset.evs[stat_name] / 4.0) + 110)
        self.health = self.final_stats['hp']

    def get_stat(self, stat_name):
        return self.final_stats[stat_name]

    def set_status(self, status):
        print self.name, "got", status
        self.status = status

    def copy(self):
        poke = Pokemon(self.name, list(self.typing), self.stats, self.moveset)
        poke.health = self.health
        poke.alive = self.alive
        poke.item = self.item
        poke.stages = self.stages
        return poke

    def __repr__(self):
        return "%s(%f, %s)" % (self.name, self.health, self.item)

class Team():
    def __init__(self, poke_list):
        self.poke_list = poke_list
        self.primary_poke = 0

    def copy(self):
        team = Team([p.copy() for p in self.poke_list])
        team.primary_poke = self.primary_poke
        return team

    def primary(self):
        return self.poke_list[self.primary_poke]

    def __getitem__(self, index):
        return self.poke_list.__getitem__(index)

    def __repr__(self):
        return "[" + ', '.join([repr(x) for x in self.poke_list]) + "]"

    @staticmethod
    def convert_nature(nature):
        nature_dict = {"hp": 1.0, "patk": 1.0, "pdef": 1.0, "spatk": 1.0, "spdef": 1.0, "spe": 1.0}
        if nature == "Lonely":
            nature_dict['patk'] = 1.1
            nature_dict['pdef'] = 0.9
        elif nature == "Brave":
            nature_dict['patk'] = 1.1
            nature_dict['spe'] = 0.9
        elif nature == "Adamant":
            nature_dict['patk'] = 1.1
            nature_dict['spatk'] = 0.9
        elif nature == "Naughty":
            nature_dict['patk'] = 1.1
            nature_dict['spdef'] = 0.9
        elif nature == "Bold":
            nature_dict['pdef'] = 1.1
            nature_dict['patk'] = 0.9
        elif nature == "Relaxed":
            nature_dict['pdef'] = 1.1
            nature_dict['spe'] = 0.9
        elif nature == "Impish":
            nature_dict['pdef'] = 1.1
            nature_dict['spatk'] = 0.9
        elif nature == "Lax":
            nature_dict['pdef'] = 1.1
            nature_dict['spdef'] = 0.9
        elif nature == "Timid":
            nature_dict['spe'] = 1.1
            nature_dict['patk'] = 0.9
        elif nature == "Hasty":
            nature_dict['spe'] = 1.1
            nature_dict['pdef'] = 0.9
        elif nature == "Jolly":
            nature_dict['spe'] = 1.1
            nature_dict['spatk'] = 0.9
        elif nature == "Naive":
            nature_dict['spe'] = 1.1
            nature_dict['spdef'] = 0.9
        elif nature == "Modest":
            nature_dict['spatk'] = 1.1
            nature_dict['patk'] = 0.9
        elif nature == "Mild":
            nature_dict['spatk'] = 1.1
            nature_dict['pdef'] = 0.9
        elif nature == "Quiet":
            nature_dict['spatk'] = 1.1
            nature_dict['spe'] = 0.9
        elif nature == "Rash":
            nature_dict['spatk'] = 1.1
            nature_dict['spdef'] = 0.9
        elif nature == "Calm":
            nature_dict['spdef'] = 1.1
            nature_dict['patk'] = 0.9
        elif nature == "Gentle":
            nature_dict['spdef'] = 1.1
            nature_dict['pdef'] = 0.9
        elif nature == "Sassy":
            nature_dict['spdef'] = 1.1
            nature_dict['spe'] = 0.9
        elif nature == "Careful":
            nature_dict['spdef'] = 1.1
            nature_dict['spatk'] = 0.9
        return nature_dict

    @staticmethod
    def make_team(text, data):
        poke_list = []
        text_lines = text.split("\n\n")[:6]
        for tl in text_lines:
            line = tl.split('\n')
            match = re.search(r'(.+?)\s*(\((.+?)\))?\s*(@ (.+?))?$', line[0])
            nickname = match.group(1)
            name = match.group(3)
            item = match.group(5)
            if name is None:
                name = nickname
            ability = line[1][9:]
            moves = [x[2:] for x in line[4:]]
            ev_list = line[2].split("/")
            ev_list[0] = ev_list[0][4:]
            evs = {'spatk': 0, 'pdef': 0, 'hp': 0, 'spdef': 0, 'patk': 0, 'spe': 0}
            for ev in ev_list:
                if 'HP' in ev:
                    hp = int(''.join(s for s in ev if s.isdigit()))
                    evs['hp'] = hp
                if 'Atk' in ev:
                    patk = int(''.join(s for s in ev if s.isdigit()))
                    evs['patk'] = patk
                if 'Def' in ev:
                    pdef = int(''.join(s for s in ev if s.isdigit()))
                    evs['pdef'] = pdef
                if 'SpA' in ev:
                    spa = int(''.join(s for s in ev if s.isdigit()))
                    evs['spatk'] = spa
                if 'SpD' in ev:
                    spd = int(''.join(s for s in ev if s.isdigit()))
                    evs['spdef'] = spd
                if 'Spe' in ev:
                    spe = int(''.join(s for s in ev if s.isdigit()))
                    evs['spe'] = spe
            nature = line[3][:-7]
            nature = Team.convert_nature(nature)
            moveset = smogon.SmogonMoveset(name, item, ability, evs, nature, moves)
            typing = data[name].typing
            stats = data[name].stats
            poke = Pokemon(name, typing, stats, moveset)
            poke_list.append(poke)
        return Team(poke_list)

with open('data/poke.json') as f:
    data = json.loads(f.read())
    poke_dict = smogon.Smogon.convert_to_dict(data)
    with open("pokemon_team2.txt", "r") as f:
        team_text = f.read()
        pokes = Team.make_team(team_text, poke_dict)
