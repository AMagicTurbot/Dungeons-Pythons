import random

class Agent():
    def __init__(self):
        pass

    def decision(available_actions, game):
        if game.active_player.current_movement < 1:
            action = available_actions[random.randint(8, len(available_actions)-1)]
        else:
            action = available_actions[random.randint(0, len(available_actions)-1)]
        return action