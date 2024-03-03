import os
import random
from config import *

class Token:
    def __init__(self, name, texture=None, texture_rect=None):
        self.name = name
        self.ID = random.randint(10000, 99999)
        self.texture = texture
        self.set_texture()
        self.texture_rect = texture_rect
        
        #default attributes
        self.can_move = False
        self.team = None

    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        if other == None:
            return False
        else:
            return self.name == other.name and self.ID == other.ID
    
    def set_texture(self):
        try: self.texture = os.path.join(f'assets/images/tokens/{self.name}.png')
        except: self.texture = os.path.join(f'assets/images/tokens/Antonio.png')
        
    


#Playable tokens
class Creature(Token):
    def __init__(self, name, team, speed=0):
        super().__init__(name)
        self.team = team
        
        #Movement
        self.can_move = True
        self.speed = speed // UNITLENGHT
        self.current_movement = self.speed 
        self.moves = []
        self.has_moved_diagonally_once = False

        #Game variables
        self.initiative = 0
        self.action = 1
        self.bonus_action = 1
        self.reaction = 1

    def add_move(self, move):
        self.moves.append(move)
    
    def clear_moves(self):
        self.moves = []
    
    def recover_action(self):
        self.action = 1

    def recover_bonus_action(self):
        self.bonus_action=1

    def recover_reaction(self):
        self.reaction = 1
    
    def recover_all(self):
        self.recover_action()
        self.recover_bonus_action()
        self.recover_reaction()
        self.current_movement=self.speed

    def has_action(self):
        return self.action>0

    def has_bonus_action(self):
        return self.bonus_action>0

    def has_reaction(self):
        return self.reaction>0

    def _bonus(characteristic):
        return (characteristic-10)//2

    

#Preset characters
class Antonio(Creature): 
    def __init__(self):
        super().__init__('Antonio', team='players')
        self.speed = 20 // UNITLENGHT
        self.dex = 16
        self.dex_bonus = Creature._bonus(self.dex)

class Kenku(Creature):
    def __init__(self):
        super().__init__('Kenku', team='enemies')
        self.speed = 10 // UNITLENGHT
        self.dex = 14
        self.dex_bonus = Creature._bonus(self.dex)




#Inanimate game objects
class Object(Token):
    def __init__(self, name):
        super().__init__(name)

class stones(Object):
    def __init__(self):
        super().__init__('stones')


        