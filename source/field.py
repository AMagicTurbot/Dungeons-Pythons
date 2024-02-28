import numpy as np

from config import *
from init import *
from square import Square
from tokens import *
from move import Move

class Field:

    def __init__(self):
        self.squares = list([0 for col in range(COLS)] for row in range(ROWS))
        self._create()
        self.playable_tokens = []
        self._init_tokens()
    

    def movement_distance(self, token, move, calculating=False):
        numofdiag = 0
        initial=move.initial
        final=move.final
        if initial.row != final.row and initial.col != final.col:
            numofdiag = min(abs(final.row - initial.row), abs(final.col - initial.col))
            #Single movement by an even number of diagonals
            if numofdiag % 2 == 0: 
                distance = move.lenght()+numofdiag//2
            #Single movement by an odd number of diagonals
            else: 
                movement_cost = move.lenght()
                if token.has_moved_diagonally_once:
                    distance = movement_cost+numofdiag//2+numofdiag%2
                    if not calculating: token.has_moved_diagonally_once = False
                else:
                    distance = movement_cost+numofdiag//2
                    if not calculating: token.has_moved_diagonally_once = True
                    
        else:
            distance = move.lenght()
        return distance
    
    def move(self, token, move):
        initial = move.initial
        final = move.final
        #Update squares list with new token position
        self.squares[initial.row][initial.col].token = None
        self.squares[final.row][final.col].token = token
        #Consume movement speed
        movedistance = self.movement_distance(token, move)
        token.current_movement -= movedistance
        token.clear_moves()
        return movedistance

    def valid_move(self, token, move):
        return move in token.moves

    def get_moves(self, token, row, col):
        #Check if the token can move
        if token.can_move and token.current_movement != 0:
            initial_square = Square(row, col) 
            #Calculate all possible moves for that token
            possible_moves = []
            for rows in self.squares:
                for possible_square in rows:
                    move = Move(initial_square, possible_square)
                    distance = self.movement_distance(token, move, calculating=True)
                    if distance<=token.current_movement:
                        possible_moves.append((possible_square.row, possible_square.col))
            #Filter out invalid moves
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                #Check if the evaluated move is valid (out of range, occupied square)
                if Square.on_field(possible_move_row, possible_move_col):
                    if not self.squares[possible_move_row][possible_move_col].is_occupied():
                        #create a new move
                        final = Square(possible_move_row, possible_move_col)
                        move = Move(initial_square, final)
                        token.add_move(move)
        else:
            pass
   
    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _init_tokens(self):
        init = Init()
        for token in init.players:
            self.playable_tokens.append(token[0])
            self.squares[token[1]][token[2]] = Square(token[1],token[2], token[0])
        for token in init.enemies:
            self.playable_tokens.append(token[0])
            self.squares[token[1]][token[2]] = Square(token[1],token[2], token[0])
        for token in init.objects:
            self.squares[token[1]][token[2]] = Square(token[1],token[2], token[0])

    def add_token(self, token, row, col):
        self.squares[row][col] = Square(row, col, token)
