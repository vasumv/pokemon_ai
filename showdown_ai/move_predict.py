import random

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


def create_predictor(name, poke, pokedata):
    return PREDICTORS[name](poke, pokedata)

PREDICTORS = {
    'RandomMovePredictor': RandomMovePredictor
}

