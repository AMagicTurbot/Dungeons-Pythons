from tokens import *


class Erundor(Creature): 
    def __init__(self, name='Erundor', team='players'):
        spritename='Erundor'
        super().__init__(spritename, team)
        self.name=name
        self.speed = 15 // UNITLENGHT
        self.level = 6
        self.proficiency = 3

        #Characteristics
        self.str = 8
        self.str_bonus = Creature._bonus(self.str)
        self.dex = 16
        self.dex_bonus = Creature._bonus(self.dex)
        self.cos = 14
        self.cos_bonus = Creature._bonus(self.dex)
        self.int = 18
        self.int_bonus = Creature._bonus(self.dex)
        self.wis = 10
        self.wis_bonus = Creature._bonus(self.dex)
        self.cha = 8
        self.cha_bonus = Creature._bonus(self.dex)

        #Status
        self.MaxHp = 43
        self.Hp = self.MaxHp

        #Equipment
        self.proficiencies = ['Crossbow']
        self.weapon = Crossbow
        self.InfusedCrossbow()
        self.ArmorClass = 17

        #Actions
        self.action_list = ['Dodge',
                            'Disengage',
                            'Weapon Attack',
                            'Firebolt',
                            'Cure Wounds',
                            'Magic Missiles'
                            ]

        self.bonus_action_list = ['Triangulate Target',
                                  'Dash',
                                  #'Misty Step',
                                  'Propulsion Blast']

        #Spellcasting
        self.spellslots = [99, 4, 1]
        self.spellcasting_bonus = self.int_bonus
        self.spell_DC = 8 + self.spellcasting_bonus + self.proficiency


    def InfusedCrossbow(self):
        self.weapon.name = 'Infused Crossbow'
        self.weapon.atkmodifier = 1
        self.weapon.dmgmodifier = 1