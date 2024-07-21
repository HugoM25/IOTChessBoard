import numpy as np

from chess_engine_lib.move import Move

class LedCom:
    def __init__(self):
        # Define 1D array to represent the LED board used to store rgb colors
        self.led_board_colors = np.zeros(64*3, dtype=int)

    def reset_led_board(self) -> None : 
        '''
        Resets the LED board to the default state.
        '''
        # Set all the LEDs to off
        self.led_board_colors = np.zeros(64*3, dtype=int)
        
    def wrong_move_led_board(self) -> None : 
        '''
        Turns on all the LEDs in red to indicate a wrong move.
        '''
        # Set all the LEDs to red (only the red channel is on so 1 out of 3)
        self.reset_led_board()

        self.led_board_colors[0::3] = 255
    
    def highlight_move_led_board(self, moves: list[Move]) -> None : 
        '''
        Highlights the move on the LED board.
        @param move: The move to highlight.
        '''
        self.reset_led_board()
        
        for move in moves : 
            # Get the start and end square of the move
            start_square = move.start_pos_index
            end_square = move.end_pos_index
            # Set the start square to green
            self.led_board_colors[start_square*3 + 1] = 255

            if move.is_capturing : 
                # Set the end square to red
                self.led_board_colors[end_square*3] = 255
            else :
                # Set the end square to green
                self.led_board_colors[end_square*3 + 1] = 255
    
    def highlight_specific_move(self, move: Move)-> None :
        '''
        Highlights a specific move on the LED board.
        @param move: The move to highlight.
        '''
        self.reset_led_board()

        # Get the start and end square of the move
        start_square = move.start_pos_index
        end_square = move.end_pos_index
        # Set the start square to green
        self.led_board_colors[start_square*3 + 1] = 255

        if move.is_capturing : 
            # Set the end square to red
            self.led_board_colors[end_square*3] = 255
        else :
            # Set the end square to blue
            self.led_board_colors[end_square*3 + 2] = 255

    def highlight_square_led_board(self, square: int) -> None : 
        '''
        Highlights a square on the LED board.
        @param square: The square to highlight.
        '''
        self.reset_led_board()
        
        # Set the square to blue
        print(square)
        self.led_board_colors[square*3 + 2] = 255

    def end_of_game_led_board(self) -> None : 
        '''
        Turns on all the LEDs in blue to indicate the end of the game.
        '''
        # Set all the LEDs to blue (only the blue channel is on so 3 out of 3)
        self.reset_led_board()

        self.led_board_colors[2::3] = 255


