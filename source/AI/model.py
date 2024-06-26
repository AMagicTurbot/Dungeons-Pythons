import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
from config import *


class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = AIPATH
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class BiLinear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.lineari2h = nn.Linear(input_size, hidden_size)
        self.linearh2h = nn.Linear(hidden_size, hidden_size)
        self.linearh2o = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.lineari2h(x))
        x = F.relu(self.linearh2h(x))
        x = self.linearh2o(x)
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = AIPATH
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma 
        self.model = model

        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, game_ended):
        state = torch.tensor(state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            next_state = torch.unsqueeze(next_state, 0)
            game_ended = (game_ended, )
        
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(game_ended)):
            Q_new = reward[idx]
            if not game_ended:
                Q_new = reward[idx] + self.gamma*torch.max(self.model(next_state[idx]))

            target[idx]=Q_new
        
        self.optimizer.zero_grad() #Empty the gradient
        loss = self.criterion(target, pred)
        loss.backward() #Update gradients

        self.optimizer.step()
