from chess_engine_lib import LedCom
import serial 
import time
class ArduinoCom(): 
    def __init__(self, port: str, baud_rate: int = 9600) -> None:
        self.serial = serial.Serial(port, baud_rate, timeout=1)
    
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
    
    def set_leds_with_colors(self, leds_indexes: list[int], color: tuple[int,int,int]) -> str: 
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

        command += "\n"

        return command

    def ask_for_board_state(self) -> str:
        """
        Ask the Arduino for the board state
        @return: The command to send to the Arduino as a string
        """
        command_id = 6
        command = f"{command_id:04b}000000\n"
        return command
    
    def send_command(self, command: str) -> None: 
        '''
        Send a command to the Arduino.
        '''
        self.serial.write(command.encode())
        self.serial.flush()
    


if __name__ == '__main__':
    arduino_com = ArduinoCom('COM6')
    time.sleep(2)
    command = arduino_com.set_leds_with_colors([1,8,15], (255,0,0))
    print(command)
    arduino_com.send_command(command)