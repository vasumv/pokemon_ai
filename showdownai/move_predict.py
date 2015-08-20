import random
from data import MOVE_CORRECTIONS, NAME_CORRECTIONS, load_data, correct_name, correct_move
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
        poke_moves = self.pokedata.poke_moves[correct_mega(correct_name(self.poke))]
        random.shuffle(poke_moves)
        prob = 1.0 / len(poke_moves)
        self.predictions = [(x, prob) for x in poke_moves]

    def get_moves(self, known_moves):
        return self.predictions

class MoveFrequencyPredictor(MovePredictor):

    def __init__(self, poke, pokedata):
        super(MoveFrequencyPredictor, self).__init__(poke, pokedata)
        graph_move = self.pokedata.graph_move
        self.poke_moves = self.pokedata.poke_moves[correct_mega(correct_name(self.poke))]
        self.co = graph_move['cooccurences']
        self.freq = graph_move['frequencies']

    def get_freqs(self, freq):
        probs = {}
        for move in freq:
            prob = freq[move]
            probs[move] = prob
        return probs

    def get_moves(self, known_moves):
        move_freq = sorted(self.get_freqs(self.freq).items(), key=lambda x: -x[1])
        new_move_freq = []
        for move in move_freq:
            if move[0] in self.poke_moves:
                new_move_freq.append(move)
        self.predictions = new_move_freq
        return self.predictions

class MoveCoPredictor(MovePredictor):

    def __init__(self, poke, pokedata):
        super(MoveCoPredictor, self).__init__(poke, pokedata)
        graph_move = self.pokedata.graph_move
        self.poke_moves = self.pokedata.poke_moves[correct_mega(correct_name(self.poke))]
        self.co = graph_move['cooccurences']
        self.freq = graph_move['frequencies']

    def get_freqs(self, freq):
        probs = {}
        for move in freq:
            if move in self.poke_moves:
                prob = freq[move]
                probs[move] = prob
        return probs

    def get_moves(self, known_moves):
        probs = {}
        if len(known_moves) == 0:
            probs = self.get_freqs(self.freq)
        else:
            for move in self.co:
                print move
                if move in known_moves:
                    continue
                if move not in self.poke_moves:
                    continue
                prob = 1.0
                for othermove in known_moves:
                    if othermove not in self.co[move]:
                        prob *= 0
                        continue
                    prob *= self.co[move][othermove]
                if move in MOVE_CORRECTIONS:
                    probs[MOVE_CORRECTIONS[othermove]] = probs[othermove]
                    del probs[move]
                prob *= self.freq[move]
                probs[move] = prob
        if probs == {}:
            probs = self.get_freqs(self.freq)
        self.predictions = sorted(probs.items(), key=lambda x: -x[1])
        return self.predictions

    def get_moves_assumption_two(self, known_moves):
        probs = {}
        if len(known_moves) == 0:
            probs = self.get_freqs(self.freq)
        else:
            for move in known_moves:
                if move not in self.co:
                    continue
                for othermove in self.co[move]:
                    prob = 1.0
                    if othermove in MOVE_CORRECTIONS:
                        probs[MOVE_CORRECTIONS[othermove]] = probs[othermove]
                        del probs[move]
                    if othermove not in self.poke_moves:
                        continue
                    if othermove in known_moves:
                        continue
                    prob = self.co[move][othermove]
                    if othermove not in probs:
                        probs[othermove] = 1
                    probs[othermove] *= prob
        if probs == {}:
            probs = self.get_freqs(self.freq)
        self.predictions = sorted(probs.items(), key=lambda x: -x[1])
        return self.predictions

class PokeFrequencyPredictor(MovePredictor):

    def __init__(self, poke, pokedata):
        super(PokeFrequencyPredictor, self).__init__(poke, pokedata)
        graph_poke = self.pokedata.graph_poke
        self.co = graph_poke['cooccurences']
        self.freq = graph_poke['frequencies']

    def get_freqs(self, freq):
        poke = correct_name(self.poke)
        poke = correct_mega(poke)
        probs = {}
        for move in freq[poke]:
            prob = freq[poke][move]
            probs[move] = prob
        return probs

    def get_moves(self, known_moves):
        poke = correct_name(self.poke)
        poke = correct_mega(poke)
        probs = {}
        if len(known_moves) == 0:
            probs = self.get_freqs(self.freq)
        else:
            for move in self.co[poke]:
                if move in known_moves:
                    continue
                prob = 1.0
                for othermove in known_moves:
                    if othermove not in self.co[poke][move]:
                        prob *= 0
                        continue
                    prob *= self.co[poke][move][othermove]
                if move in MOVE_CORRECTIONS:
                    probs[MOVE_CORRECTIONS[othermove]] = probs[othermove]
                    del probs[move]
                prob *= self.freq[poke][move]
                probs[move] = prob
        #else:
            #for move in known_moves:
                #if move not in self.co[poke]:
                    #continue
                #for othermove in self.co[poke][move]:
                    #if othermove in MOVE_CORRECTIONS:
                        #probs[MOVE_CORRECTIONS[othermove]] = probs[othermove]
                        #del probs[move]
                    #if othermove in known_moves:
                        #continue
                    #prob = self.co[poke][move][othermove]
                    #if othermove not in probs:
                        #probs[othermove] = 1
                    #probs[othermove] *= prob
        if probs == {}:
            probs = self.get_freqs(poke, self.freq)
        self.predictions = sorted(probs.items(), key=lambda x: -x[1])
        return self.predictions

    def get_moves_assumption_two(self, known_moves):
        poke = correct_name(self.poke)
        poke = correct_mega(self.poke)
        probs = {}
        if len(known_moves) == 0:
            probs = self.get_freqs(poke, self.freq)
        else:
            for move in known_moves:
                if move not in self.co[poke]:
                    continue
                for othermove in self.co[poke][move]:
                    if othermove in MOVE_CORRECTIONS:
                        probs[MOVE_CORRECTIONS[othermove]] = probs[othermove]
                        del probs[move]
                    if othermove in known_moves:
                        continue
                    prob = self.co[poke][move][othermove]
                    if othermove not in probs:
                        probs[othermove] = 1
                    probs[othermove] *= prob
        if probs == {}:
            probs = self.get_freqs(poke, self.freq)
        self.predictions = sorted(probs.items(), key=lambda x: -x[1])
        return self.predictions

def create_predictor(name, poke, pokedata):
    return PREDICTORS[name](poke, pokedata)

PREDICTORS = {
    'RandomMovePredictor': RandomMovePredictor,
    'PokeFrequencyPredictor': PokeFrequencyPredictor,
    'MoveFrequencyPredictor': MoveFrequencyPredictor,
    'MoveCoPredictor': MoveCoPredictor
}

if __name__ == "__main__":
    pokedata = load_data("data")
    def foo(poke, moves):
        return MoveCoPredictor(poke, pokedata)(moves)
    movepredictor = MoveCoPredictor("Charizard", pokedata)
