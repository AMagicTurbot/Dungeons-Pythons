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

from AI.model import Linear_QNet, QTrainer

BATCH_SIZE = 1000
MAX_MEMORY = 100000

# LR should be a bit higher in the beginning and then go back to around 0.001
LR = 0.001
EPSILON = 0
GAMMA = 0.5

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
            
            attack = WeaponAttack().create(token, 'Action')
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
            
            attack = WeaponAttack().create(token, 'Action')
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

        return moveset

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

        self.trainer.train_step(state, action, reward, next_state, game_ended)


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
            
            attack = WeaponAttack().create(token, 'Action')
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
            attack = WeaponAttack().create(token, 'Action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack.set_target(enemy, enemy_square, token_square)
                moveset.append(attack)
            valid = True

        moveset.append(Pass().create(token,None))
        return moveset, valid

        return moveset

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

        self.trainer.train_step(state, action, reward, next_state, game_ended)


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
            
            attack = WeaponAttack().create(token, 'Action')
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
            attack = WeaponAttack().create(token, 'Action')
            if token_square.distance(enemy_square)<=token.weapon.range:
                attack.set_target(enemy, enemy_square, token_square)
                moveset.append(attack)
            valid = True

        moveset.append(Pass().create(token,None))
        return moveset, valid

        return moveset
