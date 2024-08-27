import numpy as np
import serial

from chess_engine_lib.move import Move


class LedCom:
    def __init__(self, arduino_com:serial.Serial=None) -> None:
        # Define 1D array to represent the LED board used to store rgb colors
        self.led_board_colors = np.zeros(64*3, dtype=int)

        self.arduino_com = arduino_com

    def reset_led_board(self) -> None : 
        '''
        Resets the LED board to the default state.
        '''
        # Set all the LEDs to off
        self.led_board_colors = np.zeros(64*3, dtype=int)

        # If the serial connection is established, send the LED commands to the Arduino
        if self.arduino_com != None: 
            self.arduino_com.send_leds_range_command(0, 63, (0, 0, 0))
        
    def wrong_move_led_board(self, last_piece_index:int = -1) -> None : 
        '''
        Turns on all the LEDs in red to indicate a wrong move.
        '''
        # Set all the LEDs to red (only the red channel is on so 1 out of 3)
        self.reset_led_board()

        self.led_board_colors[0::3] = 255

        if self.arduino_com != None: 
            self.arduino_com.send_leds_range_command(0, 63, (255, 0, 0))

            if last_piece_index != -1:
                self.arduino_com.set_leds_with_colors([last_piece_index], (255, 255, 255))
    
    def highlight_move_led_board(self, moves: list[Move], piece_index: int) -> None : 
        '''
        Highlights the move on the LED board.
        @param move: The move to highlight.
        '''
        self.reset_led_board()

        moves_end_capturing = []
        moves_end = []
        
        for move in moves : 
            # Get the start and end square of the move
            start_square = move.start_pos_index
            end_square = move.end_pos_index
            # Set the start square to green
            self.led_board_colors[start_square*3 + 1] = 255

            if move.is_capturing : 
                # Set the end square to red
                self.led_board_colors[end_square*3] = 255
                moves_end_capturing.append(end_square)
            else :
                # Set the end square to green
                self.led_board_colors[end_square*3 + 1] = 255
                moves_end.append(end_square)
        
        if self.arduino_com != None :
            self.arduino_com.set_leds_with_colors([piece_index], (255, 255, 255))
            if len(moves_end) > 0:
                self.arduino_com.set_leds_with_colors(moves_end, (0, 255, 0))
            if len(moves_end_capturing) > 0:
                self.arduino_com.set_leds_with_colors(moves_end_capturing, (255, 0, 0))
    
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
        
        if self.arduino_com != None: 
            self.arduino_com.set_leds_with_colors([end_square], (0, 255, 0))


        if move.is_capturing : 
            # Set the end square to red
            self.led_board_colors[end_square*3] = 255

            if self.arduino_com != None:
                self.arduino_com.set_leds_with_colors([end_square], (255, 0, 0))
        else :
            # Set the end square to blue
            self.led_board_colors[end_square*3 + 2] = 255

            if self.arduino_com != None: 
                self.arduino_com.set_leds_with_colors([end_square], (0, 0, 255))


    def highlight_square_led_board(self, square: int, color:tuple[int,int,int]) -> None : 
        '''
        Highlights a square on the LED board. 
        @param square: The square to highlight.
        '''
        
        # Set the square to blue
        self.led_board_colors[square*3 + 2] = 255

        if self.arduino_com != None: 
            self.arduino_com.set_leds_with_colors([square], color)

    def highlight_squares_led_board(self, squares: list[int], color:tuple[int,int,int]) -> None :
        '''
        Highlights the squares on the LED board.
        @param squares: The squares to highlight.
        '''

        if self.arduino_com != None: 
            self.arduino_com.set_leds_with_colors(squares, color)

    def end_of_game_led_board(self) -> None : 
        '''
        Turns on all the LEDs in blue to indicate the end of the game.
        '''
        # Set all the LEDs to blue (only the blue channel is on so 3 out of 3)
        self.reset_led_board()

        self.led_board_colors[2::3] = 255

        if self.arduino_com != None: 
            self.arduino_com.send_leds_range_command(0, 63, (0, 0, 255))

            



    




