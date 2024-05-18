import pygame

from config import *
from dice import *
from tokens import Creature, Target
from field import Field
from dragger import Dragger
from gamelog import Gamelog
from actions import *
from buttons import Buttons, Actionbutton


class Game:

    def __init__(self, level):
        self.level = level
        self.field = Field(self.level)
        self.dragger = Dragger()
        self.gamelog = Gamelog()
        self.buttons = Buttons()

        self.initiative_order = []
        self.active_player = self.field.playable_tokens[0]
        self.show_actions = None
        self.turns = 0

        #AI variables
        self.game_ended = False
        self.AIDelay = AIDELAY
        self.PreviousTurnHP = self.active_player.Hp

    #Gamestate methods
    def take_action(self, moveset, valid):
        reward = 0
        score = 0

        if not valid: #reward -10 if moveset is invalid
            return -10, self.game_ended, score

        for action in moveset:
            if action.requires_target():
                saved_target_hp = action.target.Hp

            if isinstance(action, Movement):
                for row in self.field.squares:
                    for square in row:
                        if square.token == self.active_player:
                            initial_player_square = square
                        if square.has_enemy(self.active_player.team):
                            enemy_square = square

            action.do(self)

            #Rewards   
            if isinstance(action, Attack) or isinstance(action, MagicMissiles): # +6 for attacking, to be removed
                reward += 6
            if action.requires_target(): 
                if action.target.Hp < saved_target_hp and action.target.team!=self.active_player.team: # +9 for hitting
                    reward+= 9
                if action.target.Hp <= 0: # +10 for killing
                    reward+= 15
        if self.active_player.weapon.name == 'Morning Star':
            reward += 3
            # if isinstance(action, Movement) and self.active_player.weapon.range<2: # +3 for getting closer
            #     for row in self.field.squares:
            #         for square in row:
            #             if square.token == self.active_player:
            #                 player_square = square
            #     if player_square.distance(enemy_square) < initial_player_square.distance(enemy_square) and initial_player_square.distance(enemy_square)>self.active_player.weapon.range:
            #         reward += 5

        time.sleep(self.AIDelay)
        if reward == 0 or reward == 3:
            reward = -10
        # reward -= self.turns//2
        
        #End game
        if len(self.initiative_order)==1:
            if self.initiative_order[0].team  == 'enemies':
                print('Enemies win!')
                score = 100-self.turns
            elif self.initiative_order[0].team == 'players':
                print('Players win!')
                score = 0
            self.game_ended = True

        # print('AI reward: ' + str(reward))
        return reward, self.game_ended, score

    #Blit methods
    def show_all(self, surface):
        self.show_field(surface)
        self.show_interface(surface)
        self.show_tokens(surface)
        self.show_moves(surface)
        self.show_gamelog(surface)

    def show_field(self, surface):
        #Load bckgrnd image
        if BACKGROUND != None:
            bgnd = pygame.image.load(BACKGROUND)
            surface.blit(bgnd, (0, 0))
        else:
            surface.fill((253,253,253)) #White
        #Show game grid
        for row in range(ROWS):
            for col in range(COLS):
                rect = (col*SQSIZE, row*SQSIZE , SQSIZE, SQSIZE)
                pygame.draw.rect(surface, (0,0,0), rect, 1) #Black borders

    def show_tokens(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.field.squares[row][col].is_occupied():
                    token = self.field.squares[row][col].token
                    if token is not self.dragger.token: #Don't show dragged pieces
                        #Token
                        img = pygame.image.load(token.texture)
                        img_center = col*SQSIZE+SQSIZE//2, row*SQSIZE+SQSIZE//2
                        token.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, token.texture_rect)
                        #Hp bar
                        if isinstance(token, Creature):
                            HPWidth = (token.Hp/token.MaxHp)*SQSIZE
                            HPRect = pygame.Rect((col*SQSIZE, row*SQSIZE), (HPWidth, 0.1*SQSIZE))
                            EmpyRect = pygame.Rect((col*SQSIZE, row*SQSIZE), (SQSIZE, 0.1*SQSIZE))
                            pygame.draw.rect(surface, LOGBKGNDCOLOR, EmpyRect)
                            pygame.draw.rect(surface, ONColor, HPRect)
                        
    def show_moves(self, surface):
        if self.dragger.dragging and self.dragger.token.can_move:
            token = self.dragger.token
            if token.team == 'players':
                color = PlayersCOLOR
            else:
                color = EnemiesCOLOR
            for move in token.moves:
                rect = (move.final.col*SQSIZE, move.final.row*SQSIZE , SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect, 4)
        elif self.dragger.dragging and self.dragger.targetting:
            if self.dragger.token.team == 'players':
                color = PlayersCOLOR
            else:
                color = EnemiesCOLOR
            for square in self.dragger.action.available_targets:
                TargetImg = Target()
                img = pygame.image.load(TargetImg.texture)
                img_center = ((square.col+0.5)*SQSIZE, (square.row+0.5)*SQSIZE)
                surface.blit(img, img.get_rect(center=img_center))            

    def show_interface(self, surface):
        #Current level
        CurrentLevelText = self.gamelog.font.render('Currently on Level ' + str(self.level), True, self.gamelog.textcolor)
        surface.blit(CurrentLevelText, (self.gamelog.x, self.gamelog.y*0.95))
        #Active player
        ActivePlayerColor = PlayersCOLOR if self.active_player.team == 'players' else EnemiesCOLOR
        ActivePlayerText = self.gamelog.font.render('Current player: ' + str(self.active_player), True, ActivePlayerColor)
        surface.blit(ActivePlayerText, (self.gamelog.x, 10))
        #Movement
        MovementText = self.gamelog.font.render('Movement: ' + str(self.active_player.current_movement*UNITLENGHT) + ' ' + LENGHTNAME, True, self.gamelog.textcolor)
        surface.blit(MovementText, (self.gamelog.x, 30))
        #Actions
        AColor = ONColor if self.active_player.has_action() else OFFColor
        AText = self.gamelog.font.render('Action', True, (50, 50, 50))
        surface.blit(AText, (WIDTH+LOGWIDTH//8+(LOGWIDTH//3-AText.get_width())/2, 60))
        #Bonus Actions
        ARect = pygame.Rect((WIDTH + LOGWIDTH*7//12, 50), (LOGWIDTH//3, 30))
        AColor = ONColor if self.active_player.has_bonus_action() else OFFColor
        AText = self.gamelog.font.render('Bonus Action', True, (50, 50, 50))
        pygame.draw.rect(surface, ONColor, ARect)
        surface.blit(AText, (WIDTH+LOGWIDTH*7//12+(LOGWIDTH//3-AText.get_width())/2, 60))

    def show_gamelog(self, surface):
        #Log box
        pygame.draw.rect(surface, self.gamelog.rectcolor, self.gamelog.rect)
        #Blit lines
        for l, line in enumerate(self.gamelog.log):
            if len(line)<=self.gamelog.maxchar:
                text = self.gamelog.font.render(line[0:self.gamelog.maxchar], True, self.gamelog.textcolor)
                surface.blit(text, self.gamelog.linepos[l])
            else:
                text = self.gamelog.font.render(line[0:self.gamelog.maxchar], True, self.gamelog.textcolor)
                surface.blit(text, self.gamelog.linepos[l])
                text = self.gamelog.font.render(line[self.gamelog.maxchar:2*self.gamelog.maxchar], True, self.gamelog.textcolor)
                surface.blit(text, (self.gamelog.linepos[l][0],self.gamelog.linepos[l][1]+self.gamelog.linedim[1]*0.5))


    #Turn methods
    def roll_initiative(self):
        self.initiative_order = []
        for token in self.field.playable_tokens:
                token.initiative = D20.roll() + token.dex_bonus
                for i, other in enumerate(self.initiative_order):
                    if other.initiative == token.initiative:
                        if token.dex_bonus >= other.dex_bonus:
                            self.initiative_order.insert(i, token)
                            break
                        else:
                            if i == len(self.initiative_order)-1:
                                self.initiative_order.append(token) 
                                break
                            else:
                                self.initiative_order.insert(i+1, token)
                                break
                    elif other.initiative < token.initiative:
                        self.initiative_order.insert(i, token)
                        break
                if token not in self.initiative_order: self.initiative_order.append(token)    
        self.active_player=self.initiative_order[0]
        self.active_player.turn_start()

        #Gamelog initiative
        initiative = 'Initiative: '
        for token in self.initiative_order:
            initiative += str(token) + ' ,'
        self.gamelog.new_line(initiative)
           
    def get_available_actions(self):
        #Consider token Actions list
        self.active_player.ActiveTurnActions = []
        for action_name in self.active_player.action_list:                      
            possible_action = ActionDatabase[action_name]                       
            if possible_action.is_available(self.active_player, 'action'):          #Check if action is available 
                action = possible_action.create(self.active_player,'action')        #Create action by binding token and cost   
                if action.requires_target(): 
                    action.get_available_targets(self.active_player, self.field)   
                    if len(action.available_targets)>0: 
                        self.active_player.ActiveTurnActions.append(action)                        
                else: self.active_player.ActiveTurnActions.append(action)
        #Consider token Bonus Actions
        self.active_player.ActiveTurnBonusActions = []
        for action_name in self.active_player.bonus_action_list:                
            possible_action = ActionDatabase[action_name]
            if possible_action.is_available(self.active_player, 'bonus action'):    #Check if action is available 
                action = possible_action.create(self.active_player,'bonus action')  #Create action by binding token and cost
                if action.requires_target(): 
                    action.get_available_targets(self.active_player, self.field)   
                    if len(action.available_targets)>0: self.active_player.ActiveTurnBonusActions.append(action)                        
                else: self.active_player.ActiveTurnBonusActions.append(action)    
        self.active_player.ActiveTurnActions.append(Pass().create(self.active_player,None))          


    def next_turn(self):
        #End-Turn events 
        for action in self.active_player.EndTurnActions:
            if action.is_available(self.active_player, None):
                action.do(self)
        #Advance Initiative
        index = self.initiative_order.index(self.active_player)
        if index < len(self.initiative_order)-1:
            self.active_player = self.initiative_order[index+1]
        else:
            self.active_player = self.initiative_order[0]
            self.turns += 1
        #Reset token turn variables
        self.active_player.turn_start()
        #Start-Turn events 
        for action in self.active_player.BeginTurnActions:
            if action.is_available(self.active_player, None):
                action.do(self)
        