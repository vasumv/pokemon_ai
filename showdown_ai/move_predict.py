import random
from data import MOVE_CORRECTIONS, load_data, correct_name
from data import correct_mega

class MovePredictor(object):
    def __init__(self, poke, pokedata):
        self.pokedata = pokedata
        self.poke = poke

    def get_moves(self, poke, known_moves):
        raise NotImplementedError

    def __call__(self, *args):
        return self.get_moves(*args)

class RandomMovePredictor(MovePredictor):

    def __init__(self, poke, pokedata):
        super(RandomMovePredictor, self).__init__(poke, pokedata)
        poke_moves = self.pokedata.poke_moves[self.poke]
        random.shuffle(poke_moves)
        prob = 1.0 / len(poke_moves)
        self.predictions = [(x, prob) for x in poke_moves]

    def get_moves(self, poke, known_moves):
        return self.predictions

class PokeFrequencyPredictor(MovePredictor):

    def __init__(self, poke, pokedata):
        super(PokeFrequencyPredictor, self).__init__(poke, pokedata)
        graph_poke = self.pokedata.graph_poke
        self.co = graph_poke['cooccurences']
        self.freq = graph_poke['frequencies']

    def get_moves(self, known_moves):
        poke = correct_name(self.poke)
        poke = correct_mega(self.poke)
        probs = {}
        if len(known_moves) == 0:
            probs = self.get_freqs(poke, self.freq)
        else:
            for move in known_moves:
                if move not in self.co[poke]:
                    continue
                total = float(sum(self.co[poke][move].values()))
                for othermove in self.co[poke][move]:
                    if othermove in MOVE_CORRECTIONS:
                        print othermove
                        print MOVE_CORRECTIONS[othermove]
                        print probs[othermove]
                        probs[MOVE_CORRECTIONS[othermove]] = probs[othermove]
                        del probs[move]
                    if othermove in known_moves:
                        continue
                    prob = self.co[poke][move][othermove] / total
                    if othermove not in probs:
                        probs[othermove] = 1
                    probs[othermove] *= prob
        if probs == {}:
            probs = self.get_freqs(poke, self.freq)
        self.predictions = sorted(probs.items(), key=lambda x: -x[1])
        return self.predictions

    def get_freqs(self, poke, freq):
        poke = correct_name(self.poke)
        poke = correct_mega(self.poke)
        probs = {}
        total = float(sum(freq[poke].values()))
        for move in freq[poke]:
            prob = freq[poke][move] / total
            probs[move] = prob
        return probs

def create_predictor(name, poke, pokedata):
    return PREDICTORS[name](poke, pokedata)

PREDICTORS = {
    'RandomMovePredictor': RandomMovePredictor,
    'PokeFrequencyPredictor': PokeFrequencyPredictor
}

if __name__ == "__main__":
    pokedata = load_data("data")
    def foo(poke, moves):
        return PokeFrequencyPredictor(poke, pokedata)(moves)
    movepredictor = PokeFrequencyPredictor("Meganium", pokedata)


