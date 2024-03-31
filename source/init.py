from tokens import *
from PresetCharacters.characters import *

class Init:
    def __init__(self):
        self.players = [
            [Kenku(name='Kenku'), 4, 4]       #Token and starting position in row, col
            ] 
        self.enemies = [
            # [Erundor(name='AI'), 3, 3]
            [Kenku(name='Kenku AI'), 4, 3], 
            # [Kenku(name='Kenku 2'), 4, 4] 
        ]
        self.objects = [
            [stones(), 2, 2] 
        ]


        self.players[0][0].weapon = Shortsword
