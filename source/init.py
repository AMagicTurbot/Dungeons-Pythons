from tokens import *
import random
from PresetCharacters.characters import *


row1, row2, row3 = 3,3,2
col1, col2, col3 = 4,4,2

def initialize_positions():
    global row1, row2, row3, col1, col2, col3 
    row1, row2, row3 = random.sample(range(0,8), 3)
    col1, col2, col3 = random.sample(range(0,11), 3)

class Init:
    def __init__(self):
        initialize_positions()
        self.players = [
             [Kenku(name='Kenku Player'), row1, col1]
            # [Erundor(), 3, 3]      #Token and starting position in row, col
            ] 
        self.enemies = [
            # [Erundor(name='AI'), 3, 3]
            [Kenku(name='Kenku AI'), row2, col2], 
            # [Kenku(name='Kenku 2'), 4, 4] 
        ]
        self.objects = [
            [stones(), row3, col3] 
        ]


        self.enemies[0][0].weapon = Shortsword
        self.players[0][0].weapon = Shortsword




