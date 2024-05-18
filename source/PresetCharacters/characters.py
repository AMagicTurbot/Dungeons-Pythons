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
        self.cos_bonus = Creature._bonus(self.cos)
        self.int = 18
        self.int_bonus = Creature._bonus(self.int)
        self.wis = 10
        self.wis_bonus = Creature._bonus(self.wis)
        self.cha = 8
        self.cha_bonus = Creature._bonus(self.cha)

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
        self.cos_bonus = Creature._bonus(self.cos)
        self.int = 8
        self.int_bonus = Creature._bonus(self.int)
        self.wis = 11
        self.wis_bonus = Creature._bonus(self.wis)
        self.cha = 9
        self.cha_bonus = Creature._bonus(self.cha)
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


class Aegis(Creature): 
    def __init__(self, name='Aegis', team='players'):
        spritename='Aegis'
        super().__init__(spritename, team)
        self.name=name
        self.speed = 45 // UNITLENGHT
        self.level = 7
        self.proficiency = 3

        #Characteristics
        self.str = 11
        self.str_bonus = Creature._bonus(self.str)
        self.dex = 14
        self.dex_bonus = Creature._bonus(self.dex)
        self.cos = 16
        self.cos_bonus = Creature._bonus(self.cos)
        self.int = 10
        self.int_bonus = Creature._bonus(self.int)
        self.wis = 18
        self.wis_bonus = Creature._bonus(self.wis)
        self.cha = 10
        self.cha_bonus = Creature._bonus(self.cha)

        #Status
        self.MaxHp = 74
        self.Hp = self.MaxHp

        #Equipment
        self.proficiencies = ['Monk Fists']
        self.weapon = Unarmed
        self.MonkDie = D8
        self.MonkFists()
        self.ArmorClass = 17

        #Actions
        self.max_attacks = 2
        self.attacks_during_action = 0
        self.attacks_during_bonus_action = 0
        self.has_used_Hands_of_Harm = False
        self.has_used_Hands_of_Healing = False
        self.action_list = ['Monk Weapon Attack', 
                            'Hands of Harm',        
                            'Monk Dodge',
                            'Monk Dash',
                            'Monk Disengage'                            
                            ]

        self.bonus_action_list = ['Monk Weapon Attack',
                                'Hands of Healing',        
                                'Hands of Harm',
                                'Monk Dodge',
                                'Monk Dash',
                                'Monk Disengage'
                                ]     

        #Ki abilities
        self.ki_points = self.level 
        self.ki_DC = 8 + self.wis_bonus + self.proficiency

    def turn_start(self):
        self.recover_action()
        self.recover_bonus_action()
        self.recover_reaction()
        self.current_movement=self.speed
        self.is_dodging = False
        self.attacks_during_action = 0
        self.attacks_during_bonus_action = 0
        self.has_used_Hands_of_Harm = False
        self.has_used_Hands_of_Healing = False

    def MonkFists(self):
        self.weapon.name = 'Monk Fists'
        self.weapon.DamageDice = self.MonkDie
        self.weapon.attributes.append('finesse')
