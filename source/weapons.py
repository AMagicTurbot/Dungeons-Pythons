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
        


Shortsword = Weapon('Shortsword', 
                    'Martial', 5//UNITLENGHT, 
                    D6, 'slashing', 
                    ['finesse', 'light'])

Shortbow = Weapon('Shortbow', 
                    'Simple', 20//UNITLENGHT, 
                    D6, 'slashing', 
                    ['ammunition'])