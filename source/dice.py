
import random
import numpy as np
from config import *

class Dice:
    def __init__(self, faces, number=1):
        self.faces = faces
        self.number = number

    def roll_dice(self, number):
        if number == 1:
            roll = np.random.randint(self.faces)+1
            if PRINTDICE: print('Roll 1D' + str(self.faces) + ': ' + str(roll))
            return roll
        else:
            rolls = []
            for i in range(number):
                rolls.append(np.random.randint(self.faces)+1)
            if PRINTDICE: print('Roll '+str(number)+'D' + str(self.faces) + ': ' + str(rolls))
            return sum(rolls)

    def roll(self, num=1, advantage=False, disadvantage=False):
        num = num*self.number
        if advantage and disadvantage or not advantage and not disadvantage:
            return self.roll_dice(num)
        elif advantage:
            rolls = [self.roll_dice(num), self.roll_dice(num)]
            roll = max(rolls)
            if PRINTDICE: print('Advantage-> ' + str(roll))
            return roll
        elif disadvantage:
            rolls = [self.roll_dice(num), self.roll_dice(num)]
            roll = min(rolls)
            if PRINTDICE: print('Disadvantage-> ' + str(roll))
            return roll
        
        

D20 = Dice(20)
D12 = Dice(12)
D10 = Dice(10)
D8 = Dice(8)
D6 = Dice(6)
D4 = Dice(4)
D6x3 = Dice(6, number=3)
