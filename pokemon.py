class Pokemon():
    def __init__(self, name, hp, moves, evconfigs, ability, nature, item):
        self.name = name
        self.poke_type = poke_type
        self.hp = hp
        self.moves = moves
        self.evconfigs = evconfigs
        self.ability = ability
        self.nature = nature
        self.item = item

    def set_name(self, name):
        self.name = name

    def set_poketype(self, poketype):
        self.poke_type = poketype

    def set_hp(self, hp):
        self.hp = hp
    def set_moves(self, moves):
        self.moves = moves
    def set_nature(self, nature):
        self.nature = nature
    def set_ability(self, ability):
        self.ability = ability
    def set_evconfigs(self, evconfigs):
        self.evconfigs = evconfigs
    def set_item(self, item):
        self.item = item



