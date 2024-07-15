from chess_engine_lib.move import Move
import numpy as np

class Piece :
    def __init__(self) -> None:
        self.position: int = -1
        self.color: str = "w"
        self.name: str = "piece"

    def possible_moves(self, chess_board, position) -> list[Move]:
        '''
        Returns a list of possible moves for the piece.
        @param chess_board: The chessnp.array().
        @return: A list of possible moves for the piece.
        '''
        return []
    
    def move(self, new_position: list[int, int]) -> None:
        '''
        Moves the piece to a new position.
        @param new_position: The new position of the piece.
        '''
        self.position = new_position

    def __repr__(self) -> str:
        return self.name
        

class Pawn(Piece):
    def __init__(self, color:str) -> None:
        super().__init__()
        self.color: str = color
        if color == "w":
            self.name: str = "P"
        else:
            self.name: str = "p"

    def possible_moves(self, chess_board, position) -> list[Move]:
        '''
        The pawn can move one square forward at a time, except for the first move, where it can move two squares forward.
        The pawn can capture pieces one square diagonally in front of it.
        En passant is possible if the opponent moves a pawn two squares forward from its starting position, and the pawn could have captured it had it moved only one square forward.
        '''
        moves_list: list[Move] = []
        dir_val = 1 if self.color == "w" else -1

        if chess_board.board_list[position + 8 * dir_val] == None:
            #Basic pawn move forward one square
            moves_list.append(Move(self.name, position, position + 8 * dir_val))

            # If the pawn is at the starting position, it can move two squares forward
            if (position // 8 == 1 and self.color == "w") or (position // 8 == 6 and self.color == "b") :
                if chess_board.board_list[position + 16 * dir_val] == None :
                    moves_list.append(Move(self.name, position, position + 16 * dir_val))
        
        # Capture moves
        if position % 8 > 0 and chess_board.board_list[position + 8 * dir_val - 1] != None and chess_board.board_list[position + 8 * dir_val - 1].color != self.color :
            moves_list.append(Move(self.name, position, position + 8 * dir_val - 1, is_capturing=True))
        
        if position % 8 < 7 and chess_board.board_list[position + 8 * dir_val + 1] != None and chess_board.board_list[position + 8 * dir_val + 1].color != self.color :
            moves_list.append(Move(self.name, position, position + 8 * dir_val + 1, is_capturing=True))
        
        # En passant
        if chess_board.en_passant_square != '-' :
            index_en_passant = chess_board.square_to_index(chess_board.en_passant_square)
            if index_en_passant == position + 8 * dir_val - 1 or index_en_passant == position + 8 * dir_val + 1 :
                moves_list.append(Move(self.name, position, index_en_passant, is_en_passant=True))
        
        return moves_list

class Knight(Piece):
    def __init__(self, color:str) -> None:
        super().__init__()
        if color == "w":
            self.name: str = "N"
        else:
            self.name: str = "n"
        self.color: str = color
    
    def possible_moves(self, chess_board, position) -> list[Move]:
        '''
        The knight can move in an L shape.
        '''
        moves_list: list[Move] = []

        # Possible moves for the knight 
        possible_moves = [[1,2], [2,1], [-1,2], [-2,1], [1,-2], [2,-1], [-1,-2], [-2,-1]]
        for move in possible_moves :
            current_position_x = position % 8 + move[0]
            current_position_y = position // 8 + move[1]
            if current_position_x >= 0 and current_position_x < 8 and current_position_y >= 0 and current_position_y < 8 :
                target_position = current_position_y * 8 + current_position_x
                if chess_board.board_list[target_position] == None :
                    moves_list.append(Move(self.name, position, target_position))
                else :
                    if chess_board.board_list[target_position].color != self.color :
                        moves_list.append(Move(self.name, position, target_position, is_capturing=True))
    
        return moves_list

class Bishop(Piece):
    def __init__(self, color:str) -> None:
        super().__init__()
        self.color: str = color
        if color == "w":
            self.name: str = "B"
        else:
            self.name: str = "b"
    
    def possible_moves(self, chess_board, position) -> list[Move]:
        '''
        The bishop can move diagonally.
        '''
        moves_list: list[Move] = []

        directions_to_check = [[1,1], [1,-1], [-1, -1], [-1, 1]] 
        for direction in directions_to_check :
            
            current_position_x = position % 8 + direction[0]
            current_position_y = position // 8 + direction[1]
            
            while current_position_x >= 0 and current_position_x < 8 and current_position_y >= 0 and current_position_y < 8 :
                target_position = current_position_y * 8 + current_position_x
                if chess_board.board_list[target_position] == None :
                    moves_list.append(Move(self.name, position, target_position))
                else :
                    if chess_board.board_list[target_position].color != self.color :
                        moves_list.append(Move(self.name, position, target_position, is_capturing=True))
                    break
                current_position_x += direction[0]
                current_position_y += direction[1]

        # Possible moves for the bishop in the 4 diagonals
        return moves_list

class Rook(Piece):
    def __init__(self, color:str) -> None:
        super().__init__()
        self.color: str = color
        if color == "w":
            self.name: str = "R"
        else:
            self.name: str = "r"
    
    def possible_moves(self, chess_board, position) -> list[Move]:
        '''
        The rook can move horizontally and vertically.
        '''
        moves_list: list[Move] = []

        directions_to_check = [[1,0], [0,1], [-1, 0], [0, -1]]
        for direction in directions_to_check :
            
            current_position_x = position % 8 + direction[0]
            current_position_y = position // 8 + direction[1]
            
            while current_position_x >= 0 and current_position_x < 8 and current_position_y >= 0 and current_position_y < 8 :
                target_position = current_position_y * 8 + current_position_x
                if chess_board.board_list[target_position] == None :
                    moves_list.append(Move(self.name, position, target_position))
                else :
                    if chess_board.board_list[target_position].color != self.color :
                        moves_list.append(Move(self.name, position, target_position, is_capturing=True))
                    break
                current_position_x += direction[0]
                current_position_y += direction[1]

        return moves_list

class Queen(Piece):
    def __init__(self, color:str) -> None:
        super().__init__()
        self.color: str = color
        if color == "w":
            self.name: str = "Q"
        else:
            self.name: str = "q"
    
    def possible_moves(self, chess_board, position) -> list[Move]:
        '''
        The queen can move horizontally, vertically and diagonally.
        '''
        moves_list: list[Move] = []

        directions_to_check = [[1,1], [1,-1], [-1, -1], [-1, 1], [1,0], [0,1], [-1, 0], [0, -1]]
        for direction in directions_to_check :
            
            current_position_x = position % 8 + direction[0]
            current_position_y = position // 8 + direction[1]
            
            while current_position_x >= 0 and current_position_x < 8 and current_position_y >= 0 and current_position_y < 8 :
                target_position = current_position_y * 8 + current_position_x
                if chess_board.board_list[target_position] == None :
                    moves_list.append(Move(self.name, position, target_position))
                else :
                    if chess_board.board_list[target_position].color != self.color :
                        moves_list.append(Move(self.name, position, target_position, is_capturing=True))
                    break
                current_position_x += direction[0]
                current_position_y += direction[1]

        return moves_list

class King(Piece):
    def __init__(self, color:str) -> None:
        super().__init__()
        self.color: str = color
        if color == "w":
            self.name: str = "K"
        else:
            self.name: str = "k"
    
    def possible_moves(self, chess_board, position) -> list[Move]:
        '''
        The king can move one square in any direction.
        '''
        moves_list: list[Move] = []

        # TODO: Implement castling, check and checkmate (prevent the king from moving into check)

        directions_to_check = [[1,1], [1,-1], [-1, -1], [-1, 1], [1,0], [0,1], [-1, 0], [0, -1]]
        for direction in directions_to_check :
            
            current_position_x = position % 8 + direction[0]
            current_position_y = position // 8 + direction[1]
            
            if current_position_x >= 0 and current_position_x < 8 and current_position_y >= 0 and current_position_y < 8 :
                target_position = current_position_y * 8 + current_position_x
                if chess_board.board_list[target_position] == None :
                    moves_list.append(Move(self.name, position, target_position))
                else :
                    if chess_board.board_list[target_position].color != self.color :
                        moves_list.append(Move(self.name, position, target_position, is_capturing=True))
                current_position_x += direction[0]
                current_position_y += direction[1]
        
        # White king 
        if self.color == "w" :
            if chess_board.castling_rights_w != "" :
                if chess_board.castling_rights_w.find("K") != -1 :
                    if chess_board.get_piece_at("b1") == None and chess_board.get_piece_at("c1") == None and chess_board.get_piece_at("d1") == None :
                        moves_list.append(Move(self.name, position, chess_board.square_to_index("c1")))
                if chess_board.castling_rights_w.find("Q") != -1 :
                    if chess_board.get_piece_at("g1") == None and chess_board.get_piece_at("f1") == None :
                        moves_list.append(Move(self.name, position, chess_board.square_to_index("g1")))
        elif self.color == "b" :
            if chess_board.castling_rights_b != "" :
                if chess_board.castling_rights_b.find("k") != -1 :
                    if chess_board.get_piece_at("b8") == None and chess_board.get_piece_at("c8") == None and chess_board.get_piece_at("d8") == None :
                        moves_list.append(Move(self.name, position, chess_board.square_to_index("c8")))
                if chess_board.castling_rights_b.find("q") != -1 :
                    if chess_board.get_piece_at("g8") == None and chess_board.get_piece_at("f8") == None :
                        moves_list.append(Move(self.name, position, chess_board.square_to_index("g8")))
        return moves_list
