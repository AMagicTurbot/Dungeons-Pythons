from dice import *
from buttons import *

class Action:
    def __init__(self,name, cost, token):
        self.name = name
        self.token = token
        self.cost = cost
    
        self.button = None #to be created automatically as an instance of Action(Button) in the game class
        

    def __eq__(self, other):
        return self.name == other.name and self.token == other.token

    def do(self, game):
        pass

class ExtractWeapon(Action):
    def __init__(self, weapon, token):
        self.weapon = weapon
        name = 'Extract' + weapon.name
        cost = None
        super().__init__(name, cost, token)
    
    def do(self, game):
        self.token.weapon = self.weapon
        game.gamelog.new_line(self.name + ' extracts ' + self.weapon.name)


class Attack(Action):
    def __init__(self, name, cost, token):
        super().__init__(name, cost, token)
        self.range = 5//UNITLENGHT
        self.target = None

    def get_available_targets(token, field):
        available_targets = []
        for rows in self.field.squares:
            for square in rows:
                if square.token == token:
                    square == initial_square
        for rows in self.field.squares:
            for square in rows:
                if square.has_enemy() and initial_square.distance(square)<=token.weapon.range:
                    available_targets.append(square.token)


class WeaponAttack(Attack):
    def __init__(self, cost, token, proficient=True):
        name = token.weapon.name + ' attack'
        super().__init__(name, cost, token)
        self.proficient = proficient
        self.range = self.token.weapon.range
    
    def attack(self, modifier=0):
        roll = D20.roll()
        if self.token.weapon.range > 5//UNITLENGHT or 'finesse' in self.token.weapon.attributes:
            roll += self.token.dex_bonus()
        else:
            roll += self.token.str_bonus()
        if self.proficient: roll+= self.token.proficiency
        roll += modifier
        return roll
    
    def damage(self, modifier=0):
        roll = self.token.weapon.DamageDice.roll()
        if self.token.weapon.range > 5//UNITLENGHT  or 'finesse' in self.token.weapon.attributes:
            roll += self.token.dex_bonus()
        else:
            roll += self.token.str_bonus()
        roll += modifier
        return roll

    def do(self, game, modifier=0):
        if self.cost == 'action':
            self.token.action = 0
        elif self.cost == 'bonus action':
            self.token.bonus_action = 0
        AttackRoll = self.roll(modifier)
        if AttackRoll >= self.target.ArmorClass:
            DamageRoll = self.damage()
            self.target.HP -= DamageRoll
