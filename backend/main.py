
# Libraries related to the web server
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO

import threading
import json
import time
import serial


# Libraries related to the chess engine
from chess_engine_lib import ChessEngine
from arduino_com import ArduinoCom
import numpy as np

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


# Create an enum to define the different states of the game
class GameState:
    SETUP_START_POS = 0
    PLAYING_GAME = 1
    GAME_OVER = 2


# Define the chess engine globally
myEngine = None
current_game_state = GameState.SETUP_START_POS

@app.route('/api/v1/chess_engine_data', methods=['GET'])
def get_chess_engine_data():
    '''
    This function returns the data of the chess engine
    ''' 
    response = None
    if request.method == 'GET':
        if myEngine is not None:
            # Assuming myEngine has a method to get its current state
            engine_data = myEngine.get_engine_infos()
            response = jsonify(engine_data)
        else:
            response = jsonify({"error": "Chess engine not initialized"})
        return response, 200

@app.route('/update_parameters', methods=['POST'])
def update_parameters(): 
    try:
        data = request.json
        # Assuming the file to update is 'parameters.json'
        with open('parameters.json', 'r+') as file:
            parameters = json.load(file)
            # Update parameters with the received data
            parameters.update(data)
            # Move the file pointer to the beginning of the file
            file.seek(0)
            # Write the updated parameters back to the file
            json.dump(parameters, file, indent=4)
            # Truncate the file to the current size
            file.truncate()
        return jsonify({"message": "Parameters updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def run_chess_engine(): 
    global myEngine
    global current_game_state

    # Setup arduino_com object --------------------------------------------------------------------
    serial_com_timeout = 2
    arduino_com = ArduinoCom('/dev/ttyUSB0')
    
    # Wait for the serial connection to be established
    start_time = time.time()
    while not arduino_com.serial.is_open and time.time() - start_time < serial_com_timeout: 
        time.sleep(0.1)
    
    time.sleep(2)
    
    # Ensure the connection is established
    if arduino_com.serial.is_open:
        print("Serial port opened")
    else:
        print("Error: Serial port not opened, no data will be sent/received to/from the Arduino")
    
    # Setup chess engine ---------------------------------------------------------------------
    myEngine = ChessEngine(arduino_com=arduino_com)
    # Load default board position 
    myEngine.board.set_board_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

    arduino_com.send_leds_range_command(0, 63, (0, 0, 0))
    # Ask the Arduino to get the initial board state

    # Main loop to handle the game state -----------------------------------------------------
    time_start_turn = time.time()
    time_remaining_turn = 10000
    while True:
        # Read the board state from the Arduino (if available)
        binary_board = arduino_com.read_board_data()

        if binary_board is None : 

            if time.time() - time_start_turn > time_remaining_turn:
                print("too slow")
                current_game_state = GameState.GAME_OVER

            # No data has been read, meaning the board state has not changed
            continue

        # Check the current game state to determine the action to take
        if current_game_state == GameState.SETUP_START_POS:
            # Help the player to set up the board in the correct position
            is_setup_done = myEngine.setup_start_position(binary_board)

            if is_setup_done :
                # Change the game state to PLAYING_GAME
                current_game_state = GameState.PLAYING_GAME
                socketio.emit('reload_backend', {})
                time_start_turn = time.time()

        elif current_game_state == GameState.PLAYING_GAME:
            # Check if a move was played based on the received board state
            was_move_played : bool = myEngine.handle_moves(binary_board)

            if was_move_played:
                socketio.emit('reload_backend', {})

                time_taken = time.time()- time_start_turn
                
                if myEngine.board.player_to_move == "w" : 
                    time_remaining_turn = myEngine.timer_white
                    myEngine.timer_black -= time_taken
                else : 
                    time_remaining_turn = myEngine.timer_black
                    myEngine.timer_white -= time_taken

                print(f"time black : {myEngine.timer_black:.2f}, time white : {myEngine.timer_white:.2f}")

                time_start_turn = time.time()
            
        elif current_game_state == GameState.GAME_OVER: 
            print("Game Over.")
                
                
    

if __name__ == '__main__':
    # Start the chess engine as background task
    socketio.start_background_task(run_chess_engine)

    socketio.run(app, port=5000)

    