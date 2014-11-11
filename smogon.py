import requests
import json

class Smogon():
    BASE_URL = "http://www.smogon.com/dex/api/query"
    def __init__(self):
        self.url = self.BASE_URL

    def get_all_pokemon(self):
        fields = ["name", "alias"]
        query = {"pokemonalt":{"gen":"xy"}, "$": fields}
        params = {"q": json.dumps(query)}
        output = requests.get(self.url, params=params)
        output = output.json()
        names = output['result']
        poke_names = []
        for name in names:
            poke_names.append(name['alias'])
        return poke_names

    def get_pokemon_info(self, pokemon):
        moveset_fields = ["name", "alias", {"movesets":["name",
                                                {"items":["alias","name"]},
                                                {"abilities":["alias","name","gen"]},
                                                {"evconfigs":["hp","patk","pdef","spatk","spdef","spe"]},
                                                {"natures":["hp","patk","pdef","spatk","spdef","spe"]},
                                                {"$groupby":"slot","moveslots":["slot",{"move":["name","alias","gen"]}]},"description"]},{"moves":["name","alias","gen","category","power","accuracy","pp","description",{"type":["alias","name","gen"]}]}
                                                ]
        moveset_query = {"pokemon":{"gen":"xy","alias":"%s" % pokemon}, "$": moveset_fields}
        moveset_params = {"q": json.dumps(moveset_query)}
        moveset_output = requests.get(self.url, params=moveset_params)
        moveset_output = moveset_output.json()
        meta_fields = ["name","alias","gen",{"types":["alias","name","gen"]}, {"abilities":["alias","name","gen"]}]
        meta_query = {"pokemonalt":{"gen":"xy","alias":"%s" % pokemon}, "$": meta_fields}
        meta_params = {"q": json.dumps(meta_query)}
        meta_output = requests.get(self.url, params=meta_params)
        meta_output = meta_output.json()
        return pokemon, meta_output, moveset_output

    def convert_to_pokemon(self, pokemon, meta_output, moveset_output):
        moveset_results = moveset_output['result']
        movesets = moveset_results[0]['movesets']
        poke_movesets = []
        meta_results = meta_output['result']
        abilities = meta_results[0]['abilities']
        for moveset in movesets:
            if len(moveset['abilities']) != 0:
                ability = moveset['abilities'][0]['alias']
            else:
                ability = abilities[0]['alias']
            name = moveset['name']
            if len(moveset['items']) != 0:
                item = moveset['items'][0]['alias']
            else:
                item = ""
            evs = moveset['evconfigs'][0]
            moveslots = moveset['moveslots']
            nature = moveset['natures'][0]
            moves = []
            for moveslot in moveslots:
                for move in moveslot['moves']:
                    moves.append(move['alias'])
            moves = moves
            poke_moveset = SmogonMoveset(name, item, ability, evs, nature, moves)
            poke_movesets.append(poke_moveset)
        type_list = []
        types = meta_results[0]['types']
        for poke_type in types:
            type_list.append(poke_type['alias'])
        poke = SmogonPokemon(pokemon, type_list, poke_movesets)
        return poke


class SmogonPokemon():
    def __init__(self, name, typing, movesets):
        self.name = name
        self.typing = typing
        self.movesets = movesets
    def to_dict(self):
        dictionary = {'name': self.name, 'typing': self.typing, 'movesets': [moveset.to_dict() for moveset in self.movesets]}
        return dictionary
    def set_name(self, name):
        self.name = name
    def set_typing(self, typing):
        self.typing = typing
    def set_movesets(self, movesets):
        self.movesets = movesets

    @staticmethod
    def from_dict(dictionary):
        return SmogonPokemon(dictionary['name'], dictionary['typing'], )

poke = SmogonPokemon.from_dict(dictionary)

class SmogonMoveset():
    def __init__(self, name, item, ability, evs, nature, moves):
        self.name = name
        self.item = item
        self.ability = ability
        self.evs = evs
        self.nature = nature
        self.moves = moves
    def to_dict(self):
        dictionary = {'name': self.name, 'item': self.item, 'ability': self.ability, 'evs': self.evs, 'nature': self.nature, 'moves': self.moves}
        return dictionary
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

class Move():
    def __init__(self, name, typing, power, accuracy):
        self.name = name
        self.typing = typing
        self.power = power
        self.accuracy = accuracy

if __name__ == "__main__":
    smogon = Smogon()
    pokes = smogon.get_all_pokemon()
    poke_objects = []
    for poke in pokes:
        try:
            print poke
            poke, typing, movesets = smogon.get_pokemon_info(poke)
            poke_obj = smogon.convert_to_pokemon(poke, typing, movesets)
            poke_objects.append(poke_obj.to_dict())
        except IndexError:
            print "error: " + poke
    with open('poke.json', 'w') as f:
        f.write(json.dumps(poke_objects, sort_keys=True,indent=4, separators=(',', ': ')))

