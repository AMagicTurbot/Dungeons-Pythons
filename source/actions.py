from dice import *
from buttons import *

class Action:
    #Rationale:
    # - Actions must be self consistent objects that can be instanciated without any external parameter
    # - Each Action is identified by an unambigous name
    # - Each Action has a .do(), .is_available(), .requires_target() and .bind() methods
    # - Each Action will be bounded to a token and a cost using the .create() method (in game.get_available_actions())
    # - Unbound actions are used to let the game know what each token is capable of doing
    # - Additional parameters needed to complete the Action data (such as weapons, targets and so on) are added during binding
    # - When the Action binding is completed, a Button is associated to it for GUI purposes
    def __init__(self,name):
        #Mandatory parameters
        self.name = name
        
        #Binding parameters
        self.cost = None
        self.token = None 
        self.button = None 
        
    def __eq__(self, other):
        return self.name == other.name

    def is_available(self, token, cost):
        if cost == 'action':
            return token.has_action()
        elif cost == 'bonus action':
            return token.has_bonus_action()

    def requires_target(self):
        return False

    def create(self, token, cost):
        self.token = token
        self.cost = cost
        return self

    def do(self, game):
        pass

### Actions Database ###

#General turn actions
class Wait(Action):
    def __init__(self):
        name = 'Wait'
        super().__init__(name)

    def do(self, game):
        game.gamelog.new_line(self.token.name + ' waits...')
        if self.cost == 'action': self.token.use_action()
        elif self.cost == 'bonus action': self.token.use_bonus_action()
        game.next_turn()

class Dash(Action):
    def __init__(self):
        name = 'Dash'
        super().__init__(name)
    
    def do(self, game):
        self.token.current_movement += self.token.speed
        game.gamelog.new_line(self.token.name + ' dashes.')
        if self.cost == 'action': self.token.use_action()
        elif self.cost == 'bonus action': self.token.use_bonus_action()

#Attacks Action
#Attacks require a TARGET, which is found by scanning squares within a certain RANGE for enemy tokens
class Attack(Action):
    def __init__(self, name):
        super().__init__(name)
        self.range = 5//UNITLENGHT
        self.target = None
    
    def requires_target(self):
        return True

    def get_available_targets(self, token, field):
        available_targets = []
        for rows in field.squares:
            for square in rows:
                if square.token == token:
                    initial_square = square
        for rows in field.squares:
            for square in rows:
                if square.has_enemy(token.team): 
                    if initial_square.distance(square)<=token.weapon.range:
                        available_targets.append(square.token)
        return available_targets


class WeaponAttack(Attack):
    def __init__(self):
        name = 'Weapon Attack'
        super().__init__(name)
        self.proficient = False
        self.modifier = 0
    
    def __deepcopy__(self):
        return WeaponAttack()
    def create(self, token, cost, target):
        new_instance = self.__deepcopy__()
        new_instance.token = token
        new_instance.name = token.weapon.name + ' attack vs ' + target.name
        new_instance.range = new_instance.token.weapon.range
        new_instance.proficient = bool(token.weapon.name in token.proficiencies)
        new_instance.cost = cost
        new_instance.target = target
        return new_instance

    def attack(self):
        roll = D20.roll()
        if self.token.weapon.range > 1 or 'finesse' in self.token.weapon.attributes:
            roll += self.token.dex_bonus
        else:
            roll += self.token.str_bonus
        if self.proficient: roll+= self.token.proficiency
        roll += self.modifier
        return roll
    
    def damage(self):
        roll = self.token.weapon.DamageDice.roll()
        if self.token.weapon.range > 1  or 'finesse' in self.token.weapon.attributes:
            roll += self.token.dex_bonus
        else:
            roll += self.token.str_bonus
        roll += self.modifier
        return roll

    def do(self, game):
        AttackRoll = self.attack()
        game.gamelog.new_line(self.token.name + ' attacks ' + self.target.name)
        if AttackRoll >= self.target.ArmorClass:
            DamageRoll = self.damage()
            game.gamelog.new_line(str(AttackRoll) + ' to hit: Hits for '+ str(DamageRoll) + ' ' + self.token.weapon.DamageType + ' damage')
            self.target.Hp -= DamageRoll
        else: 
            game.gamelog.new_line(str(AttackRoll) + ' to hit: Misses!')
        if self.cost == 'action': self.token.use_action()
        elif self.cost == 'bonus action': self.token.use_bonus_action()


ActionDatabase = {  'Wait': Wait(),
                    'Dash': Dash(),
                    'Weapon Attack': WeaponAttack()}