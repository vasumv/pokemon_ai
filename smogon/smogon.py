import requests
import json

class Smogon():
    BASE_URL = "http://www.smogon.com/dex/api/query"
    def __init__(self):
        self.url = self.BASE_URL

    @staticmethod
    def convert_to_dict(poke_list):
        poke_dict = {}
        for poke in poke_list:
            poke_dict[poke['name']] = SmogonPokemon.from_dict(poke)
        return poke_dict

    def get_all_pokemon(self):
        fields = ["name"]
        query = {"pokemonalt":{"gen":"bw"}, "$": fields}
        params = {"q": json.dumps(query)}
        output = requests.get(self.url, params=params)
        output = output.json()
        names = output['result']
        poke_names = []
        for name in names:
            poke_names.append(name['name'])
        return poke_names

    def get_pokemon_info(self, pokemon):
        moveset_fields = ["name", "alias", {"movesets":["name",
                                                {"tags":["alias","name"]},
                                                {"items":["alias","name"]},
                                                {"abilities":["alias","name","gen"]},
                                                {"evconfigs":["hp","patk","pdef","spatk","spdef","spe"]},
                                                {"natures":["hp","patk","pdef","spatk","spdef","spe"]},
                                                {"$groupby":"slot","moveslots":["slot",{"move":["name","alias","gen"]}]},"description"]},
                                                {"moves":["name","alias","gen","category","power","accuracy","pp","description",{"type":["alias","name","gen"]}]}
                                                ]
        moveset_query = {"pokemon":{"gen":"bw","name":"%s" % pokemon}, "$": moveset_fields}
        moveset_params = {"q": json.dumps(moveset_query)}
        moveset_output = requests.get(self.url, params=moveset_params)
        moveset_output = moveset_output.json()
        meta_fields = ["name","alias","gen",{"types":["alias","name","gen"]}, {"abilities":["alias","name","gen"]}, "hp", "patk", "pdef", "spatk", "spdef", "spe"]
        meta_query = {"pokemonalt":{"gen":"bw","name":"%s" % pokemon}, "$": meta_fields}
        meta_params = {"q": json.dumps(meta_query)}
        meta_output = requests.get(self.url, params=meta_params)
        meta_output = meta_output.json()
        return pokemon, meta_output, moveset_output

    def convert_to_pokemon(self, pokemon, meta_output, moveset_output):
        moveset_results = moveset_output['result']
        meta_results = meta_output['result']
        abilities = meta_results[0]['abilities']
        type_list = []
        types = meta_results[0]['types']
        poke_moves = []
        for move in moveset_results[0]['moves']:
            poke_moves.append(move['name'])
        for poke_type in types:
            type_list.append(poke_type['name'])
        if "-Mega" in pokemon:
            movesets = ""
        else:
            movesets = moveset_results[0]['movesets']
        poke_movesets = []
        stats = {}
        stats['hp'] = meta_results[0]['hp']
        stats['patk'] = meta_results[0]['patk']
        stats['pdef'] = meta_results[0]['pdef']
        stats['spatk'] = meta_results[0]['spatk']
        stats['spdef'] = meta_results[0]['spdef']
        stats['spe'] = meta_results[0]['spe']
        if "-Mega" not in pokemon:
            for moveset in movesets:
                tag = moveset['tags'][0]['name']
                if len(moveset['abilities']) != 0:
                    ability = moveset['abilities'][0]['name']
                else:
                    ability = abilities[0]['name']
                name = moveset['name']
                if len(moveset['items']) != 0:
                    item = moveset['items'][0]['name']
                else:
                    item = ""
                if len(moveset['evconfigs']) != 0:
                    evs = moveset['evconfigs'][0]
                else:
                    continue
                evs = moveset['evconfigs'][0]
                moveslots = moveset['moveslots']
                nature = moveset['natures'][0]
                moves = []
                for moveslot in moveslots:
                    for move in moveslot['moves']:
                        moves.append(move['name'])
                poke_moveset = SmogonMoveset(name, item, ability, evs, nature, moves, tag)
                poke_movesets.append(poke_moveset)
        else:
            ability = abilities[0]['name']
            poke_moveset = SmogonMoveset("","",ability,"","","")
            poke_movesets.append(poke_moveset)
        poke = SmogonPokemon(pokemon, type_list, stats, poke_movesets)
        return poke, poke_moves

class SmogonPokemon():
    def __init__(self, name, typing, stats, movesets):
        self.name = name
        self.typing = typing
        self.stats = stats
        self.movesets = movesets
    def to_dict(self):
        dictionary = {'name': self.name, 'typing': self.typing, 'stats': self.stats, 'movesets': [moveset.to_dict() for moveset in self.movesets]}
        return dictionary
    def set_name(self, name):
        self.name = name
    def set_typing(self, typing):
        self.typing = typing
    def set_stats(self, stats):
        self.stats = stats
    def set_movesets(self, movesets):
        self.movesets = movesets

    @staticmethod
    def from_dict(dictionary):
        return SmogonPokemon(dictionary['name'], dictionary['typing'], dictionary['stats'], dictionary['movesets'])

class SmogonMoveset():
    def __init__(self, name, item, ability, evs, nature, moves, tag):
        self.name = name
        self.item = item
        self.ability = ability
        self.evs = evs
        self.nature = nature
        self.moves = moves
        self.known_moves = []
        self.tag = tag
    def to_dict(self):
        dictionary = {'name': self.name, 'item': self.item, 'ability': self.ability, 'evs': self.evs, 'nature': self.nature, 'moves': self.moves, 'tag': self.tag}
        return dictionary
    @staticmethod
    def from_dict(dictionary):
        return SmogonMoveset(dictionary['name'], dictionary['item'], dictionary['ability'], dictionary['evs'], dictionary['nature'], dictionary['moves'], dictionary['tag'])
    def set_name(self, name):
        self.name = name
    def set_item(self, item):
        self.item = item
    def set_ability(self, ability):
        self.ability = ability
    def set_evs(self, evs):
        self.evs = evs
    def set_nature(self, nature):
        self.nature = nature
    def set_moves(self, moves):
        self.moves = moves

if __name__ == "__main__":
    smogon = Smogon()
    pokes = smogon.get_all_pokemon()
    poke_names = []
    poke_objects = []
    pokes_moves = {}
    #poke, typing, movesets = smogon.get_pokemon_info('Serperior')
    #poke_obj = smogon.convert_to_pokemon(poke, typing, movesets)[0]
    for poke in pokes:
        try:
            if "-Mega" not in poke:
                print poke
                poke, typing, movesets = smogon.get_pokemon_info(poke)
                poke_obj = smogon.convert_to_pokemon(poke, typing, movesets)[0]
                poke_objects.append(poke_obj.to_dict())
        except IndexError:
            print "error: " + poke
    with open('../data/poke2_bw.json', 'w') as f:
        f.write(json.dumps(poke_objects, sort_keys=True,indent=4, separators=(',', ': ')))
