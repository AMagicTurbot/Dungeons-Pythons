from config import * 
import pygame
import sys
import time
from gamelog import Gamelog

class Buttons:
    def __init__(self):
        self.Gamestate0 = [
            Reset(position=(WIDTH+LOGWIDTH-100, HEIGHT-30)),
            Diagnostic(position=(WIDTH+0.1*LOGWIDTH, HEIGHT-30)),
            ActionsButtons(),
            BonusactionsButtons()
        ]


    
class Button:
    def __init__(self, name):
        self.name = name
        pass

    def __eq__(self, other):
        if other == None:
            return False
        else:
            return self.name == other.name

    def blit_button(self, surface):
        pygame.draw.rect(surface, self.rectcolor, self.rect)
        surface.blit(self.text, (self.x+(self.width-self.text.get_width())/2, self.y))

    def clicked(self, event):
        return self.rect.collidepoint(event.pos)

#Action Button
class Actionbutton(Button):
    def __init__(self, position, action):
        super().__init__(action.name)
        self.action = action
        self.fontsize = 15
        self.font = pygame.font.SysFont(LOGFONT, self.fontsize)
        self.content = self.name
        self.textcolor = (0, 0, 0)
        self.text = self.font.render(self.content, True, self.textcolor)
        self.x = position[0]
        self.y = position[1]
        self.rectcolor = (210, 210, 210)
        self.width = self.text.get_width()+10
        self.height = 20
        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))

    def blit_button(self, surface):
        pygame.draw.rect(surface, self.rectcolor, self.rect)
        surface.blit(self.text, (self.x+5, self.y))
    
    def on_click(self, game):
        self.action.do(game)
        

#Special Buttons

class ActionsButtons(Button):
    def __init__(self):
        super().__init__('ActionsButtons')
        self.fontsize = 20
        self.font = pygame.font.SysFont(LOGFONT, self.fontsize)
        self.content = 'Action'
        self.width = LOGWIDTH*4.5//12
        self.height = 30
        self.x = WIDTH + LOGWIDTH//12
        self.y = 50
        self.textcolor = (0, 0, 0)
        self.rectcolor = (110, 110, 110)
        self.bkgnd_color = ONColor
        self.text = self.font.render(self.content, True, self.textcolor)
        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))
        self.bkgnd = pygame.Rect((self.x, self.y), (self.width, self.height))
        
    def blit_button(self, surface):
        pygame.draw.rect(surface, self.bkgnd_color, self.bkgnd)
        pygame.draw.rect(surface, self.rectcolor, self.rect, 1)
        surface.blit(self.text, (self.x+(self.width-self.text.get_width())/2, 57))

    def on_click(self, game):
        if game.show_actions != 'Actions': game.show_actions = 'Actions'
        else: game.show_actions = None
    
    def switch_on(self):
        self.bkgnd_color = ONColor
    
    def switch_off(self):
        self.bkgnd_color = OFFColor


class BonusactionsButtons(Button):
    def __init__(self):
        super().__init__('BonusActionsButtons')
        self.fontsize = 15
        self.font = pygame.font.SysFont(LOGFONT, self.fontsize)
        self.content = 'Bonus Action'
        self.width = LOGWIDTH*4.5//12
        self.height = 30
        self.x = WIDTH + LOGWIDTH*6.5//12
        self.y = 50
        self.textcolor = (0, 0, 0)
        self.rectcolor = (110, 110, 110)
        self.bkgnd_color = ONColor
        self.text = self.font.render(self.content, True, self.textcolor)
        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))
        self.bkgnd = pygame.Rect((self.x, self.y), (self.width, self.height))


    def blit_button(self, surface):
        pygame.draw.rect(surface, self.bkgnd_color, self.bkgnd)
        pygame.draw.rect(surface, self.rectcolor, self.rect, 1)
        surface.blit(self.text, (self.x+(self.width-self.text.get_width())/2, 57))

    def on_click(self, game):
        if game.active_player.has_bonus_action():
            if game.show_actions != 'Bonus Actions': game.show_actions = 'Bonus Actions'
            else: game.show_actions = None
        else:
            pass

    def switch_on(self):
        self.bkgnd_color = ONColor
    
    def switch_off(self):
        self.bkgnd_color = OFFColor


class Reset(Button):
    def __init__(self, position):
        super().__init__('ResetButton')
        self.fontsize = 20
        self.font = pygame.font.SysFont(LOGFONT, self.fontsize)
        self.content = 'Reset'
        self.width = 0.9*self.fontsize*len(self.content)
        self.height = self.fontsize*1.3
        self.x = position[0]
        self.y = position[1]
        self.textcolor = (0, 0, 0)
        self.rectcolor = (110, 110, 110)
        self.text = self.font.render(self.content, True, self.textcolor)
        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))

    def on_click(self, game):
        print('Resetting game...')
    
class Diagnostic(Button):
    def __init__(self, position):
        super().__init__('DiagnosticButton')
        self.fontsize = 20
        self.font = pygame.font.SysFont(LOGFONT, self.fontsize)
        self.content = 'Empty'
        self.width = 0.65*self.fontsize*len(self.content)
        self.height = self.fontsize*1.3
        self.x = position[0]
        self.y = position[1]
        self.textcolor = (0, 0, 0)
        self.rectcolor = (160, 110, 110)
        self.text = self.font.render(self.content, True, self.textcolor)
        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))


    def on_click(self, game):
        print('nothing to see here...')
        pass
        # if game.AIDelay != 0:
        #     game.AIDelay = 0
        # else:
        #     game.AIDelay = AIDELAY
        

        