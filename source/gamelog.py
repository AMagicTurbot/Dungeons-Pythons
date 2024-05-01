import pygame

from config import *


class Gamelog:
    def __init__(self):
        self.max_lenght = 10
        self.log = ['Gamestart. Roll Initiative!']

        #Box Parameters
        self.width = 0.9*LOGWIDTH 
        self.height = 4*SQSIZE
        self.x = WIDTH+0.05*LOGWIDTH
        self.y = 0.45*HEIGHT
        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))
        self.rectcolor = (210, 210, 210)
        
        #Text Parameters
        self.fontsize = int(0.4*self.height/self.max_lenght)
        self.font = pygame.font.SysFont(LOGFONT, self.fontsize)
        self.textcolor = (0, 0, 0)
        self.maxchar = int(self.width/self.fontsize*2.2)
        self.linedim = (0.9*self.width, self.height/self.max_lenght)  #Required to divide text over two lines
        self.linepos = [(1.005*self.x, (1.01*self.y+l*self.height/self.max_lenght)) for l in range(self.max_lenght)]
        
    
    def new_line(self, line):
        if len(self.log)<self.max_lenght:
            self.log.append(str(line))
        else:
            for l in range(self.max_lenght-1):
                self.log[l]=self.log[l+1]
            self.log[-1]=line

        

        
        
    