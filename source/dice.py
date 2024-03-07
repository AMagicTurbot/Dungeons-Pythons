
import random
import numpy as np

class Dice:
    def __init__(self, faces):
        self.faces = faces

    def roll_dice(self, number):
        if number == 1:
            return np.random.randint(self.faces)+1
        else:
            rolls = []
            for i in range(number):
                rolls.append(np.random.randint(self.faces)+1)
            return rolls

    def roll(self, num=1, advantage=False, disadvantage=False):
        if advantage and disadvantage or not advantage and not disadvantage:
            return self.roll_dice(num)
        elif advantage:
            rolls = [self.roll_dice(num), self.roll_dice(num)]
            print(rolls)
            return max(rolls)
        elif disadvantage:
            rolls = [self.roll_dice(num), self.roll_dice(num)]
            print(rolls)
            return min(rolls)
        
        

D20 = Dice(20)
D12 = Dice(12)
D10 = Dice(10)
D8 = Dice(8)
D6 = Dice(6)
D4 = Dice(4)
