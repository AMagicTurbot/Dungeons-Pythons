from dice import *
from buttons import *
from move import Move
import numpy as np

def on_field(row, col):
        if row > ROWS-1 or row < 0:
            return False
        if col > COLS-1 or col < 0:
            return False
        return True

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
        if other == None:
            return False
        else:
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
    
    def required_spell_slot(self):
        return 0

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
        new_instance.cost = None
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

class Movement(Action):
    def __init__(self, initial, direction):
        self.direction = direction
        self.initial_square = initial
        name = 'Move ' + str(direction[0]) + ' ,' + str(direction[1])
        super().__init__(name)

    def do(self, game):
        row = self.initial_square.row
        col = self.initial_square.col
        final_row = row+self.direction[0]
        final_col = col+self.direction[1]
        game.field.get_moves(game.active_player, row, col)
        for move in game.active_player.moves:
            if move.final.row == final_row and move.final.col == final_col:
                game.field.move(game.active_player, move, game)



#Attack Actions
#Attacks require a TARGET, which is found by scanning squares within a certain RANGE for enemy tokens
class Attack(Action):
    def __init__(self):
        name = 'Attack'
        super().__init__(name)
        self.range = 1
        self.target = None
        self.target_square = None
        self.token_square = None
        self.is_critical = False
        self.available_targets = []
    
    def requires_target(self):
        return True
    
    def set_target(self, target, target_square, token_square):
        self.token_square = token_square
        self.target_square = target_square
        self.target = target

    def create(self, token, cost):
        del self
        new_instance = Attack()
        new_instance.token = token
        new_instance.cost = cost
        return new_instance

    def get_available_targets(self, token, field):
        self.available_targets = []
        for rows in field.squares:
            for square in rows:
                if square.token == token:
                    initial_square = square
        for rows in field.squares:
            for square in rows:
                if self.is_valid_target(initial_square, square, square.token):
                        self.available_targets.append(square)
        return self.available_targets
    
    def is_valid_target(self, initial_square, final_square, token):
        if final_square.has_enemy(self.token.team): 
            if final_square.distance(initial_square)<=self.range:
                return True
            else:
                return False
        else:
            return False

    def _attack(self, modifier, advantage = False, disadvantage=False):
        #Dodging
        if self.target.is_dodging: roll = D20.roll(advantage=advantage, disadvantage=True)
        else: roll = D20.roll(advantage=advantage, disadvantage=disadvantage)
        #Critical hits
        if roll == 20: self.is_critical = True
        else: self.is_critical = False
        roll += modifier
        return roll

class WeaponAttack(Attack):
    def __init__(self):
        super().__init__()
        self.name = 'Weapon Attack'
        self.proficient = False
    
    def create(self, token, cost):
        del self
        new_instance = WeaponAttack()
        new_instance.token = token
        new_instance.name = token.weapon.name + ' attack'
        new_instance.range = new_instance.token.weapon.range
        new_instance.proficient = bool(token.weapon.name in token.proficiencies)
        new_instance.cost = cost
        return new_instance

    def attack(self, modifier = 0, advantage=False, disadvantage=False):
        #Choose correct attribute 
        if self.token.weapon.range > 1 or 'finesse' in self.token.weapon.attributes:
            mod = self.token.dex_bonus
        else:
            mod = self.token.str_bonus
        #Add proficiency
        if self.proficient: mod += self.token.proficiency
        #Roll with disadvantage for ranged weapons in melee 
        if self.token.weapon.range > 1 and self.target_square.distance(self.token_square)<=1: disadvantage=True
        roll = self._attack(mod, advantage=advantage, disadvantage=disadvantage) + self.token.weapon.atkmodifier + modifier
        return roll
    
    def damage(self, modifier = 0):
        roll = self.token.weapon.DamageDice.roll()
        if self.is_critical: roll += self.token.weapon.DamageDice.roll()
        if self.token.weapon.range > 1  or 'finesse' in self.token.weapon.attributes:
            roll += self.token.dex_bonus
        else:
            roll += self.token.str_bonus
        roll += self.token.weapon.dmgmodifier + modifier
        return roll

    def do(self, game):
        if self.target.is_triangulated[0]: 
            AtkMod = self.target.is_triangulated[1]
            DmgMod = self.target.is_triangulated[2]
        else: 
            AtkMod = 0
            DmgMod = 0
        AttackRoll = self.attack(modifier= AtkMod)
        game.gamelog.new_line(self.token.name + ' attacks ' + self.target.name)
        if AttackRoll >= self.target.ArmorClass:
            DamageRoll = self.damage(modifier= DmgMod)
            if self.is_critical: 
                if self.target.is_triangulated[0]: DamageRoll += D6.roll_dice(2)
                game.gamelog.new_line(str(AttackRoll) + ' to hit: Critical hit! '+ str(DamageRoll) + ' ' + self.token.weapon.DamageType + ' damage')
            else: game.gamelog.new_line(str(AttackRoll) + ' to hit: Hits for '+ str(DamageRoll) + ' ' + self.token.weapon.DamageType + ' damage')
            self.target.Hp -= DamageRoll
        else: 
            game.gamelog.new_line(str(AttackRoll) + ' to hit: Misses!')
        if self.cost == 'action': self.token.use_action()
        elif self.cost == 'bonus action': self.token.use_bonus_action()
        elif self.cost == 'reaction': self.token.use_reaction()

class TriangulateTarget(Attack):
    def __init__(self):
        super().__init__()
        self.name = 'Triangulate Target'

    def create(self, token, cost):
        del self
        new_instance = TriangulateTarget()
        new_instance.token = token
        new_instance.range = 30 // UNITLENGHT
        new_instance.cost = cost
        return new_instance

    def attack(self, modifier = 0, advantage=False, disadvantage=False):
        mod = self.token.spellcasting_bonus + self.token.proficiency
        if self.target_square.distance(self.token_square)<=1: disadvantage=True
        roll = self._attack(mod, advantage=advantage, disadvantage=disadvantage) + modifier
        return roll

    def do(self, game):
        if self.target.is_triangulated[0]: AtkMod = self.target.is_triangulated[1]
        else: AtkMod = 0
        AttackRoll = self.attack(modifier= AtkMod)
        game.gamelog.new_line(self.token.name + ' triangulates ' + self.target.name)
        if AttackRoll >= self.target.ArmorClass:
            self.target.is_triangulated = [True, self.token.int_bonus, D6.roll_dice(2)+self.token.proficiency]
            self.token.BeginTurnActions.append(EndTriangulated(self.token, self.target))
            game.gamelog.new_line(str(AttackRoll) + ' to hit: Success!')
        else: 
            game.gamelog.new_line(str(AttackRoll) + ' to hit: Misses!')
        if self.cost == 'action': self.token.use_action()
        elif self.cost == 'bonus action': self.token.use_bonus_action()
        elif self.cost == 'reaction': self.token.use_reaction()

class PropulsionBlast(Attack):
    def __init__(self):
        super().__init__()
        self.name = 'Propulsion Blast'

    def create(self, token, cost):
        del self
        new_instance = PropulsionBlast()
        new_instance.token = token
        new_instance.range = 20 // UNITLENGHT
        new_instance.cost = cost
        return new_instance

    def Failed_Save(self, modifier = 0, advantage=False, disadvantage=False):
        roll = D20.roll() + self.target.str_bonus    
        if roll >= self.token.spell_DC:
            return False
        else:
            return True

    def do(self, game):
        game.gamelog.new_line(self.token.name + ' uses Propulsion Blast')
        movement = self.token.current_movement
        direction = [(self.target_square.col-self.token_square.col), (self.target_square.row-self.token_square.row)]
        direction = [int(direction[0]//np.sqrt(direction[0]**2 + direction[1]**2)), int(direction[1]//np.sqrt(direction[0]**2 + direction[1]**2))]
        final_row = self.token_square.row-2*direction[1]
        final_col = self.token_square.col-2*direction[0]
        final_square = game.field.squares[min(final_row, ROWS-1)][min(final_col, COLS-1)]
        if not final_square.is_occupied():
            moveSelf = Move(self.token_square, final_square)
            game.field.move(self.token, moveSelf, game)
        else:
            final_square = game.field.squares[min(self.token_square.row-1*direction[1], ROWS-1)][min(self.token_square.col-1*direction[0], COLS-1)]
            if not final_square.is_occupied():
                moveSelf = Move(self.token_square, final_square)
                game.field.move(self.token, moveSelf, game)
            else:
                pass
        self.token.current_movement = movement
        if self.Failed_Save():
            game.gamelog.new_line(self.target.name + ' fails the saving throw')
            dmg = D6.roll() + self.token.proficiency
            self.target.Hp -= dmg
            game.gamelog.new_line(str(dmg) + ' force damage')
            movement = self.target.current_movement
            final_row = self.target_square.row+4*direction[1]
            final_col = self.target_square.col+4*direction[0]
            final_square = game.field.squares[min(final_row, ROWS-1)][min(final_col, COLS-1)]
            if not final_square.is_occupied():
                moveTarget = Move(self.target_square, final_square)
                game.field.move(self.target, moveTarget, game)
            else:
                final_square = game.field.squares[min(self.target_square.row+3*direction[1], ROWS-1)][min(self.target_square.col+3*direction[0], COLS-1)]
                if not final_square.is_occupied():
                    moveTarget = Move(self.target_square, final_square)
                    game.field.move(self.target, moveTarget, game)
                else: 
                    final_square = game.field.squares[min(self.target_square.row+2*direction[1], ROWS-1)][min(self.target_square.col+2*direction[0], COLS-1)]
                    if not final_square.is_occupied():
                        moveTarget = Move(self.target_square, final_square)
                        game.field.move(self.target, moveTarget, game)
                    else:
                        final_square = game.field.squares[min(self.target_square.row+1*direction[1], ROWS-1)][min(self.target_square.col+1*direction[0], COLS-1)]
                        if not final_square.is_occupied():
                            moveTarget = Move(self.target_square, final_square)
                            game.field.move(self.target, moveTarget, game)
                        else:
                            pass
            self.target.current_movement = movement
        else:
            game.gamelog.new_line(self.target.name + ' succeeds the saving throw')

    
        if self.cost == 'action': self.token.use_action()
        elif self.cost == 'bonus action': self.token.use_bonus_action()
        elif self.cost == 'reaction': self.token.use_reaction()


#Spells 
class Spell(Action):
    def __init__(self, name):
        super().__init__(name)

    def is_available(self, token, cost):
        has_available_slot = token.spellslots[self.required_spell_slot()]>0
        if has_available_slot:
            if cost == 'action':
                if token.has_bonus_cast:
                    return False
                else:
                    return token.has_action()
            elif cost == 'bonus action':
                if token.has_action_cast:
                    return False
                else:
                    return token.has_bonus_action()
            elif cost == 'reaction':
                return token.has_reaction()
            elif cost == None:
                return True
        else: 
            return False

class Firebolt(Attack):
    def __init__(self):
        super().__init__()
        self.name = 'Firebolt'    

    def is_available(self, token, cost):
        has_available_slot = token.spellslots[self.required_spell_slot()]>0
        if has_available_slot:
            if cost == 'action':
                if token.has_bonus_cast:
                    return False
                else:
                    return token.has_action()
            elif cost == 'bonus action':
                if token.has_action_cast:
                    return False
                else:
                    return token.has_bonus_action()
            elif cost == 'reaction':
                return token.has_reaction()
            elif cost == None:
                return True
        else: 
            return False

    def create(self, token, cost):
        del self
        new_instance = Firebolt()
        new_instance.token = token
        new_instance.range = 120 // UNITLENGHT
        new_instance.cost = cost
        return new_instance

    def attack(self, modifier=0, advantage=False, disadvantage=False):
        mod = self.token.spellcasting_bonus + self.token.proficiency
        #Roll with disadvantage if in melee 
        if self.target_square.distance(self.token_square)<=1: disadvantage=True
        roll = self._attack(mod, advantage=advantage, disadvantage=disadvantage) + modifier
        return roll
    
    def damage(self, modifier = 0):
        if self.token.level<5: num = 1
        elif self.token.level<11: num = 2
        elif self.token.level<17: num = 3
        else: num = 4
        roll = D10.roll_dice(num)
        if self.is_critical: roll += D10.roll_dice(num)
        return roll + modifier

    def do(self, game):
        if self.target.is_triangulated[0]: 
            AtkMod = self.target.is_triangulated[1]
            DmgMod = self.target.is_triangulated[2]
        else: 
            AtkMod = 0
            DmgMod = 0
        AttackRoll = self.attack(AtkMod)
        game.gamelog.new_line(self.token.name + ' casts Firebolt on ' + self.target.name)
        if AttackRoll >= self.target.ArmorClass:
            DamageRoll = self.damage(DmgMod)
            if self.is_critical: 
                if self.target.is_triangulated[0]: DamageRoll += D6.roll_dice(2)
                game.gamelog.new_line(str(AttackRoll) + ' to hit: Critical hit! '+ str(DamageRoll) + ' fire damage')
            else: game.gamelog.new_line(str(AttackRoll) + ' to hit: Hits for '+ str(DamageRoll) + ' fire damage')
            self.target.Hp -= DamageRoll
        else: 
            game.gamelog.new_line(str(AttackRoll) + ' to hit: Misses!')
        if self.cost == 'action': 
            self.token.use_action()
            self.token.has_action_cast = True
        elif self.cost == 'bonus action': 
            self.token.use_bonus_action()
            self.token.has_bonus_cast = True
        elif self.cost == 'reaction': self.token.use_reaction()

class CureWounds(Spell):
    def __init__(self):
        name = 'Cure Wounds'
        super().__init__(name)
        self.range = 5 // UNITLENGHT
        self.target = None
        self.target_square = None
        self.token_square = None
        self.available_targets = []
    
    def requires_target(self):
        return True
    
    def required_spell_slot(self):
        return 1
    
    def set_target(self, target, target_square, token_square):
        self.token_square = token_square
        self.target_square = target_square
        self.target = target

    def create(self, token, cost):
        del self
        new_instance = CureWounds()
        new_instance.token = token
        new_instance.cost = cost
        return new_instance

    def get_available_targets(self, token, field):
        for rows in field.squares:
            for square in rows:
                if square.token == token:
                    initial_square = square
        self.available_targets = [initial_square]
        for rows in field.squares:
            for square in rows:
                if self.is_valid_target(initial_square, square, square.token): 
                    if initial_square.distance(square)<=self.range:
                        if square not in self.available_targets: self.available_targets.append(square)
        return self.available_targets
    
    def is_valid_target(self, initial_square, final_square, token):
        if final_square.has_ally(self.token.team): 
            if final_square.distance(initial_square)<=self.range:
                return True
            else:
                return False
        else:
            return False
    
    def do(self, game):
        cure = D8.roll() + self.token.spellcasting_bonus
        self.target.Hp += cure
        if self.target.Hp > self.target.MaxHp: self.target.Hp = self.target.MaxHp
        game.gamelog.new_line(self.token.name + ' casts Cure Wounds on ' + self.target.name)
        game.gamelog.new_line(str(cure) + ' Hit Points restored')
        if self.cost == 'action': 
            self.token.use_action()
            self.token.has_action_cast = True
        elif self.cost == 'bonus action': 
            self.token.use_bonus_action()
            self.token.has_bonus_cast = True
        elif self.cost == 'reaction': self.token.use_reaction()
        self.token.spellslots[self.required_spell_slot()]-=1

class MagicMissiles(Spell):
    def __init__(self):
        name = 'Magic Missiles'
        super().__init__(name)
        self.range = 120 // UNITLENGHT
        self.target = None
        self.target_square = None
        self.token_square = None
        self.available_targets = []
    
    def requires_target(self):
        return True
    
    def required_spell_slot(self):
        return 1
    
    def set_target(self, target, target_square, token_square):
        self.token_square = token_square
        self.target_square = target_square
        self.target = target

    def create(self, token, cost):
        del self
        new_instance = MagicMissiles()
        new_instance.token = token
        new_instance.cost = cost
        return new_instance

    def get_available_targets(self, token, field):
        self.available_targets = []
        for rows in field.squares:
            for square in rows:
                if square.token == token:
                    initial_square = square
        for rows in field.squares:
            for square in rows:
                if self.is_valid_target(initial_square, square, square.token):
                        self.available_targets.append(square)
        return self.available_targets
    
    def is_valid_target(self, initial_square, final_square, token):
        if final_square.has_enemy(self.token.team): 
            if final_square.distance(initial_square)<=self.range:
                return True
            else:
                return False
        else:
            return False
    
    def do(self, game):
        Dmg = D4.roll_dice(3) + 3
        self.target.Hp -= Dmg
        game.gamelog.new_line(self.token.name + ' casts Magic Missiles on ' + self.target.name)
        game.gamelog.new_line(str(Dmg) + ' force damage')
        if self.cost == 'action': 
            self.token.use_action()
            self.token.has_action_cast = True
        elif self.cost == 'bonus action': 
            self.token.use_bonus_action()
            self.token.has_bonus_cast = True
        elif self.cost == 'reaction': self.token.use_reaction()
        self.token.spellslots[self.required_spell_slot()]-=1

class MistyStep(Spell):
    def __init__(self):
        name = 'Misty Step'
        super().__init__(name)
        self.range = 30 // UNITLENGHT
        self.target_square = None
        self.token_square = None
        self.available_targets = []
    
    def requires_target(self):
        return True
    
    def required_spell_slot(self):
        return 2
    
    def set_target(self, target, target_square, token_square):
        self.token_square = token_square
        self.target_square = target_square

    def create(self, token, cost):
        del self
        new_instance = MistyStep()
        new_instance.token = token
        new_instance.cost = cost
        return new_instance

    def get_available_targets(self, token, field):
        self.available_targets = []
        for rows in field.squares:
            for square in rows:
                if square.token == token:
                    initial_square = square
        for rows in field.squares:
            for square in rows:
                if self.is_valid_target(initial_square, square, square.token):
                    self.available_targets.append(square)
        return self.available_targets
    
    def is_valid_target(self, initial_square, final_square, token):
        if final_square.distance(initial_square)<=self.range and not final_square.is_occupied():
            return True
        else:
            return False
    
    def do(self, game):
        DontUseMovement = int(self.token.current_movement)
        move = Move(self.token_square, self.target_square)
        game.field.move(self.token, move, game)
        self.token.current_movement = DontUseMovement
        game.gamelog.new_line(self.token.name + ' casts Misty Step')
        if self.cost == 'action': 
            self.token.use_action()
            self.token.has_action_cast = True
        elif self.cost == 'bonus action': 
            self.token.use_bonus_action()
            self.token.has_bonus_cast = True
        elif self.cost == 'reaction': self.token.use_reaction()
        self.token.spellslots[self.required_spell_slot()]-=1



### Game Actions ###
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
            self.token.freemoving = False
            self.token.EndTurnActions.remove(EndDisengage(None))

class EndTriangulated(Action):
    def __init__(self, token, target, delay = 1):
        name = 'EndTriangulated'
        super().__init__(name)
        self.token = token
        self.target = target
        self.delay = delay
    
    def do(self, game):
        self.delay -= 1
        if self.delay <= 0:
            self.target.is_triangulated = [False, 0, 0]
            self.token.BeginTurnActions.remove(EndTriangulated(None, None))

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
                    'Weapon Attack': WeaponAttack(),
                    'Firebolt': Firebolt(),
                    'Cure Wounds': CureWounds(),
                    'Triangulate Target': TriangulateTarget(),
                    'Magic Missiles': MagicMissiles(),
                    'Misty Step': MistyStep(),
                    'Propulsion Blast': PropulsionBlast()}