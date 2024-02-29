from config import * 
import pygame
import sys
from gamelog import Gamelog

class Buttons:
    def __init__(self):
        self.list = [
            Reset(position=(WIDTH+LOGWIDTH-100, HEIGHT-30)),
            Diagnostic(position=(WIDTH+0.1*LOGWIDTH, HEIGHT-30))
        ]

        self.active = []

    
class Button:
    def __init__(self, name):
        self.name = name
        pass

    def blit_button(self, surface):
        pygame.draw.rect(surface, self.rectcolor, self.rect)
        surface.blit(self.text, (self.x+(self.width-self.text.get_width())/2, self.y))

    def clicked(self, event):
        return self.rect.collidepoint(event.pos)
    

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
        self.content = 'Diagnostic'
        self.width = 0.65*self.fontsize*len(self.content)
        self.height = self.fontsize*1.3
        self.x = position[0]
        self.y = position[1]
        self.textcolor = (0, 0, 0)
        self.rectcolor = (160, 110, 110)
        self.text = self.font.render(self.content, True, self.textcolor)
        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))

    def on_click(self, game):
        pass

        