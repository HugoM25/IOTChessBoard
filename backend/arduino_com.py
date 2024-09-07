import serial
import numpy as np 
import time
import sys

class ArduinoCom(): 
    def __init__(self, port: str, baud_rate: int = 9600, timeout: int = 2) -> None:
        self.serial = serial.Serial(port, baud_rate, timeout=timeout)
        self.last_command_sent = ""
        self.led_strip_colors_state = np.zeros((64, 3), dtype=int)

        # Queue for storing commands to be sent
        self.command_queue = [] 
        self.awaiting_ack = False



    def wait_for_com(self, max_retries: int = 5) :
        """
        Wait for the communication to be on before going to the next step
        """
        retries = 0
        while retries < max_retries:
            command = "1001;"
            self.serial.write(command.encode())
            self.serial.flush()

            # Wait for acknowledgment (ACK, in this case "1111;")
            if self.wait_for_ack(timeout=20):
                print(f"Command {command} acknowledged.")
                return True  # Command was successfully acknowledged
            else:
                print(f"Retrying command: {command}")
                retries += 1

        print(f"Command {command} failed after {max_retries} retries.")
        return False

    
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

        self.command_queue.append(command)
    
    def send_leds_range_command(self, start_index: int, end_index: int, color: tuple[int,int,int]):
        """
        Sends a command to the Arduino to set LEDs from start_index to end_index to a specified color.
        :param start_index: The starting index of LEDs to set (0 to 63).
        :param end_index: The ending index of LEDs to set (0 to 63).
        :param color: The color to set the LEDs to as a tuple (r, g, b) where r, g, b are integers between 0 and 255.
        """

        command_id = 1

        command = f"{command_id:04b}{start_index:06b}{end_index:06b}{color[0]:08b}{color[1]:08b}{color[2]:08b};"
        
        self.command_queue.append(command)

    

    def ask_for_board_state(self) -> None:
        """
        Ask the Arduino for the board state
        @return: The command to send to the Arduino as a string
        """
        command_id = 6
        command = f"{command_id:04b}000000;"

        self.command_queue.append(command)


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
    
    def send_command(self, command: str, max_retries: int = 3) -> None: 
        """
        Send a command to the Arduino with acknowledgment and retries.
        """
        retries = 0
        while retries < max_retries:
            print(f"Sending command: {command}")
            self.serial.write(command.encode())
            self.serial.flush()

            # Wait for acknowledgment (ACK, in this case "1111;")
            if self.wait_for_ack():
                print(f"Command {command} acknowledged.")
                return  # Command was successfully acknowledged
            else:
                print(f"Retrying command: {command}")
                retries += 1

        print(f"Command {command} failed after {max_retries} retries.")
    
    def wait_for_ack(self, timeout: int = 2) -> bool:
        """
        Wait for an acknowledgment (ACK) from the Arduino.
        :param timeout: Time to wait for an ACK in seconds.
        :return: True if ACK ("1111;") is received, False if timeout occurs.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.serial.in_waiting > 0:
                data = self.serial.read_until(b';').decode('utf-8').strip(';')
                if data == "1111":  # ACK received
                    return True
        return False  # Timeout occurred

    
    def process_queue(self) : 
        """
        Process the command queue and send commands one at a time.
        """
        while self.command_queue:
            command = self.command_queue.pop(0)
            self.send_command(command)

    def __del__(self):
        self.serial.close()
    