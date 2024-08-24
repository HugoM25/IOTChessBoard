from chess_engine_lib import LedCom

if __name__ == '__main__':
    # Create an instance of the LedCom class
    led_com = LedCom()

    # Send LED command to arduino
    led_com.send_leds_commands(0, 0, 255, 255)


