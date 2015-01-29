import json
def get_moves(poke, known_moves, graph):
    co = graph['cooccurences']
    freq = graph['frequencies']
    probs = {}
    if len(known_moves) == 0:
        total = float(sum(freq[poke].values()))
        for move in freq[poke]:
            prob = freq[poke][move] / total
            probs[move] = prob
    else:
        for move in known_moves:
            total = float(sum(co[poke][move].values()))
            for othermove in co[poke][move]:
                if othermove in known_moves:
                    continue
                prob = co[poke][move][othermove] / total
                if othermove not in probs:
                    probs[othermove] = 1
                probs[othermove] *= prob
    if "Hidden Power" in probs:
        del probs["Hidden Power"]
    return sorted(probs.items(), key=lambda x: -x[1])

if __name__ == "__main__":
    with open("../data/graph.json") as fp:
        graph = json.load(fp)
