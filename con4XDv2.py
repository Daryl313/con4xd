import numpy as np
import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Initialize the font module
pygame.font.init()

GRAY = (211,211,211)
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0,102,255)
WHITE = (255,255,255)
GREEN = (0,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def draw_board(board, myfont, player1_used_bomb, player2_used_bomb):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, GRAY, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):        
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == 2: 
                pygame.draw.circle(screen, BLUE, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)

    # Add bomb usage labels
    if player1_used_bomb:
        bomb_label = myfont.render("(Bomb Used)", 1, RED)
        screen.blit(bomb_label, (10, 40))
    if player2_used_bomb:
        bomb_label = myfont.render("(Bomb Used)", 1, BLUE)
        screen.blit(bomb_label, (width - 150, 40))

def draw_player_labels(myfont):
    player1_label = myfont.render("Player 1", 1, RED)
    player2_label = myfont.render("Player 2", 1, BLUE)
    screen.blit(player1_label, (10, 10))
    screen.blit(player2_label, (width - 200, 10))

def remove_surrounding_pieces(board, row, col):
    for r in range(max(0, row - 1), min(ROW_COUNT, row + 2)):
        for c in range(max(0, col - 1), min(COLUMN_COUNT, col + 2)):
            board[r][c] = 0

SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)

myfont = pygame.font.SysFont("monospace", 30)

board = create_board()
print_board(board)
game_over = False
turn = 0

player1_used_bomb = False
player2_used_bomb = False
player1_used_bomb_last_turn = False
player2_used_bomb_last_turn = False

draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
draw_player_labels(myfont)
pygame.display.update()

bomb_event = False
use_bomb = False

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
            else:
                pygame.draw.circle(screen, BLUE, (posx, int(SQUARESIZE / 2)), RADIUS)

            draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
            draw_player_labels(myfont)
            pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN and not bomb_event:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))

            posx = event.pos[0]
            col = int(math.floor(posx / SQUARESIZE))

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)

                # Check if the current player used a bomb last turn
                if (turn == 0 and player1_used_bomb_last_turn) or (turn == 1 and player2_used_bomb_last_turn):
                    # Player must place a regular disc
                    if turn == 0:
                        drop_piece(board, row, col, 1)
                        player1_used_bomb_last_turn = False
                        if winning_move(board, 1):
                            label = myfont.render("Player 1 wins!!", 1, RED)
                            screen.blit(label, (40, 30))
                            game_over = True
                    else:
                        drop_piece(board, row, col, 2)
                        player2_used_bomb_last_turn = False
                        if winning_move(board, 2):
                            label = myfont.render("Player 2 wins!!", 1, BLUE)
                            screen.blit(label, (40, 30))
                            game_over = True
                    
                    turn += 1
                    turn = turn % 2
                else:
                    # Ask for bomb usage if they haven't used it
                    if (turn == 0 and not player1_used_bomb) or (turn == 1 and not player2_used_bomb):
                        bomb_event = True
                        label = myfont.render("Use Bomb? Press Y or N", 1, WHITE)
                        screen.blit(label, (140, 70))
                        pygame.display.update()
                    else:
                        # Player must place a regular disc
                        if turn == 0:
                            drop_piece(board, row, col, 1)
                            if winning_move(board, 1):
                                label = myfont.render("Player 1 wins!!", 1, RED)
                                screen.blit(label, (40, 30))
                                game_over = True
                        else:
                            drop_piece(board, row, col, 2)
                            if winning_move(board, 2):
                                label = myfont.render("Player 2 wins!!", 1, BLUE)
                                screen.blit(label, (40, 30))
                                game_over = True
                        
                        turn += 1
                        turn = turn % 2

                draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
                draw_player_labels(myfont)
                pygame.display.update()

        if event.type == pygame.KEYDOWN and bomb_event:
            if event.key == pygame.K_y:
                use_bomb = True
            elif event.key == pygame.K_n:
                use_bomb = False

            bomb_event = False  # Reset bomb prompt

            if use_bomb:
                remove_surrounding_pieces(board, row, col)
                if turn == 0:
                    player1_used_bomb = True
                    player1_used_bomb_last_turn = True
                else:
                    player2_used_bomb = True
                    player2_used_bomb_last_turn = True
                use_bomb = False

                turn += 1
                turn = turn % 2
            else:
                # Place a regular disc
                if turn == 0:
                    drop_piece(board, row, col, 1)
                    if winning_move(board, 1):
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40, 30))
                        game_over = True
                else:
                    drop_piece(board, row, col, 2)
                    if winning_move(board, 2):
                        label = myfont.render("Player 2 wins!!", 1, BLUE)
                        screen.blit(label, (40, 30))
                        game_over = True

                turn += 1
                turn = turn % 2

            draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
            draw_player_labels(myfont)
            pygame.display.update()

    if game_over:
        pygame.time.wait(3000)