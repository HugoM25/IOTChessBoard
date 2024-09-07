import time 
import numpy

from arduino_com import ArduinoCom

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

PINK = (255,0,255)
YELLOW = (255,255,0)
CYAN = (0,255,255)

WHITE = (255,255,255)

BLACK = (0,0,0)
OFF = (0,0,0)



if __name__ == "__main__" : 

    # ----------------------------------------------------------------------------------------
    arduino_com = ArduinoCom('/dev/ttyUSB0')
    time.sleep(5)
    # ----------------------------------------------------------------------------------------


    arduino_com.send_leds_range_command(0, 63, OFF)
    time.sleep(1)
    # # --------------------------------------------------------------------------------------
    # # Test full board color by setting all the LEDs of the board to some colors.
    # colors_to_test = [RED,BLUE, GREEN, PINK, CYAN, YELLOW, WHITE, BLACK]
    # for color in colors_to_test :
    #     arduino_com.send_leds_range_command(0, 63, color)
    #     time.sleep(1)

    # #Test every LEDs by turning all LEDs one at a time white.
    # for i in range(0, 64) :
    #     last_index = (i - 1) % 64
    #     arduino_com.set_leds_with_colors([i], WHITE)
    #     arduino_com.set_leds_with_colors([last_index], OFF)
    #     time.sleep(0.25)
    # arduino_com.set_leds_with_colors([63], OFF)


    
    # --------------------------------------------------------------------------------------
    # Test LEDs and board readings 


    arduino_com.ask_for_board_state()
    # Wait a bit for response 
    time.sleep(1)
    
    while True :
        # Receive the response : 
        scan_result = arduino_com.read_board_data()

        if scan_result is None : 
            continue
        
        index_to_light_on = []
        for i in range(len(scan_result)) :
            square_state = scan_result[i]
            if square_state == 1 :
                index_to_light_on.append(i)
        
        arduino_com.send_leds_range_command(0,63, OFF)
        arduino_com.set_leds_with_colors(index_to_light_on, RED)


        arduino_com.process_queue()


        





    
