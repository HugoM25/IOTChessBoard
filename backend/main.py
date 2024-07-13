import pygame
import numpy as np
from chess_engine_lib import ChessEngine
# Initialize pygame
pygame.init()

# Define the size of the chessboard
board_size = 8
square_size = 40

# Define the colors for the chessboard
black = (118, 150, 86)
white = (238, 238, 210)

moves_zone_size = 100

# Calculate the size of the window based on the chessboard size
window_size = (board_size * square_size + 50, board_size * square_size + moves_zone_size)

# Create the window
window = pygame.display.set_mode(window_size)

# Set the window title
pygame.display.set_caption("Chessboards")

# Create a font object
font = pygame.font.Font(None, 36)

# Create a list of strings
strings = []

pieces_picked = 0

# Setup chess engine
myEngine : ChessEngine = ChessEngine()

# Initial board
myEngine.board.set_board_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

binary_board = np.zeros(64, dtype=int)
# Change two first rows to 1
binary_board[0:16] = 1
# Change two last rows to 1
binary_board[48:64] = 1

myEngine.binary_board = binary_board

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get the position of the mouse click
            mouse_pos = pygame.mouse.get_pos()
            # Calculate the index of the clicked square in a single dimension array
            index = (mouse_pos[1] // square_size) * board_size + (mouse_pos[0] // square_size)

            index = 63 - index

            # Check if the click is within the chessboard bounds
            if index < board_size * board_size:
                # Check if the clicked square is empty
                if binary_board[index] == 0:
                    # Place a piece on the clicked square
                    if pieces_picked > 0:
                        binary_board[index] = 1
                        pieces_picked -= 1
                else:
                    # Remove the piece from the clicked square
                    binary_board[index] = 0
                    pieces_picked += 1
    
    myEngine.handle_moves(binary_board)

    
    for index in range(board_size * board_size):
        i = index // board_size
        j = index % board_size
        # Flip the row and column index to render the board correctly
        flipped_i = (board_size - 1) - i
        flipped_j = (board_size - 1) - j


        if (flipped_i + flipped_j) % 2 == 0:
            color = white
        else:
            color = black

        check_color = (myEngine.led_com.led_board_colors[index * 3], myEngine.led_com.led_board_colors[index * 3 + 1], myEngine.led_com.led_board_colors[index * 3 + 2])
        if check_color != (0, 0, 0):
            color = check_color
                    
        pygame.draw.rect(window, color, (flipped_j * square_size, flipped_i * square_size, square_size, square_size))
        if binary_board[index] == 1:
            pygame.draw.circle(window, (255, 255, 255), (flipped_j * square_size + square_size // 2, flipped_i * square_size + square_size // 2), square_size // 2 - 5)
    # Render the strings
    for i, string in enumerate(strings):
        text = font.render(string, True, (255, 255, 255))
        text_width = text.get_width()
        text_height = text.get_height()
        x = 10 + i * (text_width + 10)
        y = board_size * square_size + moves_zone_size // 2 - text_height // 2
        window.blit(text, (x, y))

    # Update the display
    pygame.display.flip()

# Quit the game
pygame.quit()