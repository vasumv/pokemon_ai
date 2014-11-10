import requests
import json
from pokemon import Pokemon

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
        typing_fields = ["name","alias","gen",{"types":["alias","name","gen"]}]
        typing_query = {"pokemonalt":{"gen":"xy","alias":"%s" % pokemon}, "$": typing_fields}
        typing_params = {"q": json.dumps(typing_query)}
        typing_output = requests.get(self.url, params=typing_params)
        typing_output = typing_output.json()
        return typing_output, moveset_output

    def convert_to_pokemon(self, typing_output, moveset_output):
        moveset_results = moveset_output['result']
        movesets = moveset_results[0]['movesets']
        poke_movesets = []
        for moveset in movesets:
            name = moveset['name']
            ability = moveset['abilities'][0]['alias']
            item = moveset['items'][0]['alias']
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
        typing_results = typing_output['result']
        types = typing_results[0]['types']
        for poke_type in types:
            type_list.append(poke_type['alias'])
        poke = SmogonPokemon(type_list, poke_movesets)
        return poke


class SmogonPokemon():
    def __init__(self, typing, movesets):
        #self.name = name
        self.typing = typing
        self.movesets = movesets
    def to_dict(self):
        dictionary = {'typing': self.typing, 'movesets': [moveset.to_dict() for moveset in self.movesets]}
        return dictionary
    def set_name(self, name):
        self.name = name
    def set_typing(self, typing):
        self.typing = typing
    def set_movesets(self, movesets):
        self.movesets = movesets


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
    f = open("crashes.txt")
    crashes = f.read()
    f2 = open("autocrash.txt", "a")
    f2.write("Crashes: \n")
    smogon = Smogon()
    pokes = smogon.get_all_pokemon()
    poke_objects = []
    for poke in pokes:
        try:
            print poke
            typing, movesets = smogon.get_pokemon_info(poke)
            poke_obj = smogon.convert_to_pokemon(typing, movesets)
            poke_objects.append(poke_obj)
        except IndexError:
            f2.write(poke + "\n")
            continue
    f2.close()

    #typing, movesets = smogon.get_pokemon_info('infernape')
    #poke = smogon.convert_to_pokemon(typing, movesets)
    #poke_dict = poke.to_dict()
    #print poke_dict['movesets'][1]['ability']
    #poke = smogon.convert_to_pokemon(output)
    #print poke.movesets[0].nature
