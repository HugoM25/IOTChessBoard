
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
import numpy as np

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


# Define the chess engine globally
myEngine = None

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
    # Setup chess engine
    myEngine = ChessEngine()

    myEngine.board.set_board_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

    binary_board = np.zeros(64, dtype=int)

    # fen_list = ["rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
    #             "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
    #             "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"]
    # i = 0

    # while True:
    #     # Wait a bit
    #     time.sleep(4)

    #     socketio.emit('reload_backend', {})

    #     myEngine.board.set_board_fen(fen_list[i])
    #     i = (i + 1) % 3

    serial_obj = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)
    print("Serial port opened")

    # Setup chess engine
    myEngine = ChessEngine(serial_com_obj=serial_obj)

    binary_board = np.zeros(64, dtype=int)
    # Change two first rows to 1
    binary_board[0:16] = 1
    # Change two last rows to 1
    binary_board[48:64] = 1

    myEngine.binary_board = binary_board

    while True:
        try:
            if serial_obj.in_waiting > 0:
                # Read data from serial and process it
                data = serial_obj.readline().decode('utf-8').strip()
                if data:  # Check if data is not empty
                    board_matrix = list(map(int, data.split(',')))
                    
                    if len(board_matrix) == 64:  # Ensure that the data is of the correct length
                        binary_board = np.array(board_matrix)
                    else:
                        print("Received incomplete data. Ignoring...")
        except Exception as e:
            print(f"Error: {e}")

        # Check if a move was played based on the received board state
        was_move_played = myEngine.handle_moves(binary_board)

        if was_move_played:
            socketio.emit('reload_backend', {})
        
        was_move_played : bool = myEngine.handle_moves(binary_board)

        if was_move_played:
            socketio.emit('reload_backend', {})
    
    serial_obj.close()


if __name__ == '__main__':
    # Start the chess engine as background task
    socketio.start_background_task(run_chess_engine)

    socketio.run(app, port=5000)