import serial
import numpy as np 
import time 

class ArduinoCom(): 
    def __init__(self, port: str, baud_rate: int = 9600, timeout: int = 2) -> None:
        self.serial = serial.Serial(port, baud_rate, timeout=timeout)
        self.last_command_sent = ""
        self.led_strip_colors_state = np.zeros((64, 3), dtype=int)
    
    def index_square_to_led_strip(self, index: int) -> int:
        """
        Convert the index of the square to the index of the LED strip
        """
        row = index // 8
        col = index % 8

        if row % 2 == 0:
            return row * 8 + col
        else:
            return row * 8 + 7 - col
    
    def set_leds_with_colors(self, leds_indexes: list[int], color: tuple[int,int,int]) -> None: 
        """
        Set LEDS not next to each other with a specific color
        @return: The command to send to the Arduino as a string
        """
        command_id = 4 # Command ID for setting the color of multiple LEDs
        length = len(leds_indexes) # Number of LEDs to set

        #Construct the command
        command = f"{command_id:04b}{length:06b}{color[0]:08b}{color[1]:08b}{color[2]:08b}"

        for index in leds_indexes :
            good_index = self.index_square_to_led_strip(index)
            command += f"{good_index:06b}"

        command += ";"

        self.send_command(command)
    
    def send_leds_range_command(self, start_index: int, end_index: int, color: tuple[int,int,int]):
        """
        Sends a command to the Arduino to set LEDs from start_index to end_index to a specified color.
        :param start_index: The starting index of LEDs to set (0 to 63).
        :param end_index: The ending index of LEDs to set (0 to 63).
        :param color: The color to set the LEDs to as a tuple (r, g, b) where r, g, b are integers between 0 and 255.
        """

        command_id = 1

        command = f"{command_id:04b}{start_index:06b}{end_index:06b}{color[0]:08b}{color[1]:08b}{color[2]:08b};"
        self.send_command(command)
    

    def ask_for_board_state(self) -> None:
        """
        Ask the Arduino for the board state
        @return: The command to send to the Arduino as a string
        """
        command_id = 6
        command = f"{command_id:04b}000000;"

        self.send_command(command)

    def read_board_data(self):
        """
        Reads data from the serial port and processes it to get the board state.
        :return: A numpy array representing the board state (0s and 1s) or None if no valid data is read.
        """
        try:
            if self.serial.in_waiting > 0:
                # Read data until ';' which signifies the end of a command
                data = self.serial.read_until(b';').decode('utf-8').strip(';')
                
                if data:  # Check if data is not empty
                    # Extract the command ID (first 4 bits)
                    command_id = int(data[:4], 2)
                    
                    if command_id == 5:  # Command ID 5 for board data
                        board_data_bits = data[4:68]  # Next 64 bits are the board data
                        
                        if len(board_data_bits) == 64:  # Ensure we have all 64 bits
                            board_matrix = [int(bit) for bit in board_data_bits]
                            binary_board = np.array(board_matrix)
                            return binary_board
                        else:
                            print("Received incomplete board data. Ignoring...")
                            return None
                    else:
                        print(f"Received unknown command ID: {command_id}")
                        return None
            return None  # No data in waiting
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def send_command(self, command: str) -> None: 
        '''
        Send a command to the Arduino.
        '''

        # Prevent sending the same command multiple times
        if self.last_command_sent == command:
            return
        self.last_command_sent = command

        print(f"Sending command: {command}") 

        self.serial.write(command.encode())
        self.serial.flush()

    def __del__(self):
        self.serial.close()
    