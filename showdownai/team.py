import smogon
import json
import re
from mega_items import mega_items
from math import floor

import logging
logging.basicConfig()



class Pokemon():
    def __init__(self, name, typing, stats, moveset, predictor, alive=True, status=None, calculate=False, is_mega=False, old_typing=None, taunt=False, disabled=None, last_move=None, encore=False):
        self.name = name
        self.typing = typing
        if old_typing is not None:
            self.old_typing = old_typing
        else:
            self.old_typing = typing
        self.predictor = predictor
        self.moveset = moveset
        self.final_stats = {}
        self.item = moveset.item
        self.status = status
        self.taunt = taunt
        self.disabled = disabled
        self.last_move = last_move
        self.encore = encore
        self.is_mega = is_mega
        self.ability = moveset.ability
        self.alive = alive
        self.choiced = False
        self.stats = stats
        self.stages = {
            'patk': 0,
            'spatk': 0,
            'pdef': 0,
            'spdef': 0,
            'spe': 0,
            'acc': 0,
            'eva': 0
        }
        if calculate:
            self.set_stats(stats)
            self.health = self.final_stats['hp']

    def damage(self, amount):
        self.health = floor(max(0, self.health - amount))

    def damage_percent(self, percent):
        damage = percent * self.final_stats['hp']
        self.health = floor(max(0, self.health - damage))
        return damage

    def heal(self, percent):
        self.health = floor(min(self.final_stats['hp'], self.health + percent * self.final_stats['hp']))

    def get_stat(self, stat_name):
        return self.final_stats[stat_name]

    def set_stats(self, stats):
        self.stats = stats
        for stat_name, value in self.stats.items():
            if stat_name != 'hp':
                self.final_stats[stat_name] = floor(floor((2 * value + 31 + self.moveset.evs[stat_name] / 4.0) + 5) * self.moveset.nature[stat_name])
            else:
                self.final_stats[stat_name] = floor((2 * value + 31 + self.moveset.evs[stat_name] / 4.0) + 110)

    def get_stage(self, stat):
        return self.stages[stat]

    def increase_stage(self, stat, amount):
        assert amount > 0
        self.stages[stat] = min(6, self.stages[stat] + amount)

    def decrease_stage(self, stat, amount):
        assert amount > 0
        self.stages[stat] = max(-6, self.stages[stat] - amount)
        if self.ability == "Defiant":
            logging.debug("%s has Defiant and sharply increased attack." % self)
            self.increase_stage('patk', 2)
        elif self.ability == "Competitive":
            self.increase_stage('spatk', 2)
            logging.debug("%s has Competitive and sharply increased special attack." % self)

    def meloetta_evolve(self):
        assert self.name == "Meloetta"
        if "Psychic" in self.typing:
            stats = {
                "hp": 100,
                "patk": 128,
                "pdef": 90,
                "spatk": 77,
                "spdef": 77,
                "spe": 128
            }
            typing = ['Normal', 'Fighting']
        elif "Fighting" in self.typing:
            stats = {
                "hp": 100,
                "patk": 77,
                "pdef": 77,
                "spatk": 128,
                "spdef": 128,
                "spe": 90
            }
            typing = ['Normal', 'Psychic']
        self.set_stats(stats)
        self.typing = typing

    def meloetta_reset(self):
        stats = {
            "hp": 100,
            "patk": 77,
            "pdef": 77,
            "spatk": 128,
            "spdef": 128,
            "spe": 90
        }
        self.set_stats(stats)
        self.typing = ['Normal', 'Psychic']

    def reset_stages(self):
        self.stages = {
            'patk': 0,
            'spatk': 0,
            'pdef': 0,
            'spdef': 0,
            'spe': 0,
            'acc': 0,
            'eva': 0
        }

    def reset_typing(self):
        self.typing = self.old_typing

    def set_status(self, status):
        if self.status is None:
            self.status = status

    def set_last_move(self, move):
        self.last_move = move

    def set_encore(self, encore):
        self.encore = encore

    def set_disabled(self, move):
        self.disabled = move

    def set_taunt(self, taunt):
        self.taunt = taunt

    def reset_taunt(self):
        self.set_taunt(False)

    def reset_status(self):
        self.set_status(None)

    def reset_disabled(self):
        self.set_disabled(None)

    def reset_last_move(self):
        self.set_last_move(None)

    def reset_encore(self):
        self.set_encore(False)

    def can_evolve(self):
        if self.is_mega:
            return False
        if self.item in mega_items:
            if self.name == mega_items[self.item][0]:
                return True
        return False

    def mega_evolve(self, pokedata, log=False):
        if self.can_evolve():
            name = mega_items[self.item][1]
            mega_poke = pokedata.mega_data[name]
            typing = mega_poke.typing
            stats = mega_poke.stats
            ability = mega_poke.movesets[0]['ability']
            moveset = smogon.SmogonMoveset(self.moveset.name, None, ability, self.moveset.evs, self.moveset.nature, self.moveset.moves, tag=self.moveset.tag)
            status = self.status
            disabled = self.disabled
            taunt = self.taunt
            last_move = self.last_move
            encore = self.last_move
            poke = Pokemon(name, typing, stats, moveset, self.predictor, status=status, old_typing=None, calculate=True, is_mega=True, taunt=taunt, disabled=disabled, last_move=last_move, encore=encore)
            poke.health = self.health
            if log:
                print "%s mega evolved into %s." % (
                    self,
                    poke
                )
            return poke
        return self

    def predict_moves(self, known_moves):
        return self.predictor(known_moves)

    def copy(self):
        poke = Pokemon(self.name, self.typing[:],
                       self.stats, self.moveset, self.predictor,
                       status=self.status, taunt=self.taunt, disabled=self.disabled, last_move=self.last_move, encore=self.encore, alive=self.alive,
                       calculate=False, old_typing=self.old_typing)
        poke.final_stats = self.final_stats
        poke.health = self.health
        poke.ability = self.ability
        poke.item = self.item
        poke.stages = self.stages.copy()
        poke.is_mega = self.is_mega
        poke.choiced = self.choiced
        if self.choiced:
            poke.move_choice = self.move_choice
        return poke
    def to_tuple(self):
        return (self.name, self.item, self.health, tuple(self.typing), self.status, self.taunt, self.disabled, self.last_move, self.encore, tuple(self.stages.values()))

    def __repr__(self):
        return "%s(%u)" % (self.name, self.health)

class Team():
    def __init__(self, poke_list):
        self.poke_list = poke_list
        self.primary_poke = 0

    def copy(self):
        team = Team([p.copy() for p in self.poke_list])
        team.primary_poke = self.primary_poke
        return team

    def to_tuple(self):
        return (self.primary_poke, tuple(x.to_tuple() for x in self.poke_list))

    @staticmethod
    def from_tuple(tupl):
        team = Team(poke.from_tuple() for poke in tupl[1])
        team.primary_poke = tupl[0]
        return team

    def primary(self):
        if self.primary_poke is None:
            return None
        return self.poke_list[self.primary_poke]

    def set_primary(self, primary):
        if primary is None:
            self.primary_poke = None
            return
        self.primary_poke = primary
        self.primary().choiced = False
        self.primary().reset_stages()

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
            if tl.strip() == "":
                continue
            line = tl.strip().split('\n')
            if "(M)" in line[0]:
                line[0] = line[0].replace(" (M)", "")
            if "(F)" in line[0]:
                line[0] = line[0].replace(" (F)", "")
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
            moveset = smogon.SmogonMoveset(name, item, ability, evs, nature, moves, tag=None)
            typing = data[name].typing
            stats = data[name].stats
            poke = Pokemon(name, typing, stats, moveset, None, calculate=True)
            poke_list.append(poke)
        return Team(poke_list)

    def alive(self):
        alive = False
        for poke in self.poke_list:
            alive = alive or poke.alive
            if alive:
                return alive
        return alive
if __name__ == "__main__":
    import json
    with open("data/poke2.json") as f:
        data = json.loads(f.read())
    import smogon
    poke_dict = smogon.Smogon.convert_to_dict(data)
    poke = poke_dict['Infernape']
    print poke
    print poke.movesets[0]
    moveset = smogon.SmogonMoveset.from_dict(poke.movesets[0])
    print moveset.ability

