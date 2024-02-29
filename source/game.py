import pygame

from config import *
from init import Init
from field import Field
from dragger import Dragger
from gamelog import Gamelog
from dice import Dice

class Game:

    def __init__(self):
        self.dice = Dice()
        self.field = Field()
        self.dragger = Dragger()
        self.gamelog = Gamelog()

        self.initiative_order = []
        self.active_player = self.field.playable_tokens[0]

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
        ActivePlayerColor = PlayersCOLOR if self.active_player.team == 'players' else EnemiesCOLOR
        ActivePlayerText = self.gamelog.font.render('Current player: ' + str(self.active_player), True, ActivePlayerColor)
        surface.blit(ActivePlayerText, (self.gamelog.x, 10))
        #Movement
        MovementText = self.gamelog.font.render('Movement: ' + str(self.active_player.current_movement*UNITLENGHT) + ' ' + LENGHTNAME, True, self.gamelog.textcolor)
        surface.blit(MovementText, (self.gamelog.x, 30))
        #Actions

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
        self.initiative_order = []
        for token in self.field.playable_tokens:
                token.initiative = self.dice.rolld20() + token.dex_bonus
                for i, other in enumerate(self.initiative_order):
                    if other.initiative == token.initiative:
                        if token.dex_bonus >= other.dex_bonus:
                            self.initiative_order.insert(i, token)
                            break
                        else:
                            if i == len(self.initiative_order)-1:
                                self.initiative_order.append(token) 
                                break
                            else:
                                self.initiative_order.insert(i+1, token)
                                break
                    elif other.initiative < token.initiative:
                        self.initiative_order.insert(i, token)
                        break
                if token not in self.initiative_order: self.initiative_order.append(token)    

    def print_initiative(self):
        initiative = 'Initiative: '
        for token in self.initiative_order:
            initiative += str(token) + '(' + str(token.initiative) + '), '
        return initiative
        
    def next_turn(self):
        index = self.initiative_order.index(self.active_player)
        if index < len(self.initiative_order):
            self.active_player = self.initiative_order[index+1]
        else:
            self.active_player = self.initiative_order[0]
    
