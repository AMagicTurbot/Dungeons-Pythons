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

    def decision(available_actions, game):
        pass

    def random_decision(available_actions, game):
        if game.active_player.current_movement < 1:
            action = available_actions[random.randint(8, len(available_actions)-1)]
        else:
            action = available_actions[random.randint(0, len(available_actions)-1)]
        return action

class RandomAgent(Agent):
    def __init__(self):
        super().__init__()

    def decision(available_actions, game):
        return Agent.random_decision(available_actions, game)

class AIAgent(Agent):
    def __init__(self):
        super().__init__()
        self.n_games = 0
        self.epsilon = 0    #Randomness
        self.gamma = 0.9      #Discount Rate, <1
        self.memory = deque(maxlen=MAX_MEMORY)  #If we exceed MAX_MEMORY it will popleft() it, deleting old data
        self.model = Linear_QNet(10, 256, 1)
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
            #Num of available actions
            len(game.get_agent_actions()),
            #Self status
            player.Hp//player.MaxHp,
            player.current_movement//player.speed,
            int(player.has_action()),
            int(player.has_bonus_action()),
            #Enemy status
            enemy_square.distance(player_square),
            enemy_square.row - player_square.row,
            enemy_square.col - player_square.col,
            enemy.Hp//enemy.MaxHp,
            int(enemy.is_dodging)
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

    def get_action(self, game, state):
        available_actions = game.get_agent_actions()

        self.epsilon = 80 - self.n_games #Sets tradeoff exploration/exploitation; Vary 80 dep on how many games you want to train for
        if random.randint(0, 200)<self.epsilon: #Lower epsilon => less randomness
            if game.active_player.current_movement < 1:
                action_index = random.randint(8, len(available_actions)-1)
            else:
                action_index = random.randint(0, len(available_actions)-1)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            action_index = int(prediction.item())

        return action_index


class Main():
    def __init__(self):
        global screen
        #Pygame inizialization
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH+LOGWIDTH,HEIGHT))
        screen = self.screen
        pygame.display.set_caption('Dungeons&Pythons')

    def plot(scores, mean_scores):
        display.clear_output(wait=True)
        display.display(plt.gcf())
        plt.clf()
        plt.title('Training...')
        plt.xlabel('Number of Games')
        plt.ylabel('Score')
        plt.plot(scores)
        plt.plot(mean_scores)
        plt.ylim(ymin=-50)
        plt.text(len(scores)-1, scores[-1], str(scores[-1]))
        plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
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
        total_score = 0
        record = 0
        agent = AIAgent()
        player_agent = RandomAgent()

        print('Training Initialized')
        while True:
            game.get_available_actions()
            self.update_screen(screen, game, buttons)

            #AI choice (note that AI controls "enemies")
            if game.active_player.team == 'players':
                choice = RandomAgent.decision(game.get_agent_actions(), game)
                reward, game_ended, score = game.take_action(choice)

            if game.active_player.team == 'enemies':
                available_actions = game.get_agent_actions()
                #Get old state
                state_old = agent.get_state(game)

                #Get available actions
                final_move = agent.get_action(game, state_old)

                #Choose and perform an action
                reward, game_ended, score = game.take_action(available_actions[final_move])
                state_new = agent.get_state(game)

                #Train short memory (1 step)
                agent.train_short_memory(state_old, final_move, reward, state_new, game_ended)

                #Store training data
                agent.remember(state_old, final_move, reward, state_new, game_ended)
            
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
                plot_scores.append(score)
                total_score += score
                mean_score = total_score / agent.n_games
                plot_mean_scores.append(mean_score)
                Main.plot(plot_scores, plot_mean_scores)

                self.start_game()

if __name__ == '__main__':
    main = Main()
    main.train()