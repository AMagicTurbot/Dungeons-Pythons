from tokens import *


class Erundor(Creature): 
    def __init__(self, name='Erundor', team='players'):
        spritename='Erundor'
        super().__init__(spritename, team)
        self.name=name
        self.speed = 30 // UNITLENGHT
        self.level = 7
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
        self.MaxHp = 51
        self.Hp = self.MaxHp

        #Equipment
        self.proficiencies = ['Spell Gun']
        self.weapon = SpellGun
        # self.InfusedCrossbow()
        self.ArmorClass = 19

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
                                  'Misty Step',
                                  'Propulsion Blast']

        #Spellcasting
        self.spellslots = [99, 4, 1]
        self.spellcasting_bonus = self.int_bonus
        self.spell_DC = 8 + self.spellcasting_bonus + self.proficiency


    def InfusedCrossbow(self):
        self.weapon.name = 'Infused Crossbow'
        self.weapon.atkmodifier = 1
        self.weapon.dmgmodifier = 1


class Bugbear(Creature):
    def __init__(self, name='Goblin', team='enemies'):
        spritename='Goblin'
        super().__init__(spritename, team)
        self.name=name
        self.speed = 30 // UNITLENGHT
        self.proficiency = 3
        #Characteristics
        self.str = 16
        self.str_bonus = Creature._bonus(self.str)
        self.dex = 14
        self.dex_bonus = Creature._bonus(self.dex)
        self.cos = 13
        self.cos_bonus = Creature._bonus(self.dex)
        self.int = 8
        self.int_bonus = Creature._bonus(self.dex)
        self.wis = 11
        self.wis_bonus = Creature._bonus(self.dex)
        self.cha = 9
        self.cha_bonus = Creature._bonus(self.dex)
        #Status
        self.MaxHp = 27
        self.Hp = self.MaxHp
        #Equipment
        self.proficiencies = ['Morning Star', 'Javelin']
        self.weapon = Morning_Star
        self.ArmorClass = 16
        #Actions
        self.action_list = ['Dash',
                            'Dodge',
                            'Disengage',
                            'Bugbear Weapon Attack']