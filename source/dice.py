
import random
import numpy as np

class Dice:
    def __init__(self):
        pass

    def roll_dice(self, faces, number):
        if number == 1:
            return np.random.randint(faces)+1
        else:
            rolls = []
            for i in range(number):
                rolls.append(np.random.randint(faces)+1)
            return rolls

    def rolld20(self):
        return self.roll_dice(20, 1)

