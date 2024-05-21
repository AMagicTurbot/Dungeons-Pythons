from tokens import *
import random
from PresetCharacters.characters import *


row1, row2, row3, row4, row5, row6 = 3,3,2,1,5,6
col1, col2, col3, col4, col5, col6 = 4,4,2,4,3,5

def initialize_positions():
    global row1, row2, row3, row4, row5, row6, col1, col2, col3, col4, col5, col6
    row1, row2, row3, row4, row5, row6 = random.sample(range(0,8), 6)
    col1, col2, col3, col4, col5, col6 = random.sample(range(0,11), 6)

class Init_AI:
    def __init__(self):
        initialize_positions()
        self.players = [
            [Bugbear(name='Bugbear'), row1, col1]
            ] 
        self.enemies = [
            [Bugbear(name='Bugbear AI'), row2, col2]
        ]
        self.objects = [
            [stones(), row3, col3] 
        ]



class Init_LV1:
    def __init__(self):
        initialize_positions()
        self.players = [
            [Erundor(), row1, col1] 
            ] 
        self.enemies = [
            [Bugbear(name='Bugbear'), row2, col2] 
        ]
        self.objects = [
            [stones(), row3, col3] 
        ]

class Init_LV2:
    def __init__(self):
        initialize_positions()
        self.players = [
            [Erundor(), row1, col1]      
            ] 
        self.enemies = [
            [Bugbear(name='Bugbear A'), row2, col2],
            [Bugbear(name='Bugbear B'), row3, col3],
            [Bugbear(name='Bugbear C'), row4, col4]  
        ]
        self.objects = [
            [stones(), row5, col5],
            [stones(), row6, col6]  
        ]

class Init_LV3:
    def __init__(self):
        initialize_positions()
        self.players = [
            # [Aegis(name='Aegis'), row1, col1] 
            [Erundor(), row1, col1]    
            ] 
        self.enemies = [
            [Aegis(name='Aegis AI'), row2, col2], 
        ]
        self.objects = [
            [stones(), row3, col3],
            [stones(), row4, col4],
            [corpse(), row5, col5],
            [corpse(), row6, col6]
        ]