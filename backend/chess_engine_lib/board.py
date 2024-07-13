from chess_engine_lib.pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King 
from chess_engine_lib.move import Move
import numpy as np

class Board :
    def __init__(self) :
        self.board_list: list[Piece] = [None for _ in range(64)]
        self.player_to_move: str = "w"
        self.castling_rights_w: str = "KQ"
        self.castling_rights_b: str = "kq"
        self.en_passant_square: str = '-'
        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1

    def get_board_fen(self) -> str:
        '''
        Returns the FEN of the board.
        @param board: The board.
        @return: The FEN of the board.
        '''
        fen: str = ""

        # Parse the pieces positions
        empty_squares: int = 0
        for i in range(0,64) :
            if i % 8 == 0 and i != 0 :
                if empty_squares != 0 :
                    fen += str(empty_squares)
                    empty_squares = 0
                fen += "/"
            if self.board_list[i] == None :
                empty_squares += 1
            else :
                if empty_squares != 0 :
                    fen += str(empty_squares)
                    empty_squares = 0
                fen += self.board_list[i].name
        
        # Parse the player to move
        fen += " " + self.player_to_move

        # Parse the castling rights
        fen += " "
        if self.castling_rights_w == "" and self.castling_rights_b == "" :
            fen += "-"
        else :
            if self.castling_rights_w != "" :
                fen += self.castling_rights_w
            if self.castling_rights_b != "" :
                fen += self.castling_rights_b

        # TODO : Parse these sections of the FEN -------------------------

        # Parse the en passant square
        fen += " "
        if self.en_passant_square == "-" :
            fen += "-"
        else :
            fen += self.en_passant_square
        
        # Parse the halfmove clock
        fen += " " + str(self.halfmove_clock)

        # Parse the fullmove number
        fen += " " + str(self.fullmove_number)

        
        return fen
    
    def set_board_fen(self, fen: str) -> None:
        '''
        Sets the board to the FEN.
        - The FEN is a string that represents the board.
        - Example : rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
        - pieces positions -- player to move -- castling rights -- en passant square -- halfmove clock -- fullmove number
        @param fen: The FEN.
        '''
        self.board_list: list[Piece] = []

        fen_split: list[str] = fen.split(" ")

        pieces_positions: str = fen_split[0][::-1]

        # Parse the pieces positions
        for row in pieces_positions.split("/") :
            for char in row :
                if char.isdigit() :
                    for _ in range(int(char)) :
                        self.board_list.append(None)
                else :
                    # Check capitalization to determine color
                    color: str = "w"
                    if char.isupper() == False :
                        color = "b"
            
                    match char.lower() :
                        case "p" :
                            self.board_list.append(Pawn(color))
                        case "n" :
                            self.board_list.append(Knight(color))
                        case "b" :
                            self.board_list.append(Bishop(color))
                        case "r" :
                            self.board_list.append(Rook(color))
                        case "q" :
                            self.board_list.append(Queen(color))
                        case "k" :
                            self.board_list.append(King(color))
                        case _ :
                            print(fen)
                            raise Exception("Invalid character in FEN.")
                        
        # Parse the player to move
        self.player_to_move = fen_split[1]

        # Parse the castling rights
        self.castling_rights_w = ""
        self.castling_rights_b = ""
        if fen_split[2] != "-" :
            for char in fen_split[2] :
                if char.isupper() :
                    self.castling_rights_w += char
                else :
                    self.castling_rights_b += char
        
        # Parse the en passant square
        self.en_passant_square = fen_split[3]

        # Parse the halfmove clock
        self.halfmove_clock = int(fen_split[4])

        # Parse the fullmove number
        self.fullmove_number = int(fen_split[5])
    
    def get_board_visual(self) -> str:
        '''
        Returns the visual representation of the board.
        @return: The visual representation of the board.
        '''
        visual: str = "    --------------------------\n"
        square_nb = 64
        for i in range(square_nb,0,-1) :
            if i == square_nb :
                visual += " 8 | "
            if i != square_nb :
                visual += " "
            if i % 8 == 0 and i != square_nb :
                visual += f"|\n {i // 8} | "
            if self.board_list[i-1] == None :
                visual += "-"
            else :
                visual += self.board_list[i-1].name
            visual += " "
        visual += " | <-- start"
        visual += "\n"
        visual += "    --------------------------\n"
        visual += "     a  b  c  d  e  f  g  h   "
        return visual
    
    def get_moves_possible_in_position(self, check_verification=False) -> None:
        '''
        Updates the list of moves possible in the current position.
        '''
        moves_possible_in_position_list = []
        # Loop through the board
        for i in range(0,64) :
            # If there is a piece on the square
            if self.board_list[i] != None :
                # If the piece is of the color of the player to move
                if self.board_list[i].color == self.player_to_move :

                    # Get the possible moves of the piece
                    possible_moves: list[Move] = self.board_list[i].possible_moves(self, i)
                    # Loop through the possible moves
                    for move in possible_moves :

                        if check_verification : 
                            # Check if the move is valid
                            board_copy = self.get_copy()
                            board_copy.execute_move(move)
                            if board_copy.is_piece_under_attack(board_copy.get_king_index(self.player_to_move)) == False :
                                moves_possible_in_position_list.append(move)

                        else :
                            moves_possible_in_position_list.append(move)
                    
        return moves_possible_in_position_list
    
    
    def is_piece_under_attack(self, piece_index) -> bool:
        '''
        Checks if a piece is under attack.
        @param piece_index: The index of the piece to check.
        @return: True if the piece is under attack, False otherwise.
        '''

        for move in self.get_moves_possible_in_position(check_verification=False) :
            if move.is_capturing and move.end_pos_index == piece_index :
                return True
        
        return False
    
    def execute_move(self, move) -> None:
        '''
        Executes a move.
        @param move: The move to execute.
        '''

        # Check if the kind of move
        if move.get_algebraic_notation().lower() in ["o-o", "o-o-o"]:
            row = 1 if 'O' in move.get_algebraic_notation() else 8

            # Castling kingside 
            if move.get_algebraic_notation().lower() == "o-o" :
                # Move the king to g
                self.board_list[self.square_to_index("g" + str(row))] = self.board_list[self.square_to_index("e" + str(row))]
                self.board_list[self.square_to_index("e" + str(row))] = None

                # Move the rook to f
                self.board_list[self.square_to_index("f" + str(row))] = self.board_list[self.square_to_index("h" + str(row))]
                self.board_list[self.square_to_index("h" + str(row))] = None

                print("HERE")
            else :
                # Castling queenside
                # Move the king to c
                self.board_list[self.square_to_index("c" + str(row))] = self.board_list[self.square_to_index("e" + str(row))]
                self.board_list[self.square_to_index("e" + str(row))] = None

                # Move the rook to d
                self.board_list[self.square_to_index("d" + str(row))] = self.board_list[self.square_to_index("a" + str(row))]
                self.board_list[self.square_to_index("a" + str(row))] = None  
                print("HERE2")
        elif move.is_en_passant :
            # Make the move (if it is an en passant move)
            # Move the piece to the end position
            self.board_list[move.end_pos_index] = self.board_list[move.start_pos_index]
            self.board_list[move.start_pos_index] = None

            # Remove the captured pawn
            if self.player_to_move == "w" :
                self.board_list[move.end_pos_index - 8] = None
            else :
                self.board_list[move.end_pos_index + 8] = None

        else :
            # Make the move (if it is a classic move or a capture move)

            # Move the piece to the end position
            self.board_list[move.end_pos_index] = self.board_list[move.start_pos_index]
            self.board_list[move.start_pos_index] = None

        # Update en passant square (indicate the square behind the pawn moved two squares forward)
        if move.piece_name.lower() == "p" and abs(move.start_pos_index - move.end_pos_index) == 16 :
            indx= move.start_pos_index + (move.end_pos_index - move.start_pos_index) // 2
            print(indx)
            self.en_passant_square = self.index_to_square(indx)
        else :
            self.en_passant_square = "-"


        # Update the castling rights
        if 'k' in self.castling_rights_b :
            if move.get_algebraic_notation() == "o-o" :
                self.castling_rights_b = self.castling_rights_b.replace('k', '')
        if 'q' in self.castling_rights_b :
            if move.get_algebraic_notation() == "o-o-o" :
                self.castling_rights_b = self.castling_rights_b.replace('q', '')
        
        if 'K' in self.castling_rights_w :
            if move.get_algebraic_notation() == "O-O" :
                self.castling_rights_w = self.castling_rights_w.replace('K', '')
        if 'Q' in self.castling_rights_w :
            if move.get_algebraic_notation() == "O-O-O" :
                self.castling_rights_w = self.castling_rights_w.replace('Q', '')

        # Switch player to move
        self.player_to_move = "w" if self.player_to_move == "b" else "b"

        # Update the last valid self
        self.last_valid_board = self.get_board_fen()
    
    def board_correspond_starting_pos(self) -> bool:
        '''
        Returns whether the board corresponds to the starting position.
        @return: Whether the board corresponds to the starting position.
        '''
        return self.get_board_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def get_piece_at(self, square: str) -> Piece:
        '''
        Returns the piece at the square.
        @param square: The square name (e.g. "e4").
        @return: The piece at the square.
        '''
        square_index: int = self.square_to_index(square)
        return self.board_list[square_index]
    
    def square_to_index(self, square: str) -> int:
        '''
        Returns the index of the square.
        @param square: The square name (e.g. "e4").
        @return: The index of the square.
        '''
        return (int(square[1]) - 1) * 8 + ord('h') - ord(square[0]) 

    def index_to_square(self, index: int) -> str:
        '''
        Returns the square of the index.
        @param index: The index.
        @return: The square of the index.
        '''
        return chr(ord('h') - index % 8) + str(index // 8 + 1)
    

    def get_copy(self) -> 'Board':
        '''
        Returns a copy of the board.
        @return: A copy of the board.
        '''
        board_copy = Board()
        board_copy.board_list = self.board_list.copy()
        board_copy.player_to_move = self.player_to_move
        board_copy.castling_rights_w = self.castling_rights_w
        board_copy.castling_rights_b = self.castling_rights_b
        board_copy.en_passant_square = self.en_passant_square
        board_copy.halfmove_clock = self.halfmove_clock
        board_copy.fullmove_number = self.fullmove_number
        return board_copy
    
    def get_king_index(self, color: str) -> int:
        '''
        Returns the index of the king of a color.
        @param color: The color of the king.
        @return: The index of the king.
        '''
        if color == "w" :
            return self.board_list.index(King("w"))
        else :
            return self.board_list.index(King("b"))
        

    

