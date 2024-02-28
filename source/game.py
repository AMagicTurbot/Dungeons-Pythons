import pygame

from config import *
from init import Init
from field import Field
from dragger import Dragger
from buttons import Buttons
from gamelog import Gamelog

class Game:

    def __init__(self):
        self.field = Field()
        self.dragger = Dragger()
        self.buttons = Buttons()
        self.gamelog = Gamelog()

    def show_all(self, surface):
        self.show_field(surface)
        self.show_interface(surface)
        self.show_moves(surface)
        self.show_tokens(surface)
        self.show_gamelog(surface)

    def show_field(self, surface):
        #Load bckgrnd image
        if BACKGROUND != None:
            bgnd = pygame.image.load(BACKGROUND)
            surface.blit(bgnd, (0, 0))
        else:
            surface.fill((253,253,253)) #White
        #Show game grid
        for row in range(ROWS):
            for col in range(COLS):
                rect = (col*SQSIZE, row*SQSIZE , SQSIZE, SQSIZE)
                pygame.draw.rect(surface, (0,0,0), rect, 1) #Black borders

    def show_tokens(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.field.squares[row][col].is_occupied():
                    token = self.field.squares[row][col].token
                    if token is not self.dragger.token: #Don't show dragged pieces
                        img = pygame.image.load(token.texture)
                        img_center = col*SQSIZE+SQSIZE//2, row*SQSIZE+SQSIZE//2
                        token.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, token.texture_rect)

    def show_moves(self, surface):
        if self.dragger.dragging and self.dragger.token.can_move:
            token = self.dragger.token
            for move in token.moves:
                if token.team == 'players':
                    color = PlayersCOLOR
                else:
                    color = EnemiesCOLOR
                rect = (move.final.col*SQSIZE, move.final.row*SQSIZE , SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect, 4)

    def show_interface(self, surface):
        #Active player
        #Actions
        #Buttons
        for button in self.buttons.list:
            button.blit_button(surface)

    def show_gamelog(self, surface):
        #Log box
        pygame.draw.rect(surface, self.gamelog.rectcolor, self.gamelog.rect)
        #Blit lines
        for l, line in enumerate(self.gamelog.log):
            if len(line)<=self.gamelog.maxchar:
                text = self.gamelog.font.render(line[0:self.gamelog.maxchar], True, self.gamelog.textcolor)
                surface.blit(text, self.gamelog.linepos[l])
            else:
                text = self.gamelog.font.render(line[0:self.gamelog.maxchar], True, self.gamelog.textcolor)
                surface.blit(text, self.gamelog.linepos[l])
                text = self.gamelog.font.render(line[self.gamelog.maxchar:2*self.gamelog.maxchar], True, self.gamelog.textcolor)
                surface.blit(text, (self.gamelog.linepos[l][0],self.gamelog.linepos[l][1]+self.gamelog.linedim[1]*0.5))


    #Turn methods
    def roll_initiative(self):
        for token in self.field.playable_tokens:
            pass

    
    
