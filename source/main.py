import pygame
import sys

from config import *
from game import Game
from square import Square
from move import Move

class Main:

    def __init__(self):
        #Pygame inizialization
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH+LOGWIDTH,HEIGHT))
        pygame.display.set_caption('Dungeons&Pythons')
        self.game = Game()

    def mainloop(self):
        screen = self.screen
        game = self.game
        field = self.game.field
        dragger = self.game.dragger
        buttons = self.game.buttons
        gamelog = self.game.gamelog

        while True:
            game.show_all(screen)
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
                                game.show_all(screen)
                    
                    #Click on a button
                    for button in buttons.list:
                        if button.clicked(event):
                            button.on_click()


                            #Special: Reset button
                            if button.name == 'ResetButton':
                                game = Game()
                                field = game.field
                                dragger = game.dragger
                                buttons = game.buttons
                                gamelog = game.gamelog
                    

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
                            game.show_all(screen)
                    dragger.release_token()

                #Quit event
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
            pygame.display.update()



main = Main()
main.mainloop()