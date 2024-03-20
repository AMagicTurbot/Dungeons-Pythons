from dice import *
from config import *

class Weapon:
    def __init__(self, name, WeaponType, Range, DamageDice, DamageType, attributes):
        self.name = name
        self.WeaponType = WeaponType
        self.range = Range
        self.DamageDice = DamageDice
        self.DamageType = DamageType
        self.attributes = attributes
        self.atkmodifier = 0
        self.dmgmodifier = 0
        


Shortsword = Weapon('Shortsword', 
                    'Martial', 5//UNITLENGHT, 
                    D6, 'slashing', 
                    ['finesse', 'light'])

Shortbow = Weapon('Shortbow', 
                    'Simple', 20//UNITLENGHT, 
                    D6, 'piercing', 
                    ['ammunition'])


Crossbow = Weapon('Crossbow', 
                    'Martial', 20//UNITLENGHT, 
                    D8, 'piercing', 
                    ['ammunition'])