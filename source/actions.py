from dice import *
from buttons import *

class Action:
    #Rationale:
    # - Actions must be self consistent objects that can be instanciated without any external parameter
    # - Each Action is identified by an unambigous name
    # - Each Action has a 
    #       .is_available(), 
    #       .requires_target(),
    #       .create() and
    #       .do()
    #        methods
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
        elif cost == 'reaction':
            return token.has_reaction()
        elif cost == None:
            return True

    def requires_target(self):
        return False

    def create(self, token, cost):
        self.token = token
        self.cost = cost
        return self

    def unbind(self):
        self.token = None
        self.cost = None
        self.button = None

    def do(self, game):
        pass

### Actions Database ###

#General turn actions
class Pass(Action):
    def __init__(self):
        name = 'Pass'
        super().__init__(name)

    def is_available(self, token, cost):
        return True
    
    def create(self, token, cost):
        del self
        new_instance = Pass()
        new_instance.token = token
        new_instance.cost = cost
        return new_instance

    def do(self, game):
        game.gamelog.new_line(self.token.name + ' ends its turn')
        game.next_turn()

class Dash(Action):
    def __init__(self):
        name = 'Dash'
        super().__init__(name)
    
    def create(self, token, cost):
        del self
        new_instance = Dash()
        new_instance.token = token
        new_instance.cost = cost
        return new_instance

    def do(self, game):
        #Instructions
        self.token.current_movement += self.token.speed
        #Log
        game.gamelog.new_line(self.token.name + ' dashes.')
        #Cost
        if self.cost == 'action': self.token.use_action()
        elif self.cost == 'bonus action': self.token.use_bonus_action()

class Dodge(Action):
    def __init__(self):
        name = 'Dodge'
        super().__init__(name)

    def create(self, token, cost):
        del self
        new_instance = Dodge()
        new_instance.token = token
        new_instance.cost = cost
        return new_instance

    def do(self, game):
        #Instructions
        self.token.is_dodging = True
        #Log
        game.gamelog.new_line(self.token.name + ' dodges.')
        #Cost
        if self.cost == 'action': self.token.use_action()
        elif self.cost == 'bonus action': self.token.use_bonus_action()

class Disengage(Action):
    def __init__(self):
        name = 'Disengage'
        super().__init__(name)

    def create(self, token, cost):
        del self
        new_instance = Disengage()
        new_instance.token = token
        new_instance.cost = cost
        return new_instance

    def do(self, game):
        #Instructions
        self.token.freemoving = True
        self.token.EndTurnActions.append(EndDisengage(self.token))
        #Log
        game.gamelog.new_line(self.token.name + ' disengages.')
        #Cost
        if self.cost == 'action': self.token.use_action()
        elif self.cost == 'bonus action': self.token.use_bonus_action()


#Attacks Action
#Attacks require a TARGET, which is found by scanning squares within a certain RANGE for enemy tokens
class Attack(Action):
    def __init__(self, name):
        super().__init__(name)
        self.range = 5//UNITLENGHT
        self.target = None
        self.modifier = 0
    
    def requires_target(self):
        return True

    def create(self, token, cost, name):
        del self
        new_instance = Attack(name)
        new_instance.token = token
        new_instance.cost = cost
        return new_instance
    
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

    def _attack(self, modifier):
        if self.target.is_dodging: roll = D20.roll(disadvantage=True)
        else: roll = D20.roll()
        roll += modifier
        return roll

class WeaponAttack(Attack):
    def __init__(self):
        name = 'Weapon Attack'
        super().__init__(name)
        self.proficient = False
    
    def create(self, token, cost, target):
        del self
        new_instance = WeaponAttack()
        new_instance.token = token
        new_instance.name = token.weapon.name + ' attack vs ' + target.name
        new_instance.range = new_instance.token.weapon.range
        new_instance.proficient = bool(token.weapon.name in token.proficiencies)
        new_instance.cost = cost
        new_instance.target = target
        return new_instance

    def attack(self):
        if self.token.weapon.range > 1 or 'finesse' in self.token.weapon.attributes:
            mod = self.token.dex_bonus
        else:
            mod = self.token.str_bonus
        if self.proficient: mod += self.token.proficiency
        roll = self._attack(mod) + self.modifier
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
        elif self.cost == 'reaction': self.token.use_reaction()

#Game Actions
#Actions taken by the game itself, thus not using the .create method
class EndDisengage(Action):
    def __init__(self, token, delay = 1):
        name = 'EndDisengage'
        super().__init__(name)
        self.token = token
        self.delay = delay
    
    def do(self, game):
        self.delay -= 1
        if self.delay <= 0:
            self.token.EndTurnActions.remove(ExtraTurn(None))
            self.freemoving = False

class ExtraTurn(Action):
    def __init__(self, token):
        name = 'ExtraTurn'
        super().__init__(name)
        self.token = token

    def do(self, game):
        self.token.EndTurnActions.remove(ExtraTurn(None))
        game.gamelog.new_line(self.token.name + ' does an extra turn')
        index = game.initiative_order.index(game.active_player)
        if index == 0:
            game.active_player = game.initiative_order[-1]
        else:
            game.active_player = game.initiative_order[index-1]

class SkipTurn(Action):
    def __init__(self, token):
        name = 'SkipTurn'
        super().__init__(name)
        self.token = token

    def do(self, game):
        self.token.BeginTurnActions.remove(SkipTurn(None))
        game.gamelog.new_line(self.token.name + ' skips the turn')
        game.next_turn()


ActionDatabase = {  'Pass': Pass(),
                    'Dash': Dash(),
                    'Dodge': Dodge(),
                    'Disengage': Disengage(),
                    'Weapon Attack': WeaponAttack()}