import numpy as np
import time

import serial

from chess_engine_lib.move import Move


class LedCom:
    def __init__(self, serial_obj:serial.Serial=None) -> None:
        # Define 1D array to represent the LED board used to store rgb colors
        self.led_board_colors = np.zeros(64*3, dtype=int)

        # Define a flag to check if the serial connection is established
        # If the flag is False, the LED commands will not be sent to the Arduino
        self.serial_obj = serial_obj
        self.last_command_sent = ""
    
    def convert_to_led_strip_index(self, index: int ) -> int :
        '''
        Converts the index of the LED board to the index of the LED strip.
        @param index: The index of the LED board.
        @return: The index of the LED strip.
        '''
        row = index // 8
        col = index % 8

        if row % 2 == 0 : 
            return row*8 + col
        else : 
            return row*8 + 7 - col

    def reset_led_board(self) -> None : 
        '''
        Resets the LED board to the default state.
        '''
        # Set all the LEDs to off
        self.led_board_colors = np.zeros(64*3, dtype=int)

        # If the serial connection is established, send the LED commands to the Arduino
        if self.serial_obj != None: 
            self.send_leds_commands("0-63", 0, 0, 0)
        
    def wrong_move_led_board(self) -> None : 
        '''
        Turns on all the LEDs in red to indicate a wrong move.
        '''
        # Set all the LEDs to red (only the red channel is on so 1 out of 3)
        self.reset_led_board()

        self.led_board_colors[0::3] = 255

        if self.serial_obj != None: 
            for i in range(64) : 
                self.send_leds_commands("0-63", 255, 0, 0)
    
    def highlight_move_led_board(self, moves: list[Move]) -> None : 
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
                moves_end_capturing.append(self.convert_to_led_strip_index(end_square))
            else :
                # Set the end square to green
                self.led_board_colors[end_square*3 + 1] = 255
                moves_end.append(self.convert_to_led_strip_index(end_square))
        

        if self.serial_obj != None:
            # Send all the moves to the Arduino at once using e.g. 0.1.2 format
            if len(moves_end) > 0:
                self.send_leds_commands(".".join(map(str, moves_end)), 0, 255, 0)
            # Send all the moves capturing to the Arduino
            if len(moves_end_capturing) > 0:
                self.send_leds_commands(".".join(map(str, moves_end_capturing)), 255, 0, 0)

                
        
    
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

        if self.serial_obj != None:
            self.send_leds_commands(str(self.convert_to_led_strip_index(start_square)), 0, 255, 0)

        if move.is_capturing : 
            # Set the end square to red
            self.led_board_colors[end_square*3] = 255

            if self.serial_obj != None:
                self.send_leds_commands(str(self.convert_to_led_strip_index(end_square)), 255, 0, 0)
        else :
            # Set the end square to blue
            self.led_board_colors[end_square*3 + 2] = 255

            if self.serial_obj != None: 
                self.send_leds_commands(str(self.convert_to_led_strip_index(end_square)), 0, 0, 255)


   

    def highlight_square_led_board(self, square: int) -> None : 
        '''
        Highlights a square on the LED board.
        @param square: The square to highlight.
        '''
        self.reset_led_board()
        
        # Set the square to blue
        print(square)
        self.led_board_colors[square*3 + 2] = 255

        if self.serial_obj != None: 
            self.send_leds_commands(str(self.convert_to_led_strip_index(square)), 0, 0, 255)

    def end_of_game_led_board(self) -> None : 
        '''
        Turns on all the LEDs in blue to indicate the end of the game.
        '''
        # Set all the LEDs to blue (only the blue channel is on so 3 out of 3)
        self.reset_led_board()

        self.led_board_colors[2::3] = 255

        if self.serial_obj != None: 
            self.send_leds_commands("0-63", 0, 0, 255)

    def send_leds_commands(self, led_index: str, r: int, g: int, b: int) -> None:
        """
        Send an LED command to the Arduino to control a specific LED, multiple LEDs, or a range of LEDs.

        :param led_index: Index, range, or multiple indices of LEDs to control (e.g., "10", "0-32", "1.2.3.4").
        :param r: Red color intensity (0 to 255).
        :param g: Green color intensity (0 to 255).
        :param b: Blue color intensity (0 to 255).
        """
        if self.last_command_sent == f"{led_index},{r},{g},{b}\n":
            return

        command = f"{led_index},{r},{g},{b}\n"
        self.serial_obj.write(command.encode())
        self.serial_obj.flush()

        print(f"Sent command: {command}")
        self.last_command_sent = command


            



    




