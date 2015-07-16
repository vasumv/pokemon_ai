import json
from data import MOVE_CORRECTIONS, correct_mega
def get_moves(poke, known_moves, graph, data, alpha=1.0):
    poke = correct_mega(poke)
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
                if othermove in MOVE_CORRECTIONS:
                    probs[MOVE_CORRECTIONS[othermove]] = probs[othermove]
                    del probs[move]
                if othermove in known_moves:
                    continue
                prob = co[poke][move][othermove] / total
                if othermove not in probs:
                    probs[othermove] = 1
                probs[othermove] *= prob
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
    from data import load_data
    data, bw_data, graph = load_data('../data')
    def foo(x, y):
        return get_moves(x, y, graph, data)
