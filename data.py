import json

POKEMON_DATA = 'data/pokemon.json'

TYPE_MAP = {
    0: "Normal",
    1: "Fire",
    2: "Water",
    3: "Electric",
    4: "Grass",
    5: "Ice",
    6: "Fighting",
    7: "Poison",
    8: "Ground",
    9: "Flying",
    10: "Psychic",
    11: "Bug",
    12: "Rock",
    13: "Ghost",
    14: "Dragon",
    15: "Dark",
    16: "Steel",
    17: "Fairy"
}

def load_pokemon():
    with open('data/pokemon.json', 'r') as fp:
        pokedata = json.loads(unicode(fp.read(), "ISO-8859-1"))
    new_pokedata = {}
    for pokemon in pokedata:
        name = pokemon["Name"]
        new_pokedata[name] = {}
        new_pokedata[name]["base_stats"] = {
            "attack" : pokemon["BaseStats"]["Attack"],
            "spattack" : pokemon["BaseStats"]["SpecialAttack"],
            "defense" : pokemon["BaseStats"]["Defense"],
            "spdefense" : pokemon["BaseStats"]["SpecialDefense"],
            "speed" : pokemon["BaseStats"]["Speed"],
            "hp" : pokemon["BaseStats"]["HP"]
        }
        new_pokedata[name]["type"] = set([TYPE_MAP[x] for x in pokemon["Types"]])
    return new_pokedata

if __name__ == "__main__":
    pokemon = load_pokemon()

