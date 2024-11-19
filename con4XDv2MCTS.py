import numpy as np
import pygame
import sys
import math
import random
import time

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

myfont = pygame.font.SysFont("monospace", 28)

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
    screen.blit(player2_label, (width - 340, 10))
    
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
        screen.blit(label, (40, 60))
        pygame.display.update()
        return True, 1
    elif winning_move(board, 2):
        label = myfont.render("Player 2 wins!!", 1, BLUE)
        screen.blit(label, (40, 60))
        pygame.display.update()
        return True, 2
    elif is_board_full(board):
        label = myfont.render("Game ends in a draw!", 1, WHITE)
        screen.blit(label, (40, 60))
        pygame.display.update()
        return True, 0
    return False, None

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


class MCTSNode:
    def __init__(self, board, player, parent=None, move=None, used_bomb=False):
        self.board = board
        self.player = player
        self.parent = parent
        self.move = move
        self.used_bomb = used_bomb
        self.children = []
        self.visits = 0
        self.score = 0

    def add_child(self, child_node):
        self.children.append(child_node)

    def update(self, result):
        self.visits += 1
        self.score += result

    def fully_expanded(self):
        return len(self.children) == len(get_valid_locations(self.board))

    def best_child(self, c_param=1.4):
        best_score = -float('inf')
        best_node = None
        for c in self.children:
            if c.visits == 0:
                score = float('inf')
            else:
                score = (c.score / c.visits) + c_param * ((math.log(self.visits) / c.visits) ** 0.5)
            if score > best_score:
                best_score = score
                best_node = c
        return best_node

def mcts(board, player, player1_used_bomb, player2_used_bomb, iterations=1000):
    root = MCTSNode(board, player)
    for _ in range(iterations):
        node = root
        temp_board = board.copy()
        temp_player1_used_bomb = player1_used_bomb
        temp_player2_used_bomb = player2_used_bomb
        player1_turns = 0
        player2_turns = 0

        # Selection
        while node.fully_expanded() and node.children:
            node = node.best_child()
            if node.used_bomb:
                remove_surrounding_pieces(temp_board, get_next_open_row(temp_board, node.move), node.move)
                if node.player == 1:
                    temp_player1_used_bomb = True
                else:
                    temp_player2_used_bomb = True
            else:
                drop_piece(temp_board, get_next_open_row(temp_board, node.move), node.move, node.player)

        # Expansion
        valid_moves = get_valid_locations(temp_board)
        if not valid_moves:
            result = 1 if winning_move(temp_board, player) else 0
            while node:
                node.update(result)
                node = node.parent
            continue

        if not node.fully_expanded():
            unvisited_moves = set(valid_moves) - set(child.move for child in node.children)
            if unvisited_moves:
                move = random.choice(list(unvisited_moves))
                new_player = 3 - node.player
                for use_bomb in [False, True]:
                    if use_bomb and ((new_player == 1 and temp_player1_used_bomb) or (new_player == 2 and temp_player2_used_bomb)):
                        continue
                    child = MCTSNode(temp_board, new_player, parent=node, move=move, used_bomb=use_bomb)
                    node.add_child(child)
                node = random.choice(node.children)
            else:
                node = random.choice(node.children)

        # Simulation
        while not is_terminal_node(temp_board):
            valid_moves = get_valid_locations(temp_board)
            if not valid_moves:
                break
            move = random.choice(valid_moves)
            use_bomb = False

            # Update turn count for each player
            if node.player == 1:
                player1_turns += 1
            else:
                player2_turns += 1

            # Check if bomb can be used (after 3rd move)
            if ((node.player == 1 and player1_turns >= 3 and not temp_player1_used_bomb) or 
                (node.player == 2 and player2_turns >= 3 and not temp_player2_used_bomb)):
                opponent = 3 - node.player
                temp_board_copy = temp_board.copy()
                drop_piece(temp_board_copy, get_next_open_row(temp_board_copy, move), move, opponent)
                if winning_move(temp_board_copy, opponent):
                    use_bomb = True
                elif random.random() < 0.1:  # 10% chance to use bomb randomly
                    use_bomb = True

            if use_bomb:
                remove_surrounding_pieces(temp_board, get_next_open_row(temp_board, move), move)
                if node.player == 1:
                    temp_player1_used_bomb = True
                else:
                    temp_player2_used_bomb = True
            else:
                row = get_next_open_row(temp_board, move)
                drop_piece(temp_board, row, move, node.player)

            node.player = 3 - node.player

        # Backpropagation
        result = 1 if winning_move(temp_board, player) else 0
        while node:
            node.update(result)
            node = node.parent

    best_child = max(root.children, key=lambda c: c.visits)
    return best_child.move, best_child.used_bomb

def ai_analysis(board, player_piece, player1_used_bomb, player2_used_bomb):
    col, use_bomb = mcts(board, player_piece, player1_used_bomb, player2_used_bomb)
    return col, use_bomb


def ai_mode():
    board = create_board()
    print_board(board)
    game_over = False
    turn = 0
    player1_used_bomb = False
    player2_used_bomb = False
    player1_decisions = 0
    player2_decisions = 0
    player1_turns = 0
    player2_turns = 0
    start_time = time.time()
    winner = None
    draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
    pygame.display.update()

    while not game_over:
        if turn == 0:
            player1_turns += 1
            col, use_bomb = ai_analysis(board, turn+1, player1_used_bomb, player2_used_bomb)
            player1_decisions += 1
        else:
            player2_turns += 1
            col, use_bomb = ai_analysis(board, turn+1, player1_used_bomb, player2_used_bomb)
            player2_decisions += 1

        if col is None:
            game_over = True
            label = myfont.render("Game ends in a draw!", 1, WHITE)
            screen.blit(label, (40, 60))
            pygame.display.update()
        elif is_valid_location(board, col):
            row = get_next_open_row(board, col)
            if use_bomb and ((turn == 0 and player1_turns >= 3 and not player1_used_bomb) or (turn == 1 and player2_turns >= 3 and not player2_used_bomb)):
                remove_surrounding_pieces(board, row, col)
                if turn == 0:
                    player1_used_bomb = True
                else:
                    player2_used_bomb = True
            else:
                drop_piece(board, row, col, turn + 1)

            draw_board(board, myfont, player1_used_bomb, player2_used_bomb)
            game_over, winner = check_game_over(board)

            if not game_over:
                turn = (turn + 1) % 2

        if game_over:
            end_time = time.time()
            game_duration = end_time - start_time
            pygame.display.update()
            pygame.time.wait(4000)  # Display stats for 4 seconds

            # Print stats to console
            print(f"\nGame Statistics:")
            print(f"Game Duration using MCTS: {game_duration:.2f} seconds")
            print(f"Player 1 Decisions: {player1_decisions}")
            print(f"Player 2 Decisions: {player2_decisions}")
            print(f"Total Decisions: {player1_decisions + player2_decisions}")

            # Print the winner
            if winner == 1:
                print("Player 1 wins!")
            elif winner == 2:
                print("Player 2 wins!")
            else:
                print("The game ends in a draw!")

            # Print bomb disc usage
            print("\nBomb Disc Usage:")
            if player1_used_bomb and player2_used_bomb:
                print("Both players used their bomb disc.")
            elif player1_used_bomb:
                print("Player 1 used their bomb disc.")
            elif player2_used_bomb:
                print("Player 2  used their bomb disc.")
            else:
                print("Neither player used their bomb disc.")

            break

if __name__=="__main__":
    #manual_mode()
    ai_mode()
