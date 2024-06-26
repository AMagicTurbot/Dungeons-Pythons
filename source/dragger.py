import pygame
from square import Square
from tokens import Target
from config import *

class Dragger:

    def __init__(self):
        self.token = None
        self.action = None
        self.targetting = False
        self.dragging = False
        self.mouseX = 0
        self.mouseY = 0
        self.initial_row = 0
        self.initial_col = 0

    def update_blit(self, surface):
        img = pygame.image.load(self.token.texture)
        img_center = self.mouseX, self.mouseY
        self.token.texture_rect = img.get_rect(center=img_center)
        surface.blit(img, self.token.texture_rect)

    def update_mouse(self, pos):
        self.mouseX, self.mouseY = pos

    def save_initial(self, pos):
        if isinstance(pos, Square):
            self.initial_row = pos.row
            self.initial_col = pos.col
        else:
            self.initial_row = pos[1] // SQSIZE
            self.initial_col = pos[0] // SQSIZE

    def drag_token(self, token):
        self.token = token
        self.dragging = True

    def drag_target(self, action):
        self.token = Target()
        self.action = action
        self.dragging = True
        self.targetting = True

    def release_token(self):
        self.token = None
        self.action = None
        self.dragging = False
        self.targetting = False