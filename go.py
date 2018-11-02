#!/usr/bin/env python
# coding: utf-8

# # Inports
# 
# Usual imports.
# 

# In[1]:


import numpy as np
import math
import pygame
import os


# # Constants
# 
# Important constants for the game GO to improve code readability later on.

# In[2]:


black = -1
white = 1
empty = 0

display_w = 900
display_h = 900

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (210, 83, 83)
GREY = (200, 200, 200)
DARK_GREY = (75, 75, 75)
BROWN = (102, 51, 0)

line_width = 3
hoshi_r = 7

komi = 5.5


# # Inits
# 

# In[3]:


pygame.init()
screen = pygame.display.set_mode((display_w, display_h))
pygame.display.set_caption('GO')
clock = pygame.time.Clock()


# In[4]:


text = pygame.font.SysFont('monospace', 44)
background = pygame.image.load(os.path.join("textures","wood.jpg")).convert_alpha()

bs9 = pygame.image.load(os.path.join("textures","black9.png")).convert_alpha()
bs13 = pygame.image.load(os.path.join("textures","black13.png")).convert_alpha()
bs19 = pygame.image.load(os.path.join("textures","black19.png")).convert_alpha()

ws9 = pygame.image.load(os.path.join("textures","white9.png")).convert_alpha()
ws13 = pygame.image.load(os.path.join("textures","white13.png")).convert_alpha()
ws19 = pygame.image.load(os.path.join("textures","white19.png")).convert_alpha()


# # Classes
# 
# Definitions of useful classes

# In[5]:


class Board:
    game_board = None
    turn = 0
    passed = False
    finished = False
    size = None
    last_move = None
    
    white_capt = 0
    black_capt = 0
    
    def __init__(self, size):
        self.game_board = np.zeros((size,size), dtype=np.int8)
        self.size = size
        
    def get_situation(self):
        return self.game_board
    
    def get_board_size(self):
        return self.size
    
    def get_turn(self):
        return self.turn
    
    def get_player(self):
        if self.turn % 2 == 0:
            return black
        else:
            return white
    
    def get_group_array(self, row, col):
        if(self.game_board[row,col] == empty):
            player = self.get_player()
        else:
            player = self.game_board[row,col]
        
        check = np.full((1,), False)
        group_array = np.reshape(np.array((row,col)), (-1,2))
        
        while not check.all():
            k = np.argmax(check == False)
            
            pkt = group_array[k,:]
            
            i = pkt[0]
            j = pkt[1]
            
            if(i - 1 >= 0):                
                if(self.game_board[i-1,j] == player):
                    temp = np.reshape(np.array((i-1,j)), (-1,2))
                    already = False
                    
                    for l in range(group_array.shape[0]):
                        if((group_array[l,:] == temp).all()):
                            already = True
                            
                    if not already:
                        group_array = np.concatenate((group_array, temp))
                        check = np.concatenate((check, np.full((1,), False)))
                        

            if(i + 1 < self.size):
                if(self.game_board[i+1,j] == player):
                    temp = np.reshape(np.array((i+1,j)), (-1,2))
                    already = False
                    
                    for l in range(group_array.shape[0]):
                        if((group_array[l,:] == temp).all()):
                            already = True
                            
                    if not already:
                        group_array = np.concatenate((group_array, temp))
                        check = np.concatenate((check, np.full((1,), False)))


            if(j - 1 >= 0):
                if(self.game_board[i,j-1] == player):
                    temp = np.reshape(np.array((i,j-1)), (-1,2))
                    already = False
                    
                    for l in range(group_array.shape[0]):
                        if((group_array[l,:] == temp).all()):
                            already = True
                            
                    if not already:
                        group_array = np.concatenate((group_array, temp))
                        check = np.concatenate((check, np.full((1,), False)))


            if(j + 1 < self.size):
                if(self.game_board[i,j+1] == player):
                    temp = np.reshape(np.array((i,j+1)), (-1,2))
                    already = False
                    
                    for l in range(group_array.shape[0]):
                        if((group_array[l,:] == temp).all()):
                            already = True
                            
                    if not already:
                        group_array = np.concatenate((group_array, temp))
                        check = np.concatenate((check, np.full((1,), False)))
            
            check[k] = True
            
        return group_array
         
    
    def check_neighbors(self, row, col):
        free = 4
        same = 0
        
        if(row == 0 or row == self.size -1):
            free -= 1
        if(col == 0 or col == self.size -1):
            free -= 1
        
        player = self.get_player()
        
        if(row - 1 >= 0):
            if(self.game_board[row-1,col] == player):
                same += 1
                free -= 1
            elif(self.game_board[row-1,col] == player*(-1)):
                free -= 1
        
        if(row + 1 < self.size):
            if(self.game_board[row+1,col] == player):
                same += 1
                free -= 1
            elif(self.game_board[row+1,col] == player*(-1)):
                free -= 1
        
        if(col - 1 >= 0):
            if(self.game_board[row,col-1] == player):
                same += 1
                free -= 1
            elif(self.game_board[row,col-1] == player*(-1)):
                free -= 1
                
        if(col + 1 < self.size):
            if(self.game_board[row,col+1] == player):
                same += 1
                free -= 1
            elif(self.game_board[row,col+1] == player*(-1)):
                free -= 1
            
        return free, same
    
    
    def group_freedom(self, row, col):
        freedom = 0
        reset = False
        
        if(self.game_board[row, col] == empty):
            reset = True
            self.game_board[row,col] = self.get_player()
            
        group_array = self.get_group_array(row, col)
        
        for i in range(group_array.shape[0]):
            free, same = self.check_neighbors(group_array[i,0], group_array[i,1])
            freedom += free
        
        if reset:
            self.game_board[row,col] = empty
        
        return freedom
    
    def delete_group(self, group_array):
        captures = group_array.shape[0] 
        
        for i in range(captures):
            self.game_board[group_array[i,0], group_array[i,1]] = empty
            
        return captures
            
    
    def check_for_captures(self, row, col):
        player = self.get_player()
        
        if(row - 1 >= 0):
            if(self.game_board[row-1,col] == player*(-1)):
                temp = self.get_group_array(row-1, col)
                
                if(self.group_freedom(row-1, col) <= 0):
                    caps = self.delete_group(temp)
                
                    if player == white:
                        self.white_capt += caps
                    else:
                        self.black_capt += caps
        
        if(row + 1 < self.size):
            if(self.game_board[row+1,col] == player*(-1)):
                temp = self.get_group_array(row+1, col)
                
                if(self.group_freedom(row+1, col) <= 0):
                    caps = self.delete_group(temp)
                
                    if player == white:
                        self.white_capt += caps
                    else:
                        self.black_capt += caps
                
        if(col - 1 >= 0):
            if(self.game_board[row,col-1] == player*(-1)):
                temp = self.get_group_array(row, col-1)
                
                if(self.group_freedom(row, col-1) <= 0):
                    caps = self.delete_group(temp)
                
                    if player == white:
                        self.white_capt += caps
                    else:
                        self.black_capt += caps
                
        if(col + 1 < self.size):
            if(self.game_board[row,col+1] == player*(-1)):
                temp = self.get_group_array(row, col+1)
                
                if(self.group_freedom(row, col+1) <= 0):
                    caps = self.delete_group(temp)
                
                    if player == white:
                        self.white_capt += caps
                    else:
                        self.black_capt += caps
                
    
    
    def make_move(self, row=None, col=None, _pass=False):
        if self.finished:
            return "Game is finished."
        
        elif _pass:           
            if self.passed:
                self.finished = True
            
            self.passed = True
            p = self.get_player()
            self.turn += 1
            
            if(p == black):
                player = "Black "
            elif(p == white):
                player = "White "
                
            return player+"passed."
        
        elif self.game_board[row,col] != empty:
            return "Invalid move!"
        
        else:
            self.game_board[row,col] = self.get_player()
            self.check_for_captures(row, col)
            
            free = self.group_freedom(row, col)
            if(free <= 0):
                self.game_board[row,col] = empty
                return "Invalid move!"
            
            self.passed = False
            
            self.turn += 1
            self.last_move = (row,col)
            return


# In[6]:


class Button:
    name = "placeholder"
    name_img = None
    x = 0
    y = 0
    w = 200
    h = 50
    screen = None
    color = None
    pressed = False
    
    def __init__(self, screen, name, x,y,w,h, color, txt_color):
        self.screen = screen
        self.name = name
        self.name_img = text.render(str(self.name), 1, txt_color)
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.color = color
        
    def draw(self):
        if(self.pressed):
            pygame.draw.rect(screen, (np.array(self.color)*0.45).astype(np.uint8), (self.x, self.y, self.w, self.h), 0)
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h), 0)
            
        screen.blit(self.name_img, (self.x + int(self.w/2) - int(self.name_img.get_rect().width/2), self.y + int(self.h/2) - int(self.name_img.get_rect().height/2)))
        
    def check(self, x, y):
        if(self.x <= x and x <= self.x + self.w and self.y <= y and y <= self.y + self.h):
            return True
        else:
            return False
        
    def press(self):
        self.pressed = True
        
    def release(self):
        self.pressed = False


# # Game Functions
# 
# Functions to draw and play the game

# ### 1. Functions to convert pixel coordinates to array indices and the other way around.

# In[7]:


def intersection_to_pixel(size, i, j):
    if(size == 9):
        void = 88
    elif(size == 13):
        void = 61
    elif(size == 19):
        void = 42
        
    x = 50 + int(void/2) + j*void
    y = 50 + int(void/2) + i*void
    
    return (x,y)


# In[8]:


def pixel_to_intersection(size, x, y):
    if(size == 9):
        void = 88
    elif(size == 13):
        void = 61
    elif(size == 19):
        void = 42
    
    i = None
    j = None
    
    for k in range(size):
        if(x <= 50 + void + k*void and j is None):
            j = k
        if(y <= 50 + void + k*void and i is None):
            i = k
            
    return i, j    


# ### 2. Functions to draw stuff on the screen.

# In[9]:


def draw_hoshis(size, screen):
    if(size == 9):
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 2, 2), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 6, 6), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 2, 6), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 6, 2), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 4, 4), hoshi_r, 0)
    elif(size == 13):
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 3, 3), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 9, 9), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 3, 9), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 9, 3), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 6, 6), hoshi_r, 0)
    elif(size == 19):
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 3, 3), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 15, 15), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 3, 15), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 15, 3), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 9, 9), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 9, 15), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 15, 9), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 9, 3), hoshi_r, 0)
        pygame.draw.circle(screen, GREY, intersection_to_pixel(size, 3, 9), hoshi_r, 0)


# In[10]:


def print_(screen, txt):
    txt_img = text.render(str(txt), 1, WHITE)    
    pygame.draw.rect(screen, DARK_GREY, (0,850,900,50), 0)
    screen.blit(txt_img, (display_w/2- int(txt_img.get_rect().width/2), 850))


# In[11]:


def draw_turn(board, screen):
    turn = text.render(str(board.turn), 1, WHITE)
    w_capt = text.render(str(board.white_capt), 1, BLACK)
    b_capt = text.render(str(board.black_capt), 1, WHITE)
    
    
    
    pygame.draw.rect(screen, DARK_GREY, (0,0,900,50), 0)
    pygame.draw.rect(screen, BLACK, (0,0,b_capt.get_rect().width, 50), 0)
    pygame.draw.rect(screen, WHITE, (900-w_capt.get_rect().width,0,w_capt.get_rect().width, 50), 0)
    
    screen.blit(b_capt, (0,0))
    screen.blit(w_capt, (900 - w_capt.get_rect().width, 0))
    screen.blit(turn, (display_w/2- int(turn.get_rect().width/2), 0))


# In[12]:


def draw_board(board, screen):
    pygame.draw.rect(screen, DARK_GREY, (0,0,900,900), 0)
    screen.blit(background, (50,50))
    
    for i in range(board.size):
        pygame.draw.line(screen, GREY, intersection_to_pixel(board.size, i, 0), intersection_to_pixel(board.size, i, board.size-1), line_width)
        pygame.draw.line(screen, GREY, intersection_to_pixel(board.size, 0, i), intersection_to_pixel(board.size, board.size-1, i), line_width)
    
    draw_hoshis(board.size, screen)
    
    if(board.size==9):
        bs = bs9
        ws = ws9
    elif(board.size==13):
        bs = bs13
        ws = ws13
    elif(board.size==19):
        bs = bs19
        ws = ws19
    
    stone_rad = int(bs.get_rect().width/2)
    sit = board.get_situation()
    
    for i in range(board.size):
        for j in range(board.size):
            if(sit[i,j] == black):
                screen.blit(bs, np.subtract(intersection_to_pixel(board.size, i,j), (stone_rad, stone_rad)))
            elif(sit[i,j] == white):
                screen.blit(ws, np.subtract(intersection_to_pixel(board.size, i,j), (stone_rad, stone_rad)))
                
    last_move = board.last_move
    
    if(not (last_move is None or board.passed)):
        xy = intersection_to_pixel(board.size, last_move[0], last_move[1])

        if(board.get_player() == black):
            pygame.draw.circle(screen, BLACK, (xy[0], xy[1]), 9, 1)
        elif(board.get_player() == white):
            pygame.draw.circle(screen, WHITE, (xy[0], xy[1]), 9, 1)        


# ### Main Menu
# 
# to get the board size.
# * future selections are planned

# In[13]:


def main_menu():
    beendet = False
    start = False
    
    boardsize = 9
    
    b9 = Button(screen, "9x9", 100,370,200,60, DARK_GREY, WHITE)
    b13 = Button(screen, "13x13", 350,370,200,60, DARK_GREY, WHITE)
    b19 = Button(screen, "19x19", 600,370,200,60, DARK_GREY, WHITE)
    
    while not beendet and not start:
        
        b9.draw()
        b13.draw()
        b19.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                beendet = True
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    beendet = True
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_buttons = pygame.mouse.get_pressed()
                if mouse_buttons[0]:
                    pos = pygame.mouse.get_pos()
                    
                    if(b9.check(pos[0], pos[1])):
                        b9.press()
                    elif(b13.check(pos[0], pos[1])):
                        b13.press()
                    elif(b19.check(pos[0], pos[1])):
                        b19.press()
                        
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_buttons = pygame.mouse.get_pressed()
                if not mouse_buttons[0]:
                    pos = pygame.mouse.get_pos()
                    
                    if(b9.check(pos[0], pos[1])):
                        boardsize=9
                        start=True
                    else:
                        b9.release()
                        
                    if(b13.check(pos[0], pos[1])):
                        boardsize=13
                        start=True
                    else:
                        b13.release()
                        
                    if(b19.check(pos[0], pos[1])):
                        boardsize=19
                        start=True
                    else:
                        b19.release()
                        
        pygame.display.update()
        clock.tick(60)
        
    return Board(boardsize), start


# ### Gameloop
# The following function is the main game loop.
# This is where the magic happens.
# 
# * the game situation is drawn
# * inputs of the players are recorded
# 

# In[14]:


def gameloop(board):   
    beendet = False
    draw_board(board, screen)
    err = None
    
    while not board.finished and not beendet:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                beendet = True
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    beendet = True    
                if event.key == pygame.K_SPACE:
                    err = board.make_move(_pass=True)
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_buttons = pygame.mouse.get_pressed()
                if mouse_buttons[0]:
                    pos = pygame.mouse.get_pos()
                    if(pos[0] >= 50 and pos[1] >= 50 and pos[0] <= display_w-50 and pos[1] <= display_h-50):
                        i, j = pixel_to_intersection(board.size, pos[0], pos[1])
                        err = board.make_move(row=i, col=j)
    
                        
        
        draw_board(board, screen)
        draw_turn(board, screen)
        
        if(type(err) is str):
            print_(screen, err)
        
        err is None
        pygame.display.update()
        clock.tick(60)
        
    
    
    
    
    
    ###
    # Block to handle quitting and finishing a game
    ###
    
    if beendet:   
        pygame.quit()
    elif board.finished:
        while not beendet:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    beendet = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        beendet = True   
            print_(screen, "Game is finished.")
            
            pygame.display.update()
            clock.tick(60)
        
        pygame.quit()


# #  Main
# 
# In here the size of the board will be determined and the main game loop will be started accordingly.

# In[15]:


def main():
    board, start = main_menu()
    
    if(start):
        gameloop(board)

        
        
if __name__ == "__main__":
    main()

