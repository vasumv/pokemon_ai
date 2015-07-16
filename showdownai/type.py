multipliers = {
    "Normal": {
        "Fighting": 2.0,
        "Ghost": 0.0
    },
    "Fighting": {
        "Flying": 2.0,
        "Rock": 0.5,
        "Bug": 0.5,
        "Psychic": 2.0,
        "Dark": 0.5,
        "Fairy": 2.0
    },
    "Flying": {
        "Fighting": 0.5,
        "Ground": 0.0,
        "Rock": 2.0,
        "Bug": 0.5,
        "Grass": 0.5,
        "Electric": 2.0,
        "Ice": 2.0
    },
    "Poison": {
        "Fighting": 0.5,
        "Poison": 0.5,
        "Ground": 2.0,
        "Bug": 0.5,
        "Grass": 0.5,
        "Psychic": 2.0,
        "Fairy": 0.5
    },
    "Ground": {
        "Poison": 0.5,
        "Rock": 0.5,
        "Electric": 0.0,
        "Ice": 2.0,
        "Water": 2.0,
        "Grass": 2.0,
    },
    "Rock": {
        "Normal": 0.5,
        "Fighting": 2.0,
        "Flying": 0.5,
        "Poison": 0.5,
        "Ground": 2.0,
        "Steel": 2.0,
        "Fire": 0.5,
        "Water": 2.0,
        "Grass": 2.0,
    },
    "Bug": {
        "Fighting": 0.5,
        "Flying": 2.0,
        "Ground": 0.5,
        "Rock": 2.0,
        "Fire": 2.0,
        "Grass": 0.5
    },
    "Ghost": {
        "Normal": 0.0,
        "Fighting": 0.0,
        "Poison": 0.5,
        "Bug": 0.5,
        "Ghost": 2.0,
        "Dark": 2.0
    },
    "Steel": {
        "Normal": 0.5,
        "Fighting": 2.0,
        "Flying": 0.5,
        "Poison": 0.0,
        "Ground": 2.0,
        "Rock": 0.5,
        "Bug": 0.5,
        "Steel": 0.5,
        "Fire": 2.0,
        "Grass": 0.5,
        "Psychic": 0.5,
        "Ice": 0.5,
        "Dragon": 0.5,
        "Fairy": 0.5
    },
    "Fire": {
        "Ground": 2.0,
        "Rock": 2.0,
        "Bug": 0.5,
        "Steel": 0.5,
        "Fire": 0.5,
        "Water": 2.0,
        "Grass": 0.5,
        "Ice": 0.5,
        "Fairy": 0.5
    },
    "Water": {
        "Steel": 0.5,
        "Fire": 0.5,
        "Water": 0.5,
        "Grass": 2.0,
        "Electric": 2.0,
        "Ice": 0.5,
    },
    "Grass": {
        "Flying": 2.0,
        "Poison": 2.0,
        "Ground": 0.5,
        "Bug": 2.0,
        "Fire": 2.0,
        "Water": 0.5,
        "Grass": 0.5,
        "Electric": 0.5,
        "Ice": 2.0,
    },
    "Electric": {
        "Flying": 0.5,
        "Ground": 2.0,
        "Steel": 0.5,
        "Electric": 0.5
    },
    "Psychic": {
        "Fighting": 0.5,
        "Bug": 2.0,
        "Ghost": 2.0,
        "Psychic": 0.5,
        "Dark": 2.0
    },
    "Ice": {
        "Fighting": 2.0,
        "Rock": 2.0,
        "Steel": 2.0,
        "Fire": 2.0,
        "Ice": 0.5
    },
    "Dragon": {
        "Fire": 0.5,
        "Water": 0.5,
        "Grass": 0.5,
        "Electric": 0.5,
        "Ice": 2.0,
        "Dragon": 2.0,
        "Fairy": 2.0
    },
    "Dark": {
        "Fighting": 2.0,
        "Bug": 2.0,
        "Ghost": 0.5,
        "Psychic": 0.0,
        "Dark": 0.5,
        "Fairy": 2.0
    },
    "Fairy": {
        "Fighting": 0.5,
        "Poison": 2.0,
        "Bug": 0.5,
        "Steel": 2.0,
        "Dragon": 0.0,
        "Dark": 0.5
    }
}

def get_multiplier(defender_type, move_type, scrappy=False):
    if move_type not in multipliers[defender_type]:
        return 1.0
    if scrappy:
        if (move_type == "Fighting" or move_type == "Normal") and defender_type == "Ghost":
            return 1.0
    return multipliers[defender_type][move_type]
