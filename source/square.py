from config import *
import math

class Square:

    def __init__(self, row, col, token=None):
        self.row = row
        self.col = col
        self.token = token

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
    
    def is_occupied(self):
        return self.token != None
    
    def has_enemy(self, team):
        return self.is_occupied() and self.token.team != team

    def has_ally(self, team):
        return self.is_occupied() and self.token.team == team

    def distance(self, starting_square):
        col_dist = abs(self.row - starting_square.row)
        row_dist = abs(self.col - starting_square.col)
        distance = math.floor(math.sqrt(col_dist**2 + row_dist**2))
        return int(distance)

    @staticmethod
    def on_field(row, col):
        if row > ROWS or row < 0:
            return False
        if col > COLS or col < 0:
            return False
        return True

