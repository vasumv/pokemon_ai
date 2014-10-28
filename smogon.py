from bs4 import BeautifulSoup
import requests
import json
from pokemon import Pokemon
class Smogon():
    BASE_URL = "http://www.smogon.com/dex/api/query"
    def __init__(self):
        self.url = self.BASE_URL

    def get_pokemon(self, pokemon):
        fields = ["name", "alias", {"movesets":["name",
                                                {"items":["alias","name"]},
                                                {"abilities":["alias","name","gen"]},
                                                {"evconfigs":["hp","patk","pdef","spatk","spdef","spe"]},
                                                {"natures":["hp","patk","pdef","spatk","spdef","spe"]},
                                                {"$groupby":"slot","moveslots":["slot",{"move":["name","alias","gen"]}]},"description"]},{"moves":["name","alias","gen","category","power","accuracy","pp","description",{"type":["alias","name","gen"]}]}
                                                ]
        query = {"pokemon":{"gen":"xy","alias":"%s" % pokemon}, "$": fields}
        params = {"q": json.dumps(query)}
        output = requests.get(self.url, params=params)
        output = output.json()
        return output

    def convert_to_pokemon(self, pokemon_output):
        poke = Pokemon()
        results = pokemon_output['result']
        movesets = results[0]['movesets']
        for moveset in movesets:
            name = moveset['name']
            ability = moveset['abilities'][0]['alias']
            item = moveset['items'][0]['alias']
            evconfigs = moveset['evconfigs'][0]
            moveslots = moveset['moveslots']
            nature = moveset['natures'][0]
            for moveslot in moveslots:
                for move in moveslot['moves']:
                    print move['alias']
        #for moveset in movesets:
            #print moveset['name']


if __name__ == "__main__":
    smogon = Smogon()
    output = smogon.get_pokemon('abomasnow')
    smogon.convert_to_pokemon(output)

