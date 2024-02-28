import os
from config import *

class Token:
    def __init__(self, name, texture=None, texture_rect=None):
        self.name = name
        self.texture = texture
        self.set_texture()
        self.texture_rect = texture_rect
        
        #default attributes
        self.can_move = False
        self.team = None

    def set_texture(self):
        self.texture = os.path.join(f'assets/images/tokens/{self.name}.png')
        
    


#Playable tokens
class Creature(Token):
    def __init__(self, name, team, speed=0, sheet=None):
        super().__init__(name)
        self.team = team
        
        #Movement
        self.can_move = True
        self.speed = speed // UNITLENGHT
        self.current_movement = self.speed 
        self.moves = []
        self.has_moved_diagonally_once = False

    def add_move(self, move):
        self.moves.append(move)
    
    def clear_moves(self):
        self.moves = []

    

#Preset characters
class Antonio(Creature): 
    def __init__(self):
        super().__init__('Antonio', team='players')
        self.speed = 20 // UNITLENGHT
        self.current_movement = self.speed 

class Kenku(Creature):
    def __init__(self):
        super().__init__('Kenku', team='enemies', speed=10)




#Inanimate game objects
class Object(Token):
    def __init__(self, name):
        super().__init__(name)

class stones(Object):
    def __init__(self):
        super().__init__('stones')


        