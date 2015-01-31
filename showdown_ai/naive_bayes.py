import json
def get_moves(poke, known_moves, graph, alpha=1.0):
    if poke == "Charizard-Mega-X" or poke == "Charizard-Mega-Y":
        poke = "Charizard"
    if poke[-5:] == "-Mega":
        poke = poke[:-5]
    co = graph['cooccurences']
    freq = graph['frequencies']
    probs = {}
    if len(known_moves) == 0:
        probs = get_freqs(poke, freq)
    else:
        for move in known_moves:
            if move not in co[poke]:
                continue
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
    if probs == {}:
        probs = get_freqs(poke, freq)
    return sorted(probs.items(), key=lambda x: -x[1])

def get_freqs(poke, freq):
    probs = {}
    total = float(sum(freq[poke].values()))
    for move in freq[poke]:
        prob = freq[poke][move] / total
        probs[move] = prob
    return probs

if __name__ == "__main__":
    with open("../data/graph.json") as fp:
        graph = json.load(fp)
