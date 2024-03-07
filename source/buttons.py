from config import * 
import pygame
import sys
from gamelog import Gamelog

class Buttons:
    def __init__(self):
        self.Gamestate0 = [
            Reset(position=(WIDTH+LOGWIDTH-100, HEIGHT-30)),
            Diagnostic(position=(WIDTH+0.1*LOGWIDTH, HEIGHT-30)),
            ActionsButtons(),
            BonusactionsButtons()
        ]

        self.ActivePlayerActions = []

    
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
        self.width = LOGWIDTH*5//12
        self.height = 20
        self.x = position[0]
        self.y = position[1]
        self.textcolor = (0, 0, 0)
        self.rectcolor = (210, 210, 210)
        self.text = self.font.render(self.content, True, self.textcolor)
        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))
    
    def on_click(self, game):
        self.action.do(game)
        

#Special Buttons

class ActionsButtons(Button):
    def __init__(self):
        super().__init__('ActionsButtons')
        self.fontsize = 20
        self.font = pygame.font.SysFont(LOGFONT, self.fontsize)
        self.content = 'Actions'
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
        if game.show_actions == None: game.show_actions = 'Actions'
        elif game.show_actions == 'Actions': game.show_actions = None
    
    def switch_on(self):
        self.color = ONColor
    
    def switch_off(self):
        self.color = OFFColor


class BonusactionsButtons(Button):
    def __init__(self):
        super().__init__('BonusActionsButtons')
        self.fontsize = 15
        self.font = pygame.font.SysFont(LOGFONT, self.fontsize)
        self.content = 'Bonus Actions'
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
        if game.show_actions == None: game.show_actions = 'Bonus Actions'
        elif game.show_actions == 'Bonus Actions': game.show_actions = None

    def switch_on(self):
        self.color = ONColor
    
    def switch_off(self):
        self.color = OFFColor


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
        self.content = 'Next Turn'
        self.width = 0.65*self.fontsize*len(self.content)
        self.height = self.fontsize*1.3
        self.x = position[0]
        self.y = position[1]
        self.textcolor = (0, 0, 0)
        self.rectcolor = (160, 110, 110)
        self.text = self.font.render(self.content, True, self.textcolor)
        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))

    def on_click(self, game):
        # print(game.active_player.action)
        game.next_turn()
        pass

        