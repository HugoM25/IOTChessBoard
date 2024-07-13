# Import custom modules
from chess_engine_lib.board import Board
from chess_engine_lib.pieces import Piece
from chess_engine_lib.move import Move
from chess_engine_lib.led_com import LedCom

# Import general modules
import numpy as np
import time 

class ChessEngine:
    def __init__(self):
        self.board = Board()
        self.led_com = LedCom()

        self.test_board = Board()

        self.in_hand_pieces = []
        self.captured_pieces = []

        self.last_valid_board = ""

        self.binary_board = np.zeros(64, dtype=int)
        self.current_move = 0

        self.moves_played = []

        self.castling_move = None
        self.square_to_put_rook_on = ""
        self.en_passant_move = None

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
 
    def handle_moves(self, new_binary_board) -> None :
        '''
        Handles the moves of the player.
        Figure out which piece was picked up and which piece was dropped. 
        @param binary_board: The binary board (1 a piece is there, 0 a piece is not there).
        '''

        # Detect the picked and dropped pieces
        picked_pieces_index, dropped_pieces_index = self.detect_pick_and_drop(new_binary_board)

        # If no move detected return
        if picked_pieces_index[0].size == 0 and  dropped_pieces_index[0].size == 0 :
            return 
        
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
                    self.led_com.highlight_square_led_board(self.board.square_to_index(self.square_to_put_rook_on))
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
                        self.board.execute_move(self.castling_move)
                        # Update the moves tracking
                        self.current_move += 1
                        self.moves_played.append(self.castling_move)
                        print(self.board.get_board_visual())
                        self.castling_move = None
                        self.square_to_put_rook_on = ""
                        self.led_com.reset_led_board()
                        self.in_hand_pieces.pop(0)
                else :
                    self.led_com.wrong_move_led_board()
        
        # En passant move
        if self.en_passant_move != None :
            if picked_pieces_index[0].size > 0 :
                # Get the piece picked up
                picked_piece_index = picked_pieces_index[0][0]
                picked_piece = self.board.board_list[picked_piece_index]

                # Check if the piece taken is a pawn under the en passant square
                if picked_piece != None and picked_piece.name.lower() == "p" :
                    self.captured_pieces.append([picked_piece, picked_piece_index])

                    self.board.execute_move(self.en_passant_move)
                    self.en_passant_move = None

                    self.current_move += 1
                    self.moves_played.append(self.en_passant_move)
                    print(self.board.get_board_visual())

                    self.led_com.reset_led_board()

                else :
                    self.led_com.wrong_move_led_board()


        # Handle the picked up pieces
        elif picked_pieces_index[0].size > 0 : 
            # Get the piece picked up
            picked_piece_index = picked_pieces_index[0][0]
            picked_piece = self.board.board_list[picked_piece_index]

            if picked_piece == None :
                # Piece could not be picked up there is no piece on the square
                # Should only happen on the simulator
                self.led_com.wrong_move_led_board()
                return 
            
            # Check the color of the piece
            if picked_piece.color != self.board.player_to_move : 
                if self.can_pieces_in_hand_take_piece(picked_piece_index) == False :
                    self.led_com.wrong_move_led_board()
            else : 
                # If the piece is of the color of the player to move
                # Get the possible moves of the piece
                possible_moves: list[Move] = picked_piece.possible_moves(self.board, picked_piece_index)
                print(f"Possible moves: {possible_moves}")
                self.led_com.highlight_move_led_board(possible_moves)
            
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
                return
            
            # Get the piece dropped (assume it is the first piece in hand)
            dropped_piece, last_know_pos = self.in_hand_pieces.pop(0)
            print(f"Piece dropped: {dropped_piece.name} on square {self.board.index_to_square(dropped_piece_index)}")

            # Check if the move is valid (check if the drop position is in the possible moves of the piece 
            # based on the last known position)
            possible_moves: list[Move] = dropped_piece.possible_moves(self.board, last_know_pos)
            valid_move, move_done = False, None

            if dropped_piece.color == self.board.player_to_move :
                for move in possible_moves :
                    if move.end_pos_index == dropped_piece_index :
                        valid_move, move_done = True, move
                        break
            
            if move_done != None and move_done.get_algebraic_notation() == self.board.en_passant_square :
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
                self.led_com.highlight_square_led_board(self.board.square_to_index(rook_square))

            elif valid_move : 
                # A valid move was done
                print(f"Valid move has been done! (Move done: {move_done})")
                self.board.execute_move(move_done)
                # Update the moves tracking
                self.current_move += 1
                self.moves_played.append(move)
                print(self.board.get_board_visual())
                
                # If the move is capturing a piece remove it from the hand pieces
                if move_done.is_capturing :
                    for piece_in_hand in self.in_hand_pieces :
                        if piece_in_hand[1] == move_done.end_pos_index :
                            self.in_hand_pieces.remove(piece_in_hand)
                            self.captured_pieces.append(piece_in_hand)
                            break
                
                self.led_com.reset_led_board()

            elif last_know_pos == dropped_piece_index : 
                # Clear the LED board
                self.led_com.reset_led_board()
            
            else : 
                self.led_com.wrong_move_led_board()
        
        print(f"Current hand pieces: {self.in_hand_pieces}")
        print(f"Current captured pieces: {self.captured_pieces}")
        
    





