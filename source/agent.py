import pygame
import sys
import tracemalloc
import time
import random
import torch
from collections import deque
import numpy as np
from matplotlib import pyplot as plt
from IPython import display

from config import *
from tokens import *
from actions import *
from game import Game
from square import Square
from move import Move
from buttons import Buttons, Actionbutton

from AI.model import Linear_QNet, QTrainer


MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.001

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


class AIAgent(Agent):
    def __init__(self):
        super().__init__()
        self.n_games = 0
        self.epsilon0 = 0                      # Randomness
        self.gamma = 0.9                      # Discount Rate, <1
        self.memory = deque(maxlen=MAX_MEMORY)  #If we exceed MAX_MEMORY it will popleft() it, deleting old data
        self.model = Linear_QNet(11, 256, 2)
        #Load trained AI
        if os.path.exists(os.path.join(AIPATH, 'model.pth')) and LOAD_AI:
            self.model.load_state_dict(torch.load(os.path.join(AIPATH, 'model.pth')))
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

        # elif final_move[1]== 1:
        #     #Magic Missiles
        #     for action in token.ActiveTurnActions:
        #         if action.name == 'Magic Missiles':
        #             action.set_target(enemy, enemy_square, token_square)
        #             moveset.append(action)
        #             valid = True
            
        # elif final_move[2]== 1:
        #     #Dodge
        #     for action in token.ActiveTurnActions:
        #         if action.name == 'Dodge':
        #             moveset.append(action)
        #             valid = True
            
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


class Main():
    def __init__(self):
        global screen
        #Pygame inizialization
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH+LOGWIDTH,HEIGHT))
        screen = self.screen
        pygame.display.set_caption('Dungeons&Pythons')

    def plot(scores, mean_scores, rewards):
        display.clear_output(wait=True)
        display.display(plt.gcf())
        plt.clf()
        plt.title('Training...')
        plt.xlabel('Number of Games')
        plt.ylabel('Score')
        plt.plot(scores, label = 'score')
        plt.plot(mean_scores, label = 'mean score')
        plt.plot(rewards, label = 'rewards')
        plt.ylim(ymin=-50)
        plt.text(len(scores)-1, scores[-1], str(scores[-1]))
        plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
        plt.legend()
        plt.show(block=False)
        plt.pause(.1)


    def start_game(self):
        global game, field, dragger, gamelog, buttons, screen
        self.game = Game()
        game = self.game
        field = game.field
        dragger = game.dragger
        gamelog = game.gamelog
        buttons = game.buttons
        game.roll_initiative()

    def update_screen(self, screen, game, buttons):
        game.show_all(screen)
        if game.active_player.has_action(): buttons.Gamestate0[2].switch_on()
        else: buttons.Gamestate0[2].switch_off()
        if game.active_player.has_bonus_action(): buttons.Gamestate0[3].switch_on() 
        else: buttons.Gamestate0[3].switch_off()
        for button in buttons.Gamestate0:
            button.blit_button(screen)

    def train(self):
        global game, field, dragger, gamelog, buttons, screen
        self.start_game()

        plot_scores = []
        plot_mean_scores = []
        plot_reward = []
        reward_log = []
        total_score = 0
        record = 0
        agent = AIAgent()
        player_agent = RandomAgent()

        while True:
            self.update_screen(screen, game, buttons)

            #AI choice (note that AI controls "enemies")
            if game.active_player.team == 'players':
                state_old = player_agent.get_state(game)
                final_move = player_agent.get_move(state_old)
                moveset, valid = player_agent.get_moveset(final_move, game)
                reward, game_ended, score = game.take_action(moveset, valid)

            if game.active_player.team == 'enemies':
                #Get old state
                state_old = agent.get_state(game)

                #Get available actions
                final_move = agent.get_move(state_old)

                #Choose and perform an action
                moveset, valid = agent.get_moveset(final_move, game)
                reward, game_ended, score = game.take_action(moveset, valid)
                state_new = agent.get_state(game)

                reward_log.append(reward)

                #Train short memory (1 step)
                agent.train_short_memory(state_old, final_move, reward, state_new, game_ended)

                #Store training data
                agent.remember(state_old, final_move, reward, state_new, game_ended)
            
            for token in game.initiative_order:
                if token.Hp<=0:
                    if token == game.active_player:
                        game.next_turn()
                    game.initiative_order.remove(token)
            pygame.display.update()

            if game.game_ended:
                agent.n_games += 1

                #Train long memory
                agent.train_long_memory()
                if score > record:
                    record = score
                    agent.model.save()

                #Plot results
                print('Game', agent.n_games, 'Score', score, 'Record:', record)
                print(reward_log)
                plot_scores.append(score)
                plot_reward.append(np.mean(reward_log))
                total_score += score
                mean_score = total_score / agent.n_games
                plot_mean_scores.append(mean_score)
                Main.plot(plot_scores, plot_mean_scores, plot_reward)

                reward_log = []
                self.start_game()

if __name__ == '__main__':
    main = Main()
    main.train()