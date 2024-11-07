import numpy as np
import pygame
import sys
import math
import random

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
SQUARESIZE = 100
WINDOW_LENGTH = 4

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode(size)

myfont = pygame.font.SysFont("monospace", 30)

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
            if (board[r][c] == piece and board[r][c+1] == piece and
                board[r][c+2] == piece and board[r][c+3] == piece):
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if (board[r][c] == piece and board[r+1][c] == piece and
                board[r+2][c] == piece and board[r+3][c] == piece):
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if (board[r][c] == piece and board[r+1][c+1] == piece and
                board[r+2][c+2] == piece and board[r+3][c+3] == piece):
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if (board[r][c] == piece and board[r-1][c+1] == piece and
                board[r-2][c+2] == piece and board[r-3][c+3] == piece):
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

    # Add player labels
    player1_label = myfont.render(f"Player 1 {'(Bomb Used)' if player1_used_bomb else ''}", 1, RED)
    player2_label = myfont.render(f"Player 2 {'(Bomb Used)' if player2_used_bomb else ''}", 1, BLUE)
    screen.blit(player1_label, (10, 10))
    screen.blit(player2_label, (width - 200, 10))
    
    pygame.display.update()

def remove_surrounding_pieces(board, row, col):
    # Remove piece to the left
    if col > 0:
        board[row][col-1] = 0
    
    # Remove piece to the right
    if col < COLUMN_COUNT - 1:
        board[row][col+1] = 0
    
    # Remove piece directly below
    if row > 0:
        board[row-1][col] = 0

    # **Newly Added: Remove diagonally adjacent pieces**
    # Remove top-left piece
    if row < ROW_COUNT - 1 and col > 0:
        board[row+1][col-1] = 0
    
    # Remove top-right piece
    if row < ROW_COUNT - 1 and col < COLUMN_COUNT - 1:
        board[row+1][col+1] = 0
    
    # Remove bottom-left piece
    if row > 0 and col > 0:
        board[row-1][col-1] = 0
    
    # Remove bottom-right piece
    if row > 0 and col < COLUMN_COUNT - 1:
        board[row-1][col+1] = 0

    # Remove the bomb piece itself
    board[row][col] = 0

    # Apply gravity after removing pieces
    apply_gravity(board)

def apply_gravity(board):
    for c in range(COLUMN_COUNT):
        # Extract the column as a list from bottom to top
        col_pieces = [board[r][c] for r in range(ROW_COUNT)]
        # Remove zeros (empty spaces)
        non_zero_pieces = [piece for piece in col_pieces if piece != 0]
        # Add zeros at the top to fill the column
        new_col = non_zero_pieces + [0] * (ROW_COUNT - len(non_zero_pieces))
        # Update the board column
        for r in range(ROW_COUNT):
            board[r][c] = new_col[r]

def is_board_full(board):
    for c in range(COLUMN_COUNT):
        if is_valid_location(board, c):
            return False
    return True

def check_game_over(board):
    if winning_move(board, 1):
        label = myfont.render("Player 1 wins!!", 1, RED)
        screen.blit(label, (40, 10))
        pygame.display.update()
        return True
    elif winning_move(board, 2):
        label = myfont.render("Player 2 wins!!", 1, BLUE)
        screen.blit(label, (40, 10))
        pygame.display.update()
        return True
    elif is_board_full(board):
        label = myfont.render("Game ends in a draw!", 1, WHITE)
        screen.blit(label, (40, 10))
        pygame.display.update()
        return True
    return False

def bomb_prompt():
    label = myfont.render("Use Bomb? Press Y or N", 1, WHITE)
    screen.blit(label, (140, 70))
    pygame.display.update()

def evaluate_window(window, piece):
    score = 0
    opp_piece = 1
    if piece == 1:
        opp_piece = 2

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score positive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer, player_piece, player1_used_bomb, player2_used_bomb):
    use_bomb = False

    if player_piece == 1:
        opp_player_piece = 2
    else:
        opp_player_piece = 1

    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, player_piece):
                return False, None, 100000000000000
            elif winning_move(board, opp_player_piece):
                return False, None, -10000000000000
            else: # Game is over, no more valid moves
                return False, None, 0
        else: # Depth is zero
            return False, None, score_position(board, player_piece)
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)

            b_copy = board.copy()
            drop_piece(b_copy, row, col, player_piece)
            new_score = minimax(b_copy, depth-1, alpha, beta, False, opp_player_piece, player1_used_bomb, player2_used_bomb)[2]

            if new_score > value:
                value = new_score
                column = col
                use_bomb = False

            if player_piece == 1:
                if not player1_used_bomb:
                    c_copy = board.copy()
                    remove_surrounding_pieces(c_copy, row, col)
                    new_score_with_bomb = minimax(c_copy, depth - 1, alpha, beta, False, opp_player_piece, True, player2_used_bomb)[2]

                    if new_score_with_bomb > value:
                        value = new_score
                        column = col
                        use_bomb = True
            else:
                if not player2_used_bomb:
                    c_copy = board.copy()
                    remove_surrounding_pieces(c_copy, row, col)
                    new_score_with_bomb = minimax(c_copy, depth - 1, alpha, beta, False, opp_player_piece, player1_used_bomb, True)[2]

                    if new_score_with_bomb > value:
                        value = new_score
                        column = col
                        use_bomb = True

            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return use_bomb, column, value

    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)

            b_copy = board.copy()
            drop_piece(b_copy, row, col, opp_player_piece)
            new_score = minimax(b_copy, depth-1, alpha, beta, True, player_piece, player1_used_bomb, player2_used_bomb)[2]

            if new_score < value:
                value = new_score
                column = col
                use_bomb = False

            if opp_player_piece == 1:
                if not player1_used_bomb:
                    c_copy = board.copy()
                    remove_surrounding_pieces(c_copy, row, col)
                    new_score_with_bomb = minimax(c_copy, depth - 1, alpha, beta, True, player_piece, True, player2_used_bomb)[2]

                    if new_score_with_bomb < value:
                        value = new_score
                        column = col
                        use_bomb = True
            else:
                if not player2_used_bomb:
                    c_copy = board.copy()
                    remove_surrounding_pieces(c_copy, row, col)
                    new_score_with_bomb = minimax(c_copy, depth - 1, alpha, beta, True, player_piece, player1_used_bomb, True)[2]

                    if new_score_with_bomb < value:
                        value = new_score
                        column = col
                        use_bomb = True

            beta = min(beta, value)
            if alpha >= beta:
                break
        return use_bomb, column, value

def ai_analysis(board, player_piece, player1_used_bomb, player2_used_bomb, ai_algorithm):
    col = 0
    use_bomb = False

    if ai_algorithm == "minimax":
        use_bomb, col, minimax_score = minimax(board, 5, -math.inf, math.inf, True, player_piece, player1_used_bomb, player2_used_bomb)

    return col, use_bomb

def manual_mode():
    board = create_board()
    print_board(board)
    game_over = False
    turn = random.randint(0, 1) #make first player a random choice

    player1_used_bomb = False
    player2_used_bomb = False
    player1_used_bomb_last_turn = False
    player2_used_bomb_last_turn = False
    bomb_event = False
    use_bomb = False

    draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
    pygame.display.update()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if bomb_event:
                bomb_prompt()

            if event.type == pygame.MOUSEMOTION and not bomb_event:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                else:
                    pygame.draw.circle(screen, BLUE, (posx, int(SQUARESIZE / 2)), RADIUS)

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
                        else:
                            drop_piece(board, row, col, 2)
                            player2_used_bomb_last_turn = False

                        draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
                        game_over = check_game_over(board)
                        if not game_over:
                            turn += 1
                            turn = turn % 2
                    else:
                        # Ask for bomb usage if they haven't used it
                        if (turn == 0 and not player1_used_bomb) or (turn == 1 and not player2_used_bomb):
                            bomb_event = True
                            #bomb_prompt()
                            selected_row = row
                            selected_col = col
                        else:
                            # Player must place a regular disc
                            if turn == 0:
                                drop_piece(board, row, col, 1)
                            else:
                                drop_piece(board, row, col, 2)

                            draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
                            game_over = check_game_over(board)
                            if not game_over:
                                turn += 1
                                turn = turn % 2

            if event.type == pygame.KEYDOWN and bomb_event:
                if event.key == pygame.K_y:
                    use_bomb = True
                elif event.key == pygame.K_n:
                    use_bomb = False

                bomb_event = False  # Reset bomb prompt
                pygame.draw.rect(screen, BLACK, (140, 70, 300, 40))  # Clear the bomb prompt
                pygame.display.update()

                if use_bomb:
                    remove_surrounding_pieces(board, selected_row, selected_col)
                    draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
                    game_over = check_game_over(board)
                    if turn == 0:
                        player1_used_bomb = True
                        player1_used_bomb_last_turn = True
                    else:
                        player2_used_bomb = True
                        player2_used_bomb_last_turn = True
                    use_bomb = False

                    if not game_over:
                        turn += 1
                        turn = turn % 2
                else:
                    # Place a regular disc
                    if turn == 0:
                        drop_piece(board, selected_row, selected_col, 1)
                    else:
                        drop_piece(board, selected_row, selected_col, 2)

                    draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
                    game_over = check_game_over(board)
                    if not game_over:
                        turn += 1
                        turn = turn % 2

        if game_over:
            pygame.time.wait(3000)

def ai_mode():
    board = create_board()
    print_board(board)
    game_over = False
    turn = random.randint(0, 1) #make first player a random choice

    player1_used_bomb = False
    player2_used_bomb = False
    player1_used_bomb_last_turn = False
    player2_used_bomb_last_turn = False
    bomb_event = False
    use_bomb = False

    draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
    pygame.display.update()

    while True:
        #select AI algorithm for each player
        if turn == 0:
            col, use_bomb = ai_analysis(board, turn+1, player1_used_bomb, player2_used_bomb, "minimax")

        else:
            col, use_bomb = ai_analysis(board, turn+1, player1_used_bomb, player2_used_bomb, "minimax")

        #col = random.randint(0, COLUMN_COUNT - 1) #AI picks

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)

            # Check if the current player used a bomb last turn
            if (turn == 0 and player1_used_bomb_last_turn) or (turn == 1 and player2_used_bomb_last_turn):
                # Player must place a regular disc
                if turn == 0:
                    drop_piece(board, row, col, 1)
                    player1_used_bomb_last_turn = False
                else:
                    drop_piece(board, row, col, 2)
                    player2_used_bomb_last_turn = False

                draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
                game_over = check_game_over(board)
                if not game_over:
                    turn += 1
                    turn = turn % 2
            else:
                # Ask for bomb usage if they haven't used it
                if (turn == 0 and not player1_used_bomb) or (turn == 1 and not player2_used_bomb):
                    bomb_event = True
                    selected_row = row
                    selected_col = col
                else:
                    # Player must place a regular disc
                    if turn == 0:
                        drop_piece(board, row, col, 1)
                    else:
                        drop_piece(board, row, col, 2)

                    draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
                    game_over = check_game_over(board)
                    if not game_over:
                        turn += 1
                        turn = turn % 2

            if bomb_event:
                bomb_event = False
                #use_bomb = random.choice([True, False]) #AI picks

                if use_bomb:
                    print("used bomb: ", turn)
                    remove_surrounding_pieces(board, selected_row, selected_col)
                    draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
                    game_over = check_game_over(board)
                    if turn == 0:
                        player1_used_bomb = True
                        player1_used_bomb_last_turn = True
                    else:
                        player2_used_bomb = True
                        player2_used_bomb_last_turn = True
                    use_bomb = False

                    if not game_over:
                        turn += 1
                        turn = turn % 2
                else:
                    # Place a regular disc
                    if turn == 0:
                        drop_piece(board, selected_row, selected_col, 1)
                    else:
                        drop_piece(board, selected_row, selected_col, 2)

                    draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
                    game_over = check_game_over(board)
                    if not game_over:
                        turn += 1
                        turn = turn % 2

            if game_over:
                pygame.time.wait(5000)
                break

if __name__=="__main__":
    #manual_mode()
    ai_mode()