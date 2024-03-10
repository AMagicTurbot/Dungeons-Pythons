import os
import random
from config import *
from actions import *
from weapons import * 
from buttons import *

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
        #Turn variables
        self.initiative = 0
        self.action = 1
        self.bonus_action = 1
        self.reaction = 1
        #Status
        self.is_dodging = False
        self.freemoving = False
        #Game actions
        self.action_list = []
        self.bonus_action_list = []
        self.BeginTurnActions = []
        self.ActiveTurnActions = []
        self.ActiveTurnBonusActions = []
        self.EndTurnActions = []

    def add_move(self, move):
        self.moves.append(move)
    def clear_moves(self):
        self.moves = []
    def _bonus(characteristic):
        return (characteristic-10)//2

    #Turn methods
    def use_action(self):
        self.action = 0
    def recover_action(self):
        self.action = 1
    def use_bonus_action(self):
        self.bonus_action = 0
    def recover_bonus_action(self):
        self.bonus_action=1
    def use_reaction(self):
        self.reaction = 0
    def recover_reaction(self):
        self.reaction = 1
    
    def turn_start(self):
        self.recover_action()
        self.recover_bonus_action()
        self.recover_reaction()
        self.current_movement=self.speed
        self.is_dodging = False

    def has_action(self):
        return self.action==1
    def has_bonus_action(self):
        return self.bonus_action==1
    def has_reaction(self):
        return self.reaction==1
   
#Preset characters
class Antonio(Creature): 
    def __init__(self, name='Antonio', team='players'):
        spritename='Antonio'
        super().__init__(spritename, team)
        self.name=name
        self.speed = 20 // UNITLENGHT
        self.proficiency = 2

        #Characteristics
        self.str = 12
        self.str_bonus = Creature._bonus(self.str)
        self.dex = 16
        self.dex_bonus = Creature._bonus(self.dex)

        #Status
        self.MaxHp = 12
        self.Hp = self.MaxHp

        #Equipment
        self.proficiencies = ['Shortsword']
        self.weapon = Shortsword
        self.ArmorClass = 15

        #Actions
        self.action_list = ['Pass',
                            'Dash',
                            'Dodge',
                            'Disengage',
                            'Weapon Attack']

        self.bonus_action_list = ['Dash']

class Kenku(Creature):
    def __init__(self, name='Kenku', team='enemies'):
        spritename='Kenku'
        super().__init__(spritename, team)
        self.name=name
        self.speed = 10 // UNITLENGHT
        self.proficiency = 2
        #Characteristics
        self.str = 8
        self.str_bonus = Creature._bonus(self.str)
        self.dex = 14
        self.dex_bonus = Creature._bonus(self.dex)
        #Status
        self.MaxHp = 5
        self.Hp = self.MaxHp
        #Equipment
        self.proficiencies = []
        self.weapon = Shortsword
        self.ArmorClass = 12
        #Actions
        self.action_list = ['Pass',
                            'Dash',
                            'Dodge',
                            'Disengage',
                            'Weapon Attack']



#Inanimate tokens
class Object(Token):
    def __init__(self, name):
        super().__init__(name)

class stones(Object):
    def __init__(self):
        super().__init__('stones')

class tombstone(Object):
    def __init__(self, name):
        super().__init__('tombstone')
        self.name = name



        