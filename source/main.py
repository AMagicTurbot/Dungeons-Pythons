import pygame
import sys
import tracemalloc
import time

from agent import *
from config import *
from tokens import *
from game import Game
from square import Square
from move import Move
from buttons import Buttons, Actionbutton


class Main:
    def __init__(self):
        global screen
        #Pygame inizialization
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH+LOGWIDTH,HEIGHT))
        screen = self.screen
        pygame.display.set_caption('Dungeons&Pythons')

        self.enemies_win = 0
        self.players_win = 0
        self.AI = AIAgent()

    def plot(scores, mean_scores):
        display.clear_output(wait=True)
        display.display(plt.gcf())
        plt.clf()
        plt.title('Training...')
        plt.xlabel('Number of Games')
        plt.ylabel('Score')
        plt.plot(scores)
        plt.plot(mean_scores)
        plt.ylim(ymin=0)
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
        #Update A and BA game buttons color
        if game.active_player.has_action(): buttons.Gamestate0[2].switch_on()
        else: buttons.Gamestate0[2].switch_off()
        if game.active_player.has_bonus_action(): buttons.Gamestate0[3].switch_on() 
        else: buttons.Gamestate0[3].switch_off()
        #Blit Game buttons
        for button in buttons.Gamestate0:
            button.blit_button(screen)
        #Blit A and BA buttons
        i = 0
        if game.show_actions == 'Actions':
            for action in game.active_player.ActiveTurnActions:
                action.button = Actionbutton((10 + WIDTH + LOGWIDTH//12, 90 + i*25), action)
                action.button.blit_button(screen)
                i += 1
        elif game.show_actions == 'Bonus Actions':
            for action in game.active_player.ActiveTurnBonusActions:
                action.button = Actionbutton((10 + WIDTH + 3*LOGWIDTH//12, 90 + i*25), action)
                action.button.blit_button(screen)
                i += 1

    def mainloop(self):
        global game, field, dragger, gamelog, buttons, screen
        if MEMORYDIAG: tracemalloc.start()
    
        self.start_game()

        while not game.game_ended:
            game.get_available_actions()
            self.update_screen(screen, game, buttons)

            #AI choice
            if game.active_player.team == 'enemies':
                choice = self.AI.decision(game.get_agent_actions(), game)
                game.take_action(choice)
                time.sleep(1/game.AISpeed)
            # if game.active_player.team == 'players':
            #     choice = RandomAgent.decision(game.get_agent_actions(), game)
            #     game.take_action(choice)
            #     time.sleep(1/game.AISpeed)

            if dragger.dragging:
                dragger.update_blit(screen)
            
            #User activity
            for event in pygame.event.get():
                #Mouse click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    clicked_row = dragger.mouseY//SQSIZE
                    clicked_col = dragger.mouseX//SQSIZE

                   
                    #Click on field
                    if clicked_row < ROWS and clicked_col < COLS:
                        #Click on a token
                        if field.squares[clicked_row][clicked_col].is_occupied():
                            token = field.squares[clicked_row][clicked_col].token
                            if token.can_move and token == game.active_player:
                                #Start dragging the token
                                dragger.save_initial(event.pos)
                                dragger.drag_token(token)
                                field.get_moves(token, clicked_row, clicked_col)
                                self.update_screen(screen, game, buttons)

                    #Click outside field
                    else:
                        #Clicked on an active player button
                        if game.show_actions == 'Actions':          
                            for action in game.active_player.ActiveTurnActions:
                                if action.button.clicked(event):
                                    if action.requires_target():
                                        for row in range(ROWS):
                                            for col in range(COLS):
                                                if field.squares[row][col].token == action.token:
                                                    token_square = field.squares[row][col]
                                        dragger.save_initial(token_square)
                                        dragger.drag_target(action)
                                    else:
                                        action.button.on_click(game)
                                    self.update_screen(screen, game, buttons)
                                    break
                        elif game.show_actions == 'Bonus Actions':          
                            for action in game.active_player.ActiveTurnBonusActions:
                                if action.button.clicked(event):
                                    if action.requires_target():
                                        for row in range(ROWS):
                                            for col in range(COLS):
                                                if field.squares[row][col].token == action.token:
                                                    token_square = field.squares[row][col]
                                        dragger.save_initial(token_square)
                                        dragger.drag_target(action)
                                    else:
                                        action.button.on_click(game)
                                    self.update_screen(screen, game, buttons)
                                    break
                        
                        #Clicked on a gamestate button
                        for button in buttons.Gamestate0:
                            if button.clicked(event):
                                #Special: Reset button
                                if button.name == 'ResetButton':
                                    del game, buttons
                                    self.start_game()
                                button.on_click(game)
                                break                     
                    
                #Drag a token
                elif event.type == pygame.MOUSEMOTION:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                #Release
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        released_row = dragger.mouseY//SQSIZE
                        releades_col = dragger.mouseX//SQSIZE
                        if dragger.targetting:
                            if released_row < ROWS and releades_col < COLS:
                                initial = field.squares[dragger.initial_row][dragger.initial_col]
                                final = field.squares[released_row][releades_col]
                                #Check if action target is valid
                                if dragger.action.is_valid_target(initial, final, dragger.action.token):
                                    dragger.action.set_target(final.token, final, initial)
                                    dragger.action.do(game)
                                    self.update_screen(screen, game, buttons)
                        else:
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, releades_col)
                            move = Move(initial, final)
                            #Check if possible move is valid
                            if field.valid_move(dragger.token, move):
                                #Move token
                                movedistance = field.move(dragger.token, move, game)
                                gamelog.new_line(str(dragger.token.name) + ' moves by ' + str(int((movedistance)*UNITLENGHT)) + ' ' + LENGHTNAME)
                                                    
                                self.update_screen(screen, game, buttons)
                        dragger.release_token()

                #Quit event
                elif event.type == pygame.QUIT:
                    if MEMORYDIAG: tracemalloc.stop()
                    pygame.quit()
                    sys.exit()

            #State-based events
            for row in range(ROWS):
                for col in range(COLS):
                    if field.squares[row][col].is_occupied():
                        token = field.squares[row][col].token
                        if isinstance(token, Creature):
                            #Death
                            if token.Hp <= 0:
                                gamelog.new_line(token.name + ' died!')
                                if token == game.active_player:
                                    game.next_turn()
                                game.initiative_order.remove(token)
                                field.squares[row][col].token = tombstone(token.name)

                                #Game end
                                if all(token.team == game.initiative_order[0].team for token in game.initiative_order):
                                    if game.initiative_order[0].team == 'enemies':
                                        self.enemies_win +=1
                                        print('Enemies wins: ' + str(self.enemies_win))
                                    elif game.initiative_order[0].team == 'players':
                                        self.players_win +=1
                                        print('Players wins: ' + str(self.players_win))
                                    self.start_game()
                                    # game.game_ended = True
                


            pygame.display.update()
            if MEMORYDIAG: print(tracemalloc.get_traced_memory())

            
main = Main()
main.mainloop()