import pygame
import sys
import tracemalloc

from config import *
from tokens import *
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
                                    if action.requires_target():
                                        for row in range(ROWS):
                                            for col in range(COLS):
                                                if field.squares[row][col].token == action.token:
                                                    token_square = field.squares[row][col]
                                        dragger.save_initial(token_square)
                                        dragger.drag_target(action)
                                    else:
                                        action.button.on_click(game)
                                    self.show_all(screen, game, buttons)
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
                        if dragger.targetting:
                            if released_row < ROWS and releades_col < COLS:
                                initial = field.squares[dragger.initial_row][dragger.initial_col]
                                final = field.squares[released_row][releades_col]
                                #Check if action target is valid
                                if dragger.action.is_valid_target(initial, final, dragger.action.token):
                                    dragger.action.set_target(final.token, final, initial)
                                    dragger.action.do(game)
                                    self.show_all(screen, game, buttons)
                        else:
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, releades_col)
                            move = Move(initial, final)
                            #Check if possible move is valid
                            if field.valid_move(dragger.token, move):
                                #Move token
                                movedistance = field.move(dragger.token, move)
                                gamelog.new_line(str(dragger.token.name) + ' moves by ' + str(int((movedistance)*UNITLENGHT)) + ' ' + LENGHTNAME)
                                #Check for opportunity attacks
                                if not dragger.token.freemoving:
                                    for row in [dragger.initial_row-1, dragger.initial_row, dragger.initial_row+1]:
                                        for col in [dragger.initial_col-1, dragger.initial_col, dragger.initial_col+1]:
                                            if Square.on_field(row, col):
                                                if field.squares[row][col].has_enemy(dragger.token.team):
                                                    #Only melee weapons can make AoO
                                                    if field.squares[row][col].distance(final)>1:
                                                        if 'Weapon Attack' in dragger.token.action_list and field.squares[row][col].token.weapon.range <= 1:
                                                            action = ActionDatabase['Weapon Attack'].create(field.squares[row][col].token, 'reaction')
                                                            action.set_target(dragger.token, initial, field.squares[row][col])
                                                            if action.is_available(field.squares[row][col].token, 'reaction'): 
                                                                game.gamelog.new_line('Opportunity Attack!')
                                                                action.do(game)                                                            
                                self.show_all(screen, game, buttons)
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

            pygame.display.update()
            if MEMORYDIAG: print(tracemalloc.get_traced_memory())

            

            
main = Main()
main.mainloop()