class Move:

    def __init__(self, initial, final):
        self.initial = initial  #Squares
        self.final = final

    def __str__(self):
        s = ''
        s += f'({self.initial.row}, {self.initial.col})'
        s += f' -> ({self.final.row}, {self.final.col})'
        return s

    def __eq__(self, other):
        return self.initial == other.initial and self.final == other.final

    def lenght(self):
        return int(self.final.distance(self.initial))


