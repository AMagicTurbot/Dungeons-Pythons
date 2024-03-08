import pygame
import sys
import tracemalloc

from config import *
from game import Game
from square import Square
from move import Move
from buttons import Buttons, Actionbutton

class Main:

    def __init__(self):
        #Pygame inizialization
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH+LOGWIDTH,HEIGHT))
        pygame.display.set_caption('Dungeons&Pythons')
        self.game = Game()

    def show_all(self, screen, game, buttons):
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
        if MEMORYDIAG: tracemalloc.start()
        screen = self.screen
        game = self.game
        field = self.game.field
        dragger = self.game.dragger
        buttons = Buttons()
        gamelog = self.game.gamelog

        game.roll_initiative()
        gamelog.new_line(game.print_initiative())

        while True:
            game.get_available_actions()
            self.show_all(screen, game, buttons)

            if dragger.dragging:
                dragger.update_blit(screen)
                
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
                                self.show_all(screen, game, buttons)
                    
                    #Click outside field
                    else:
                        #Clicked on an active player button
                        if game.show_actions == 'Actions':          
                            for action in game.active_player.ActiveTurnActions:
                                if action.button.clicked(event):
                                    action.button.on_click(game)
                                    self.show_all(screen, game, buttons)
                                    break
                        elif game.show_actions == 'Bonus Actions':          
                            for action in game.active_player.ActiveTurnBonusActions:
                                if action.button.clicked(event):
                                    action.button.on_click(game)
                                    self.show_all(screen, game, buttons)
                                    break
                        
                        #Clicked on a gamestate button
                        for button in buttons.Gamestate0:
                            if button.clicked(event):
                                #Special: Reset button
                                if button.name == 'ResetButton':
                                    del game, buttons
                                    game = Game()
                                    field = game.field
                                    dragger = game.dragger
                                    buttons = Buttons()
                                    gamelog = game.gamelog
                                    game.roll_initiative()
                                    gamelog.new_line(game.print_initiative())
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
                        #Check if possible move is valid
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, releades_col)
                        move = Move(initial, final)
                        if field.valid_move(dragger.token, move):
                            #Move token
                            movedistance = field.move(dragger.token, move)
                            gamelog.new_line(str(dragger.token.name) + ' moves by ' + str(int((movedistance)*UNITLENGHT)) + ' ' + LENGHTNAME)
                            self.show_all(screen, game, buttons)
                        dragger.release_token()

                #Quit event
                elif event.type == pygame.QUIT:
                    if MEMORYDIAG: tracemalloc.stop()
                    pygame.quit()
                    sys.exit()

                #State-based events

            pygame.display.update()
            if MEMORYDIAG: print(tracemalloc.get_traced_memory())

            

            
main = Main()
main.mainloop()