from tokens import *

class Init:
    def __init__(self):
        self.players = [
            [Antonio(), 6, 5]       #Token and starting position in row, col
            ] 
        self.enemies = [
            [Kenku(name='Kenku 1'), 4, 3], 
            [Kenku(name='Kenku 2'), 4, 4] 
        ]
        self.objects = [
            [stones(), 2, 2] 
        ]


