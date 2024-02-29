import pygame
import sys

from config import *
from game import Game
from square import Square
from move import Move
from buttons import Buttons

class Main:

    def __init__(self):
        #Pygame inizialization
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH+LOGWIDTH,HEIGHT))
        pygame.display.set_caption('Dungeons&Pythons')
        self.game = Game()

    def show_all(self, screen, game, buttons):
        game.show_all(screen)
        for button in buttons.list:
            button.blit_button(screen)

    def mainloop(self):
        screen = self.screen
        game = self.game
        field = self.game.field
        dragger = self.game.dragger
        buttons = Buttons()
        gamelog = self.game.gamelog

        game.roll_initiative()
        gamelog.new_line(game.print_initiative())

        while True:
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
                            if token.can_move:
                                #Start dragging the token
                                dragger.save_initial(event.pos)
                                dragger.drag_token(token)
                                field.get_moves(token, clicked_row, clicked_col)
                                self.show_all(screen, game, buttons)
                    
                    #Click on a button
                    for button in buttons.list:
                        if button.clicked(event):
                            button.on_click(game)


                            #Special: Reset button
                            if button.name == 'ResetButton':
                                game = Game()
                                field = game.field
                                dragger = game.dragger
                                buttons = Buttons()
                                gamelog = game.gamelog
                                game.roll_initiative()
                                gamelog.new_line(game.print_initiative())
                    

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
                            gamelog.new_line(str(dragger.token.name) + ' moved by ' + str(int((movedistance)*UNITLENGHT)) + ' ' + LENGHTNAME)
                            self.show_all(screen, game, buttons)
                    dragger.release_token()

                #Quit event
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
            pygame.display.update()



main = Main()
main.mainloop()