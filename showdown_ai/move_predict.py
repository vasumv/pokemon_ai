import random

class MovePredictor(object):
    def __init__(self, pokedata):
        self.pokedata = pokedata

    def get_moves(self, poke, known_moves):
        raise NotImplementedError

    def __call__(self, *args):
        return self.get_moves(*args)

class RandomMovePredictor(MovePredictor):

    def __init__(self, pokedata):
        super(RandomMovePredictor, self).__init__(pokedata)
        move_list = list(self.pokedata.move_list.keys())
        random.shuffle(move_list)

        prob = 1.0 / len(move_list)
        self.predictions = [(x, prob) for x in move_list]

    def get_moves(self, poke, known_moves):
        return self.predictions





def create_predictor(name, pokedata):
    return PREDICTORS[name](pokedata)

PREDICTORS = {
    'RandomMovePredictor': RandomMovePredictor
}

