class Move :
    def __init__(self, piece_name:str, start_pos_index:int, end_pos_index:int, is_capturing:bool=False, is_check:bool=False, is_checkmate:bool=False, is_en_passant:bool=False, is_stalemate:bool=False, promote_to:str="") -> None:
        self.piece_name = piece_name
        self.start_pos_index: int = start_pos_index
        self.end_pos_index: int = end_pos_index
        self.is_capturing: bool = is_capturing
        self.is_check: bool = is_check
        self.is_checkmate: bool = is_checkmate
        self.is_en_passant: bool = is_en_passant
        self.is_stalemate: bool = is_stalemate
        self.promote_to: str  = promote_to

    def get_algebraic_notation(self) -> str:
        '''
        Returns the algebraic notation of the move. i.e. "e4", "Nf3", "Qxd5", "O-O", "O-O-O", etc.
        @return: str
        '''
        algebraic_notation: str = ""
        piece_name_uppercase: str = self.piece_name.upper()

        # If the move is a castling move
        if piece_name_uppercase == "K" and abs(self.end_pos_index - self.start_pos_index) == 2 :
            if self.end_pos_index - self.start_pos_index <= 0 :
                if 'k' in self.piece_name :
                    algebraic_notation = "o-o"
                else :
                    algebraic_notation = "O-O"
            else :  
                if 'k' in self.piece_name :
                    algebraic_notation = "o-o-o"
                else :
                    algebraic_notation = "O-O-O"
            
            return algebraic_notation
            

        # If the piece is a pawn, we don't need to specify it in the algebraic notation
        if piece_name_uppercase != "P" :
            algebraic_notation += piece_name_uppercase

        # Add an "x" if the move is a capture
        if self.is_capturing :
            algebraic_notation += "x"

        algebraic_notation += chr(ord('h') - self.end_pos_index % 8)
        algebraic_notation += str(self.end_pos_index // 8 + 1)

        if self.promote_to != "" :
            algebraic_notation += f"={self.promote_to}"

        # Add a "+" if the move is a check or a "#" if the move is a checkmate
        if self.is_checkmate :
            algebraic_notation += "#"
        elif self.is_check :
            algebraic_notation += "+"
        elif self.is_stalemate :
            algebraic_notation += "$"

        return algebraic_notation
    
    def __str__(self) -> str:
        return self.get_algebraic_notation()
    
    def __repr__(self) -> str:
        return self.get_algebraic_notation()
    
