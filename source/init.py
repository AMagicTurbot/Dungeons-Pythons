from tokens import *

class Init:
    def __init__(self):
        self.players = [
            [Antonio(), 6, 5]       #Token and starting position in row, col
            ] 
        self.enemies = [
            [Kenku(), 4, 3] 
        ]
        self.objects = [
            [stones(), 2, 2] 
        ]


