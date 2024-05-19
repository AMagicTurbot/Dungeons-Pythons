import pygame
import sys
import tracemalloc
import time
import random
import torch
from collections import deque
import numpy as np

from config import *
from tokens import *
from actions import *
from game import Game
from square import Square
from move import Move
from buttons import Buttons, Actionbutton

from AI.model import Linear_QNet, BiLinear_QNet, QTrainer

BATCH_SIZE = 1000
MAX_MEMORY = 100000

# LR should be a bit higher in the beginning and then go back to around 0.001
LR = 0.007
EPSILON = 0
GAMMA = 0.3

class Agent():
    def __init__(self):
        pass

    def get_state(self, game):
        pass

    def remember(self, state, action, reward, next_state, game_ended):
        pass

    def train_long_memory(self):
        pass

    def train_short_memory(self):
        pass

    def moveset(available_actions, game):
        pass

    def ConditionalMoveset(self, action):
        return action

class RandomAgent(Agent):
    def __init__(self):
        super().__init__()

    def get_state(self, game):
        player = game.active_player
        for row in game.field.squares:
            for square in row:
                if square.token == player:
                    player_square = square
                if square.has_enemy(player.team):
                    enemy = square.token
                    enemy_square = square
        state = [
            #Self status
            player.Hp//player.MaxHp,                        #0
            player_square.row,                              #1
            player_square.col,                              #2
            player.current_movement//player.speed,          #3
            int(player.has_action()),                       #4
            int(player.has_bonus_action()),                 #5
            #Enemy status   
            enemy_square.distance(player_square),           #6
            enemy_square.row,                               #7
            enemy_square.col,                               #8
            enemy.Hp//enemy.MaxHp,                          #9
            int(enemy.is_dodging)                           #10
        ]
        return np.array(state)

    def get_move(self, state):
        final_move = [0,0,0]
        move = random.randint(0,1)
        final_move[move]=1

        return final_move

    def get_moveset(self, final_move, game):
        #This method converts the logic AI choice (final_move) into a series of moves to be performed by game.take_action
        state_old = self.get_state(game)
        
        game.get_available_actions()
        token = game.active_player
        token_row = state_old[1]
        token_col = state_old[2]
        enemy_row = state_old[7]
        enemy_col = state_old[8]
        token_square = game.field.squares[token_row][token_col]
        enemy_square = game.field.squares[enemy_row][enemy_col]
        enemy = enemy_square.token
        
        moveset=[]
        valid = False

        if final_move[0] == 1:
            #Get in attack range and attack
            if state_old[6]>token.weapon.range:
                game.field.get_moves(token, token_row, token_col)
                distance_from_enemy = []
                for move in token.moves:
                    distance_from_enemy.append(np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col))
                move = token.moves[np.argmin(distance_from_enemy)]
                moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))

                token_square = game.field.squares[move.final.row][move.final.col]
                token_row = token_square.row
                token_col = token_square.col
            
            attack = WeaponAttack().create(token, 'action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack.set_target(enemy, enemy_square, token_square)
                moveset.append(attack)
            valid = True
            
        elif final_move[1]== 1:
            #Dodge
            for action in token.ActiveTurnActions:
                if action.name == 'Dodge':
                    moveset.append(action)
                    valid = True
            
        elif final_move[2]== 1:
            #Disengage and move away
            for action in token.ActiveTurnActions:
                if action.name == 'Disengage':
                    moveset.append(action)
                    valid = True
            for i in range(max([token_row, token_col])):
                    row_move = np.copysign(1, -(enemy_row-token_row))
                    col_move = np.copysign(1, -(enemy_col-token_col))
                    moveset.append(Movement(token_square, (row_move, col_move)).create(token, None))

        moveset.append(Pass().create(token,None))
        return moveset, valid

class SimpleAIAgent(Agent):
    def __init__(self):
        super().__init__()
        self.name = 'SimpleAI'
        self.n_games = 0
        self.epsilon0 = EPSILON               # Randomness
        self.gamma = GAMMA                    # Discount Rate, <1
        self.memory = deque(maxlen=MAX_MEMORY)  #If we exceed MAX_MEMORY it will popleft() it, deleting old data
        self.model = Linear_QNet(11, 256, 2)
        #Load trained AI
        if os.path.exists(os.path.join(AIPATH, (self.name + 'model.pth'))) and LOAD_AI:
            self.model.load_state_dict(torch.load(os.path.join(AIPATH, (self.name + 'model.pth'))))
            self.model.eval()
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        player = game.active_player
        for row in game.field.squares:
            for square in row:
                if square.token == player:
                    player_square = square
                if square.has_enemy(player.team):
                    enemy = square.token
                    enemy_square = square
        state = [
            #Self status
            player.Hp//player.MaxHp,                        #0
            player_square.row,                              #1
            player_square.col,                              #2
            player.current_movement//player.speed,          #3
            int(player.has_action()),                       #4
            int(player.has_bonus_action()),                 #5
            #Enemy status   
            enemy_square.distance(player_square),           #6
            enemy_square.row,                               #7
            enemy_square.col,                               #8
            enemy.Hp//enemy.MaxHp,                          #9
            int(enemy.is_dodging)                           #10
        ]
        return np.array(state)

    def remember(self, state, action, reward, next_state, game_ended):
        self.memory.append((state, action, reward, next_state, game_ended))

    def train_long_memory(self):
        if len(self.memory)>BATCH_SIZE:
            sample = random.sample(self.memory, BATCH_SIZE)
        else:
            sample = self.memory

        states, actions, rewards, next_states, games_ended = zip(*sample)
        self.trainer.train_step(states, actions, rewards, next_states, games_ended)

    def train_short_memory(self, state, action, reward, next_state, game_ended):
        self.trainer.train_step(state, action, reward, next_state, game_ended)

    def get_move(self, state):
        self.epsilon = self.epsilon0 - self.n_games #Sets tradeoff exploration/exploitation; Vary 80 dep on how many games you want to train for
        final_move = [0,0]
        if random.randint(0, 200)<self.epsilon: #Lower epsilon => less randomness
            move = random.randint(0,1)
            final_move[move]=1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move]=1

        return final_move

    def get_moveset(self, final_move, game):
        #This method converts the logic AI choice (final_move) into a series of moves to be performed by game.take_action
        state_old = self.get_state(game)

        game.get_available_actions()
        token = game.active_player
        token_row = state_old[1]
        token_col = state_old[2]
        enemy_row = state_old[7]
        enemy_col = state_old[8]
        token_square = game.field.squares[token_row][token_col]
        enemy_square = game.field.squares[enemy_row][enemy_col]
        enemy = enemy_square.token
        
        moveset=[]
        valid = False

        if final_move[0] == 1:
            #Get in attack range and attack
            if state_old[6]>token.weapon.range:
                game.field.get_moves(token, token_row, token_col)
                distance_from_enemy = []
                for move in token.moves:
                    distance_from_enemy.append(np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col))
                move = token.moves[np.argmin(distance_from_enemy)]
                moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))

                token_square = game.field.squares[move.final.row][move.final.col]
                token_row = token_square.row
                token_col = token_square.col
            
            attack = WeaponAttack().create(token, 'action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack.set_target(enemy, enemy_square, token_square)
                moveset.append(attack)
            valid = True

        elif final_move[1]== 1:
            #Disengage and move away
            for action in token.ActiveTurnActions:
                if action.name == 'Disengage':
                    moveset.append(action)
                    valid = True
            for i in range(max([token_row, token_col])):
                    row_move = np.copysign(1, -(enemy_row-token_row))
                    col_move = np.copysign(1, -(enemy_col-token_col))
                    moveset.append(Movement(token_square, (row_move, col_move)).create(token, None))

        moveset.append(Pass().create(token,None))
        return moveset, valid

class WeaponAIAgent(SimpleAIAgent):
    def __init__(self):
        super().__init__()
        self.name = 'WeaponAI'
        self.n_games = 0
        self.epsilon0 = EPSILON               # Randomness
        self.gamma = GAMMA                    # Discount Rate, <1
        self.memory = deque(maxlen=MAX_MEMORY)  #If we exceed MAX_MEMORY it will popleft() it, deleting old data
        self.model = Linear_QNet(12, 256, 3)
        #Load trained AI
        if os.path.exists(os.path.join(AIPATH, (self.name + 'model.pth'))) and LOAD_AI:
            self.model.load_state_dict(torch.load(os.path.join(AIPATH, (self.name + 'model.pth'))))
            self.model.eval()
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        player = game.active_player
        for row in game.field.squares:
            for square in row:
                if square.token == player:
                    player_square = square
                if square.has_enemy(player.team):
                    enemy = square.token
                    enemy_square = square
        state = [                                           #If the architecture of state is changed, state_old indexing must be updated
            #Self status
            player.Hp//player.MaxHp,                        #0
            player_square.row,                              #1
            player_square.col,                              #2
            player.current_movement//player.speed,          #3
            int(player.has_action()),                       #4
            int(player.has_bonus_action()),                 #5
            int(player.weapon.range>1),                     #6
            #Enemy status   
            enemy_square.distance(player_square),           #7
            enemy_square.row,                               #8
            enemy_square.col,                               #9
            enemy.Hp//enemy.MaxHp,                          #10
            int(enemy.is_dodging)                           #11
        ]
        return np.array(state)

    def get_move(self, state):
        self.epsilon = self.epsilon0 - self.n_games #Sets tradeoff exploration/exploitation; Vary 80 dep on how many games you want to train for
        final_move = [0,0,0]
        if random.randint(0, 200)<self.epsilon: #Lower epsilon => less randomness
            move = random.randint(0,len(final_move)-1)
            final_move[move]=1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move]=1

        return final_move

    def get_moveset(self, final_move, game):
        #This method converts the logic AI choice (final_move) into a series of moves to be performed by game.take_action
        state_old = self.get_state(game)

        game.get_available_actions()
        token = game.active_player
        token_row = state_old[1]
        token_col = state_old[2]
        enemy_row = state_old[8]
        enemy_col = state_old[9]
        token_square = game.field.squares[token_row][token_col]
        enemy_square = game.field.squares[enemy_row][enemy_col]
        enemy = enemy_square.token
        
        moveset=[]
        valid = False

        if final_move[0] == 1:
            #Get in melee and attack
            if token.weapon == Shortbow:
                token.weapon = Shortsword
                game.gamelog.new_line(token.name + ' wields its Shortsword')

            if state_old[7]>token.weapon.range:
                game.field.get_moves(token, token_row, token_col)
                distance_from_enemy = []
                for move in token.moves:
                    distance_from_enemy.append(np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col))
                move = token.moves[np.argmin(distance_from_enemy)]
                moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))

                token_square = game.field.squares[move.final.row][move.final.col]
                token_row = token_square.row
                token_col = token_square.col
            
            attack = WeaponAttack().create(token, 'action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack.set_target(enemy, enemy_square, token_square)
                moveset.append(attack)
            valid = True
            
        elif final_move[1]== 1:
            #Disengage and move away
            for action in token.ActiveTurnActions:
                if action.name == 'Disengage':
                    moveset.append(action)
                    valid = True
            for i in range(max([token_row, token_col])):
                    row_move = np.copysign(1, -(enemy_row-token_row))
                    col_move = np.copysign(1, -(enemy_col-token_col))
                    moveset.append(Movement(token_square, (row_move, col_move)).create(token, None))

        elif final_move[2] == 1:
            #Kite from a distance
            if token.weapon == Shortsword:
                token.weapon = Shortbow
                game.gamelog.new_line(token.name + ' draws its Shortbow')

            #Moving as far as possible from enemy
            game.field.get_moves(token, token_row, token_col)
            distance_from_enemy = []
            for move in token.moves:
                distance = np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col)
                if distance<token.weapon.range:
                    distance_from_enemy.append(distance)
                else:
                    distance_from_enemy.append(0)
            move = token.moves[np.argmax(distance_from_enemy)]
            moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))

            token_square = game.field.squares[move.final.row][move.final.col]
            token_row = token_square.row
            token_col = token_square.col
            
            #Attack
            attack = WeaponAttack().create(token, 'action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack.set_target(enemy, enemy_square, token_square)
                moveset.append(attack)
            valid = True

        moveset.append(Pass().create(token,None))
        return moveset, valid

class BugbearAIAgent(SimpleAIAgent):
    def __init__(self):
        super().__init__()
        self.name = 'BugbearAI'
        self.n_games = 0
        self.epsilon0 = EPSILON               # Randomness
        self.gamma = GAMMA                    # Discount Rate, <1
        self.memory = deque(maxlen=MAX_MEMORY)  #If we exceed MAX_MEMORY it will popleft() it, deleting old data
        self.model = Linear_QNet(12, 256, 3)
        #Load trained AI
        if os.path.exists(os.path.join(AIPATH, (self.name + 'model.pth'))) and LOAD_AI:
            self.model.load_state_dict(torch.load(os.path.join(AIPATH, (self.name + 'model.pth'))))
            self.model.eval()
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        player = game.active_player
        for row in game.field.squares:
            for square in row:
                if square.token == player:
                    player_square = square
                if square.has_enemy(player.team):
                    enemy = square.token
                    enemy_square = square
        state = [                                           #If the architecture of state is changed, state_old indexing must be updated
            #Self status
            player.Hp//player.MaxHp,                        #0
            player_square.row,                              #1
            player_square.col,                              #2
            player.current_movement//player.speed,          #3
            int(player.has_action()),                       #4
            int(player.has_bonus_action()),                 #5
            int(player.weapon.range>1),                     #6
            #Enemy status   
            enemy_square.distance(player_square),           #7
            enemy_square.row,                               #8
            enemy_square.col,                               #9
            enemy.Hp//enemy.MaxHp,                          #10
            int(enemy.is_dodging)                           #11
        ]
        return np.array(state)


    def get_move(self, state):
        self.epsilon = self.epsilon0 - self.n_games #Sets tradeoff exploration/exploitation; Vary 80 dep on how many games you want to train for
        final_move = [0,0,0]
        if random.randint(0, 200)<self.epsilon: #Lower epsilon => less randomness
            move = random.randint(0,len(final_move)-1)
            final_move[move]=1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move]=1

        return final_move

    def get_moveset(self, final_move, game):
        #This method converts the logic AI choice (final_move) into a series of moves to be performed by game.take_action
        state_old = self.get_state(game)

        game.get_available_actions()
        token = game.active_player
        token_row = state_old[1]
        token_col = state_old[2]
        enemy_row = state_old[8]
        enemy_col = state_old[9]
        token_square = game.field.squares[token_row][token_col]
        enemy_square = game.field.squares[enemy_row][enemy_col]
        enemy = enemy_square.token
        
        moveset=[]
        valid = False

        if final_move[0] == 1:
            #Get in melee and attack
            if token.weapon == Javelin:
                token.weapon = Morning_Star
                game.gamelog.new_line(token.name + ' wields its '+ str(token.weapon.name))

            if state_old[7]>token.weapon.range:
                game.field.get_moves(token, token_row, token_col)
                distance_from_enemy = []
                for move in token.moves:
                    distance_from_enemy.append(np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col))
                move = token.moves[np.argmin(distance_from_enemy)]
                moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))

                token_square = game.field.squares[move.final.row][move.final.col]
                token_row = token_square.row
                token_col = token_square.col
            
            attack = WeaponAttack().create(token, 'action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack.set_target(enemy, enemy_square, token_square)
                moveset.append(attack)
            valid = True
            
        elif final_move[1]== 1:
            #Disengage and move away
            for action in token.ActiveTurnActions:
                if action.name == 'Disengage':
                    moveset.append(action)
                    valid = True
            for i in range(max([token_row, token_col])):
                    row_move = np.copysign(1, -(enemy_row-token_row))
                    col_move = np.copysign(1, -(enemy_col-token_col))
                    moveset.append(Movement(token_square, (row_move, col_move)).create(token, None))

        elif final_move[2] == 1:
            #Kite from a distance
            if token.weapon == Morning_Star:
                token.weapon = Javelin
                game.gamelog.new_line(token.name + ' draws its ' + str(token.weapon.name))

            #Moving as far as possible from enemy
            game.field.get_moves(token, token_row, token_col)
            distance_from_enemy = []
            for move in token.moves:
                distance = np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col)
                if distance<token.weapon.range:
                    distance_from_enemy.append(distance)
                else:
                    distance_from_enemy.append(0)
            move = token.moves[np.argmax(distance_from_enemy)]
            moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))

            token_square = game.field.squares[move.final.row][move.final.col]
            token_row = token_square.row
            token_col = token_square.col
            
            #Attack
            attack = WeaponAttack().create(token, 'action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack.set_target(enemy, enemy_square, token_square)
                moveset.append(attack)
            valid = True

        moveset.append(Pass().create(token,None))
        return moveset, valid

class AegisAIAgent(SimpleAIAgent):
    def __init__(self):
        super().__init__()
        self.name = 'AegisAI'
        self.n_games = 0
        self.epsilon0 = EPSILON               # Randomness
        self.gamma = GAMMA                    # Discount Rate, <1
        self.memory = deque(maxlen=MAX_MEMORY)  #If we exceed MAX_MEMORY it will popleft() it, deleting old data
        self.model = BiLinear_QNet(13, 256, 5)
        #Load trained AI
        if os.path.exists(os.path.join(AIPATH, (self.name + 'model.pth'))) and LOAD_AI:
            self.model.load_state_dict(torch.load(os.path.join(AIPATH, (self.name + 'model.pth'))))
            self.model.eval()
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

        self.past_Hp = 74
    def get_state(self, game):
        player = game.active_player
        for row in game.field.squares:
            for square in row:
                if square.token == player:
                    player_square = square
                if square.has_enemy(player.team):
                    enemy = square.token
                    enemy_square = square
        state = [                                           #If the architecture of state is changed, state_old indexing must be updated
            #Self status
            player.Hp//player.MaxHp,                        #0
            player_square.row,                              #1
            player_square.col,                              #2
            player.ki_points,                               #3
            int(player.has_action()),                       #4
            int(player.has_bonus_action()),                 #5
            player.has_used_Hands_of_Harm,                  #6
            player.attacks_during_action,                   #7
            player.attacks_during_bonus_action,             #8
            #Enemy status   
            enemy_square.distance(player_square),           #9
            enemy_square.row,                               #10
            enemy_square.col,                               #11
            enemy.Hp//enemy.MaxHp,                          #12
        ]
        return np.array(state)

    def get_move(self, state):
        self.epsilon = self.epsilon0 - self.n_games #Sets tradeoff exploration/exploitation; Vary 80 dep on how many games you want to train for
        final_move = [0,0,0,0,0]
        if random.randint(0, 200)<self.epsilon: #Lower epsilon => less randomness
            move = random.randint(0,len(final_move)-1)
            final_move[move]=1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move]=1

        return final_move

    def get_moveset(self, final_move, game):
        #This method converts the logic AI choice (final_move) into a series of moves to be performed by game.take_action
        state_old = self.get_state(game)

        game.get_available_actions()
        token = game.active_player
        token_row = state_old[1]
        token_col = state_old[2]
        enemy_row = state_old[10]
        enemy_col = state_old[11]
        token_square = game.field.squares[token_row][token_col]
        enemy_square = game.field.squares[enemy_row][enemy_col]
        enemy = enemy_square.token
        enemy_distance = state_old[9]
        ki_points = state_old[3]
        
        moveset=[]
        valid = False

        self.will_use_Hands_of_Harm = False
        

        if final_move[0] == 1: #Make two attacks and a bonus action attack 
            valid = True
            #Always get in melee
            if enemy_distance>1 and token.current_movement>0:
                    game.field.get_moves(token, token_row, token_col)
                    distance_from_enemy = []
                    for move in token.moves:
                        distance_from_enemy.append(np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col))
                    move = token.moves[np.argmin(distance_from_enemy)]
                    moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))

                    token_square = game.field.squares[move.final.row][move.final.col]
                    token_row = token_square.row
                    token_col = token_square.col

            attack1 = MonkWeaponAttack().create(token, 'action')
            attack2 = MonkWeaponAttack().create(token, 'action')
            attack3 = MonkWeaponAttack().create(token, 'bonus action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack1.set_target(enemy, enemy_square, token_square)
                attack2.set_target(enemy, enemy_square, token_square)
                attack3.set_target(enemy, enemy_square, token_square)
                moveset.append(attack1)
                moveset.append(attack2)
                moveset.append(attack3)
            
        elif final_move[1] == 1: #Make two attacks and two bonus action attack 
            if token.ki_points>0:
                valid = True
            #Always get in melee
            if enemy_distance>1 and token.current_movement>0:
                    game.field.get_moves(token, token_row, token_col)
                    distance_from_enemy = []
                    for move in token.moves:
                        distance_from_enemy.append(np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col))
                    move = token.moves[np.argmin(distance_from_enemy)]
                    moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))

                    token_square = game.field.squares[move.final.row][move.final.col]
                    token_row = token_square.row
                    token_col = token_square.col

            attack1 = MonkWeaponAttack().create(token, 'action')
            attack2 = MonkWeaponAttack().create(token, 'action')
            attack3 = MonkWeaponAttack().create(token, 'bonus action')
            attack4 = MonkWeaponAttack().create(token, 'bonus action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack1.set_target(enemy, enemy_square, token_square)
                attack2.set_target(enemy, enemy_square, token_square)
                attack3.set_target(enemy, enemy_square, token_square)
                attack4.set_target(enemy, enemy_square, token_square)
                moveset.append(attack1)
                moveset.append(attack2)
                moveset.append(attack3)
                moveset.append(attack4)

        elif final_move[2] == 1: #Same as [0] but with Hands of Harm
            if ki_points>0:
                valid = True
            self.will_use_Hands_of_Harm = True
            #Always get in melee
            if enemy_distance>1 and token.current_movement>0:
                    game.field.get_moves(token, token_row, token_col)
                    distance_from_enemy = []
                    for move in token.moves:
                        distance_from_enemy.append(np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col))
                    move = token.moves[np.argmin(distance_from_enemy)]
                    moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))

                    token_square = game.field.squares[move.final.row][move.final.col]
                    token_row = token_square.row
                    token_col = token_square.col

            attack1 = MonkWeaponAttack().create(token, 'action')
            attack2 = MonkWeaponAttack().create(token, 'action')
            attack3 = MonkWeaponAttack().create(token, 'bonus action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack1.set_target(enemy, enemy_square, token_square)
                attack2.set_target(enemy, enemy_square, token_square)
                attack3.set_target(enemy, enemy_square, token_square)
                moveset.append(attack1)
                moveset.append(attack2)
                moveset.append(attack3)
                
        elif final_move[3] == 1: #Same as [1] but with Hands of Harm
            if token.ki_points>1:
                valid = True
            self.will_use_Hands_of_Harm = True
            #Always get in melee
            if enemy_distance>1 and token.current_movement>0:
                    game.field.get_moves(token, token_row, token_col)
                    distance_from_enemy = []
                    for move in token.moves:
                        distance_from_enemy.append(np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col))
                    move = token.moves[np.argmin(distance_from_enemy)]
                    moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))

                    token_square = game.field.squares[move.final.row][move.final.col]
                    token_row = token_square.row
                    token_col = token_square.col

            attack1 = MonkWeaponAttack().create(token, 'action')
            attack2 = MonkWeaponAttack().create(token, 'action')
            attack3 = MonkWeaponAttack().create(token, 'bonus action')
            attack4 = MonkWeaponAttack().create(token, 'bonus action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack1.set_target(enemy, enemy_square, token_square)
                attack2.set_target(enemy, enemy_square, token_square)
                attack3.set_target(enemy, enemy_square, token_square)
                attack4.set_target(enemy, enemy_square, token_square)
                moveset.append(attack1)
                moveset.append(attack2)
                moveset.append(attack3)
                moveset.append(attack4)
        
        elif final_move[4]== 1: #Dodge as a bonus action
            if ki_points>0:
                valid = True
            #Always get in melee
            if enemy_distance>1 and token.current_movement>0:
                    game.field.get_moves(token, token_row, token_col)
                    distance_from_enemy = []
                    for move in token.moves:
                        distance_from_enemy.append(np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col))
                    move = token.moves[np.argmin(distance_from_enemy)]
                    moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))
                    token_square = game.field.squares[move.final.row][move.final.col]
                    token_row = token_square.row
                    token_col = token_square.col

            attack1 = MonkWeaponAttack().create(token, 'action')
            attack2 = MonkWeaponAttack().create(token, 'action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack1.set_target(enemy, enemy_square, token_square)
                attack2.set_target(enemy, enemy_square, token_square)
                moveset.append(attack1)
                moveset.append(attack2)
            action = MonkDodge().create(token, 'bonus action')
            moveset.append(action)

        # if not valid:
        #     valid = True
        #     #Always get in melee
        #     if enemy_distance>1 and token.current_movement>0:
        #             game.field.get_moves(token, token_row, token_col)
        #             distance_from_enemy = []
        #             for move in token.moves:
        #                 distance_from_enemy.append(np.square(enemy_row-move.final.row)+np.square(enemy_col-move.final.col))
        #             move = token.moves[np.argmin(distance_from_enemy)]
        #             moveset.append(Movement(token_square, (move.final.row-token_row, move.final.col-token_col)).create(token, None))

        #             token_square = game.field.squares[move.final.row][move.final.col]
        #             token_row = token_square.row
        #             token_col = token_square.col

        #     attack1 = MonkWeaponAttack().create(token, 'action')
        #     attack2 = MonkWeaponAttack().create(token, 'action')
        #     attack3 = MonkWeaponAttack().create(token, 'bonus action')
        #     if token_square.distance(enemy_square)<=token.weapon.range:
        #         attack1.set_target(enemy, enemy_square, token_square)
        #         attack2.set_target(enemy, enemy_square, token_square)
        #         attack3.set_target(enemy, enemy_square, token_square)
        #         moveset.append(attack1)
        #         moveset.append(attack2)
        #         moveset.append(attack3)
            
        moveset.append(Pass().create(token,None))
        return moveset, valid

    def ConditionalMoveset(self, action):
        if isinstance(action, MonkWeaponAttack) and self.will_use_Hands_of_Harm:
            if not action.token.has_used_Hands_of_Harm:
                new_action = HandsofHarm().create(action.token, action.cost)
                new_action.set_target(action.target, action.target_square, action.token_square)
                return new_action
        return action

class AegisRandomAgent(AegisAIAgent):
    def __init__(self):
        super().__init__()
        self.name = 'RandomAegisAI'

    def get_move(self, state):
        final_move = [0,0,0,0,0]

        has_action = state[4]
        has_bonus_action = state[5]
        ki_points = state[3]
        attacks_during_action = state[7]
        attacks_during_bonus_action = state[8]
        has_used_Hands_of_Harm = state[6]
        
        valid_moves = [0,1,2,3,4]
        if not has_action:
            valid_moves.remove(0)
        if attacks_during_action<1 or not has_bonus_action:
            valid_moves.remove(1)
        if attacks_during_bonus_action<1 or ki_points<1 or not has_bonus_action:
            valid_moves.remove(2)
        if has_used_Hands_of_Harm or ki_points<1 or not has_action:
            valid_moves.remove(3)
        if ki_points<1 or not has_bonus_action:
            valid_moves.remove(4)

        if valid_moves != []:
            move = random.choice(valid_moves)
        else:
            move = 0
        final_move[move]=1

        return final_move
