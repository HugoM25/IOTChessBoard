# Import custom modules
from chess_engine_lib.board import Board
from chess_engine_lib.move import Move
from chess_engine_lib.led_com import LedCom
from chess_engine_lib.pieces import *

# Import general modules
import numpy as np
import json 
import serial
import time 

class ChessEngine:
    def __init__(self, initial_board_fen:str="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", arduino_com=None, stockfish_brain=None) -> None:

        # Setup the initial board
        self.board = Board()
        # Set the board to the desired initial FEN position
        self.board.set_board_fen(initial_board_fen)

        # Calculate the possible moves in the current position
        self.current_moves_possible = self.board.get_all_moves_in_position()

        self.last_valid_board = initial_board_fen
        self.initial_board_fen = initial_board_fen

        # Setup the binary board
        self.binary_board = self.board.get_binary_board()
        self.last_binary_board = self.binary_board

        # Setup the Serial communication with the Arduino (if available)
        self.arduino_com = arduino_com
        self.led_com = LedCom(arduino_com)

        # Setup the game tracking 
        self.current_move = 0
        self.in_hand_pieces = []
        self.captured_pieces = []

        self.moves_played = []

        self.castling_move = None
        self.square_to_put_rook_on = ""
        self.en_passant_move = None

        self.promotion_move = None
        self.piece_type_promotion = ""

        self.timer_classic = 10*60
        self.timer_white = self.timer_classic
        self.timer_black = self.timer_classic

        self.time_start_turn = time.time()

        self.is_player_w_AI = False
        self.is_player_b_AI = False 

        self.stockfish_brain = stockfish_brain

        self.action_done = False


    def check_board_validity(self) -> bool:
        '''
        Checks if the board is valid.
        @return: True if the board is valid, False otherwise.
        '''

        for i in range(0,len(self.binary_board)) : 
            square = self.binary_board[i]
            if square == 1 and self.board.board_list[i] == None :
                return False
        
        return True
    
    def detect_pick_and_drop(self, new_binary_board) :
        # For starting I will assume we can only pick up one piece at a time and drop one piece at a time
        # Compare the binary board with the last binary board
        diff = new_binary_board - self.binary_board
        # Update the binary board (without reference)
        self.binary_board = new_binary_board.copy()

        # Find the index of the picked pieces
        picked_pieces_index: int = np.where(diff == -1)

        # Find the index of the dropped pieces
        dropped_pieces_index: int = np.where(diff == 1)

        return picked_pieces_index, dropped_pieces_index
    
    def can_pieces_in_hand_take_piece(self, piece_index) -> bool:
        '''
        Checks if the pieces in hand can take a piece.
        @param piece_index: The index of the piece to check.
        @return: True if the pieces in hand can take the piece, False otherwise.
        '''
        for piece_in_hand in self.in_hand_pieces :
            possible_moves: list[Move] = piece_in_hand[0].possible_moves(self.board, piece_in_hand[1])
            for move in possible_moves :
                if move.end_pos_index == piece_index :
                    return True
        
        return False
 
    def handle_moves(self, new_binary_board) -> Move :
        '''
        Handles the moves of the player.
        Figure out which piece was picked up and which piece was dropped. 
        @param binary_board: The binary board (1 a piece is there, 0 a piece is not there).
        '''
        valid_move = False
        has_move_been_played = False
        is_game_over = False

        # Detect the picked and dropped pieces
        picked_pieces_index, dropped_pieces_index = self.detect_pick_and_drop(new_binary_board)

        # If no move detected return
        if picked_pieces_index[0].size == 0 and  dropped_pieces_index[0].size == 0 :
            return has_move_been_played
        
        # Handling of special moves
        # Castling move
        if self.castling_move != None :
            # If a castling move is initiated (by moving the king two squares)
            if picked_pieces_index[0].size > 0 :
                # Get the piece picked up
                picked_piece_index = picked_pieces_index[0][0]
                picked_piece = self.board.board_list[picked_piece_index]

                # Check if the piece taken is a rook
                if picked_piece != None and picked_piece.name.lower() == "r" :
                    self.led_com.highlight_square_led_board(self.board.square_to_index(self.square_to_put_rook_on), (0, 0, 255))
                    self.in_hand_pieces.append([picked_piece, picked_piece_index])
                else :
                    self.led_com.wrong_move_led_board()
                
            elif dropped_pieces_index[0].size > 0 :
                # Get the drop position 
                dropped_piece_index = dropped_pieces_index[0][0]
                # If the rook is dropped on the right square
                if len(self.in_hand_pieces) > 0 and self.in_hand_pieces[0][0].name.lower() == "r" :
                    if self.board.square_to_index(self.square_to_put_rook_on) == dropped_piece_index :
                        # Execute the castling move
                        is_game_over = self.apply_move(self.castling_move)
                        self.castling_move = None
                        self.square_to_put_rook_on = ""
                        self.led_com.reset_led_board()
                        self.in_hand_pieces.pop(0)
                else :
                    self.led_com.wrong_move_led_board()
        
        # En passant move
        elif self.en_passant_move != None :
            if picked_pieces_index[0].size > 0 :
                # Get the piece picked up
                picked_piece_index = picked_pieces_index[0][0]
                picked_piece = self.board.board_list[picked_piece_index]

                # Check if the piece taken is a pawn under the en passant square
                if picked_piece != None and picked_piece.name.lower() == "p" :
                    self.captured_pieces.append([picked_piece, picked_piece_index])

                    is_game_over = self.apply_move(self.en_passant_move)

                    self.en_passant_move = None


                    self.led_com.reset_led_board()

                else :
                    self.led_com.wrong_move_led_board()

        # promotion move
        elif self.promotion_move != None :
            if picked_pieces_index[0].size > 0 :
                picked_piece_index = picked_pieces_index[0][0]

                # Check if the piece picked up is really the pawn under promotion
                if self.promotion_move.end_pos_index == picked_piece_index :
                    picked_piece = self.board.board_list[self.promotion_move.start_pos_index] 

            elif dropped_pieces_index[0].size > 0 : 
                dropped_piece_index = dropped_pieces_index[0][0]

                # Check if the place where the piece has been dropped is the pawn spot
                if self.promotion_move.end_pos_index == dropped_piece_index :
                    dropped_piece = self.board.board_list[self.promotion_move.start_pos_index] 
                    # Turn the pawn into the new type of piece (by default queen)
                    type_promotion = "Q"
                    # Check if the player wants to promote it to something else
                    if self.piece_type_promotion != "" : 
                        type_promotion = self.piece_type_promotion
                    
                    # Check the color of the piece 
                    if self.promotion_move.piece_name.isupper() == True :
                        type_promotion = type_promotion.upper()
                    else : 
                        type_promotion = type_promotion.lower()

                    self.promotion_move.promote_to = type_promotion
                    self.piece_type_promotion = ""


                    is_game_over = self.apply_move(self.promotion_move)
                    self.promotion_move = None
                    self.led_com.reset_led_board()

        # Handle the picked up pieces
        elif picked_pieces_index[0].size > 0 : 
            # Get the piece picked up
            picked_piece_index = picked_pieces_index[0][0]
            picked_piece = self.board.board_list[picked_piece_index]

            if picked_piece == None :
                # Piece could not be picked up there is no piece on the square
                # Should only happen on the simulator
                self.led_com.wrong_move_led_board()
                return has_move_been_played
            
            print(f"Piece picked: {picked_piece.name} on square {self.board.index_to_square(picked_piece_index)}")
            
            # Check the color of the piece
            if picked_piece.color != self.board.player_to_move : 
                if self.can_pieces_in_hand_take_piece(picked_piece_index) == False :
                    self.led_com.wrong_move_led_board(last_piece_index=picked_piece_index)
            else : 
                # If the piece is of the color of the player to move
                # Get the moves that are possible with this piece (from the moves list)
                possible_moves = []
                for move in self.current_moves_possible :
                    if move.start_pos_index == picked_piece_index :
                        possible_moves.append(move)
                
                print(f"Possible moves for this piece: {possible_moves}")

                if (self.board.player_to_move == "w" and self.is_player_w_AI == False) or (self.board.player_to_move == "b" and self.is_player_b_AI == False): 
                    self.led_com.highlight_move_led_board(possible_moves, picked_piece_index)
            
            if self.check_board_validity() == False :
                self.led_com.wrong_move_led_board() 

            # Add the piece to the hand pieces
            self.in_hand_pieces.append([picked_piece, picked_piece_index])
            
        # Handle the dropped pieces
        elif dropped_pieces_index[0].size > 0 :
            # Get the drop position
            dropped_piece_index = dropped_pieces_index[0][0]

            # Check if there are no pieces in hand to drop
            if len(self.in_hand_pieces) == 0 :

                # Check if the board saved corresponds to the current binary board
                if self.check_board_validity() == False :
                    self.led_com.wrong_move_led_board()
                else :
                    self.led_com.reset_led_board()
                return has_move_been_played
            
            # Get the piece dropped (assume it is the first piece in hand)
            dropped_piece, last_know_pos = self.in_hand_pieces.pop(0)
            print(f"Piece dropped: {dropped_piece.name} on square {self.board.index_to_square(dropped_piece_index)}")

            # Check if the move is valid ( check if the drop position is in the possible moves of the piece)
            possible_moves = []
            for move in self.current_moves_possible :
                if move.start_pos_index == last_know_pos and move.end_pos_index == dropped_piece_index :
                    possible_moves.append(move)

            move_done = None

            if dropped_piece.color == self.board.player_to_move :
                for move in possible_moves :
                    if move.end_pos_index == dropped_piece_index :
                        valid_move, move_done = True, move
                        break
            
            # Initiating pawn promotion 
            # TO DO : handle capture promotion
            if move_done != None and move_done.promote_to != "" :

                print("Initiating promotion move")
                self.promotion_move = move_done
                self.is_pawn_promoting = False

                self.led_com.highlight_square_led_board(self.board.square_to_index(move_done.get_algebraic_notation()))

            
            elif move_done != None and move_done.get_algebraic_notation() == self.board.en_passant_square :
                self.en_passant_move = move_done
                if move_done.piece_name == "p" :
                    self.led_com.highlight_square_led_board(self.board.square_to_index(self.board.en_passant_square)+8)
                else : 
                    self.led_com.highlight_square_led_board(self.board.square_to_index(self.board.en_passant_square)-8)
        
            elif move_done != None and move_done.get_algebraic_notation().lower() in ["o-o", "o-o-o"] :
                # Initiate the castling move
                self.castling_move = move_done
                print(move_done.piece_name)
                # Get the square to put the rook on
                rook_castling_square = "f" if move_done.get_algebraic_notation().lower() == "o-o" else "d"
                rook_castling_square += "8" if move_done.piece_name == "k" else "1"
                self.square_to_put_rook_on = rook_castling_square
                print(f"CASTLING MOVE INITIATED: square to put rook on: {self.square_to_put_rook_on}")
                # Highlight the current square of the rook 
                rook_square = "a" if move_done.get_algebraic_notation().lower() == "o-o-o" else "h"
                rook_square += "8" if move_done.piece_name == "k" else "1"
                print(f"Rook square: {rook_square}")
                self.led_com.highlight_square_led_board(self.board.square_to_index(rook_square), (0, 0, 255))

            elif valid_move : 
                # A valid move was done
                print(f"Valid move has been done! (Move done: {move_done})")

                is_game_over = self.apply_move(move_done)
                
                # If the move is capturing a piece remove it from the hand pieces
                if move_done.is_capturing :
                    for piece_in_hand in self.in_hand_pieces :
                        if piece_in_hand[1] == move_done.end_pos_index :
                            self.in_hand_pieces.remove(piece_in_hand)
                            self.captured_pieces.append(piece_in_hand)
                            break
                # If the move is a mate then stops the game and turn the board blue
                elif move_done.is_checkmate : 
                    self.arduino_com.send_leds_range_command(0,63,(0,0,255))

                elif move_done.is_check : 
                    # Highlight king pos
                    self.led_com.reset_led_board()
                    if self.board.player_to_move == "b" :
                        self.arduino_com.set_leds_with_colors([self.board.get_king_index('b')], (255,0,0))
                    else : 
                        self.arduino_com.set_leds_with_colors([self.board.get_king_index('w')], (255,0,0))

                else :
                    self.led_com.reset_led_board()

            elif last_know_pos == dropped_piece_index : 
                # Clear the LED board
                self.led_com.reset_led_board()
            elif self.check_board_validity() == False :
                self.led_com.wrong_move_led_board()
            elif self.check_board_validity() == True :
                self.led_com.reset_led_board()
        
        # If a valid move has been done
        if valid_move : 
            print(f"Valid move has been done : {move_done}")
            # If the player that has to play is an AI, display the move wanted
            if self.is_player_b_AI :
                if self.board.player_to_move == "b" :
                        print("Black is thinking....")
                        # Display the move the AI wants to play
                        self.stockfish_brain.set_fen_position(self.board.get_board_fen())
                        best_move = self.stockfish_brain.get_best_move(wtime=1000, btime=1000)
                        print(f"Black thinks the best move is {best_move}")
                        self.led_com.show_AI_move(best_move)
            if self.is_player_w_AI :
                if self.board.player_to_move == "w" :
                        print("White is thinking....")
                        # Display the move the AI wants to play
                        self.stockfish_brain.set_fen_position(self.board.get_board_fen())
                        best_move = self.stockfish_brain.get_best_move(wtime=1000, btime=1000)
                        print(f"White thinks the best move is {best_move}")
                        self.led_com.show_AI_move(best_move)
            
            # Update time taken from last turn's player
            time_taken = time.time() - self.time_start_turn

            if self.board.player_to_move == "b" : 
                self.timer_white -= time_taken
            
            if self.board.player_to_move == "w" :
                self.timer_black -= time_taken

            self.time_start_turn = time.time()

            # Return the move done 
            return move_done

        return None


    def apply_move(self, move: Move) -> None:
        '''
        Applies a move to the board.
        @param move: The move to apply.
        '''

        is_game_over = self.board.execute_move(move)

        if is_game_over == True :
            print("Game is over...")

        self.current_moves_possible = self.board.get_all_moves_in_position()
        self.current_move += 1
        self.moves_played.append(move)

        # Display board for debug purposes
        print(self.board.get_board_visual())

        return is_game_over
    
    def reset_game(self) -> None:
        '''
        Resets the game.
        '''
        self.board.set_board_fen(self.last_valid_board)
        self.binary_board = self.board.get_binary_board()
        self.current_moves_possible = self.board.get_all_moves_in_position()
        self.current_move = 0
        self.in_hand_pieces = []
        self.captured_pieces = []
        self.moves_played = []
        self.castling_move = None
        self.square_to_put_rook_on = ""
        self.en_passant_move = None
        self.led_com.reset_led_board()

    def load_fen_pos(self, fen_position) -> bool :
        '''
        Load a FEN position into the engine
        '''

        fen_loaded = False
        # If the fen is valid load the fen position into the engine
        if self.board.is_fen_valid(fen_position) : 

            self.initial_board_fen = fen_position
            self.last_valid_board = fen_position
            self.reset_game()
            fen_loaded = True
        
        return fen_loaded

    
    def get_engine_infos(self) -> dict: 
        '''
        Returns the engine information to be processed by the frontend.
        '''

        engine_infos = {
            "board_infos" : {
                "board_fen": self.board.get_board_fen(),
                "player_to_move": self.board.player_to_move,
                "captured_pieces": [piece[0].serialize() for piece in self.captured_pieces],
                "clocks":{
                    "white": self.timer_white,
                    "black": self.timer_black
                },
                "promoting" : self.promotion_move != None
            }
        }

        return engine_infos
    

    def setup_start_position(self, binary_board) -> bool:
        '''
        Tells the player which square needs to have a piece on it.
        yellow light on the square that needs a piece
        green light on the square that have a piece
        '''

        is_setup_correct = False
        
        # Compare the binary board with the squares that need a piece
        diff = binary_board - self.binary_board

        if not diff.any() :
            # The board is already set up correctly
            is_setup_correct = True
            self.led_com.reset_led_board()
            return is_setup_correct
        
        # Send the information to the LED board by highlighting the squares that need a piece
        self.led_com.highlight_squares_led_board(np.where(diff == -1)[0], (255, 255, 0))

        # Get the list of indices where diff == 0 and self.binary_board == 1
        # These are the squares that have a piece on them
        squares_with_piece = np.where((diff == 0) & (self.binary_board == 1))[0]
        self.led_com.highlight_squares_led_board(squares_with_piece, (0, 255, 0))


        return is_setup_correct
    


        






