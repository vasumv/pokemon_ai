import requests
import json
class SmogonMoves():
    BASE_URL = "http://www.smogon.com/dex/api/query"
    def __init__(self):
        self.url = self.BASE_URL
    def get_all_moves(self):
        fields = ["name"]
        query = {"move":{"gen":"xy"}, "$": fields}
        params = {"q": json.dumps(query)}
        output = requests.get(self.url, params=params)
        output = output.json()
        moves = output['result']
        poke_moves = []
        for move in moves:
            poke_moves.append(move['name'])
        return poke_moves

    def get_move_info(self, move):
        fields = ["name","alias","gen","category","power","accuracy","pp","description",{"type":["alias","name","gen"]}]
        query = {"move":{"gen":"xy", "name": "%s" % move}, "$": fields}
        params = {"q": json.dumps(query)}
        output = requests.get(self.url, params=params)
        output = output.json()
        return output
    def write_damage_move(self, move, output):
        result = output['result']
        category = result[0]['category']
        if category == "Physical" or category == "Special":
            name = result[0]['name']
            power = result[0]['power']
            description = result[0]['description']
            priority = 0
            if "Priority" in description:
                priority_index = description.index("Priority")
                priority = description[priority_index+9:][:2]
                if "+" in priority:
                    priority = priority[1:]
                priority = int(priority)
            accuracy = float(result[0]['accuracy']) / 100
            type = result[0]['type']['name']
            output = """"%s": DamagingMove("%s",
                          power=%d,
                          category="%s",
                          priority=%d,
                          type="%s",
                          accuracy=%f),\n""" % (
                          name,
                          name,
                          power,
                          category,
                          priority,
                          type,
                          accuracy
                          )
            with open("data/moves.json", "a") as f:
                f.write(output)


move = SmogonMoves()
moves = move.get_all_moves()
for poke_move in moves:
    print poke_move
    if poke_move == "Pursuit":
        continue
    info = move.get_move_info(poke_move)
    move.write_damage_move(poke_move, info)
