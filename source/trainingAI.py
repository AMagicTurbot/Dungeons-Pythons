
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

from AI.agent import *




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
        self.game = Game(level=3)
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
        wins = 0
        agent = AegisAIAgent()
        player_agent = AegisRandomAgent()

        while True:
            self.update_screen(screen, game, buttons)

            #AI choice to emulate player
            if game.active_player.team == 'players':
                state_old = player_agent.get_state(game)
                final_move = player_agent.get_move(state_old)
                moveset, valid = player_agent.get_moveset(final_move, game)
                try:reward, game_ended, score = game.take_action(moveset, valid, player_agent)
                except ValueError: self.start_game()

            #AI to be trained
            if game.active_player.team == 'enemies':
                #Get old state
                state_old = agent.get_state(game)

                #Get available actions
                final_move = agent.get_move(state_old)

                #Choose and perform an action
                moveset, valid = agent.get_moveset(final_move, game)
                try: reward, game_ended, score = game.take_action(moveset, valid, agent)
                except ValueError: self.start_game()
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
                if game.active_player.team == 'enemies' and score != 0:
                    wins += 1

                #Train long memory
                agent.train_long_memory()
                if score > record:
                    record = score
                    agent.model.save(file_name=(agent.name + 'model.pth'))

                #Plot results
                print('Game', agent.n_games, 'Score', score, 'Win%:', np.round(wins/agent.n_games*100))
                print(reward_log)
                if agent.n_games%1==0:
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