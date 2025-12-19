""" Diese Klasse stellt das Schachbrett mit allen Figuren als numpy 8x8 Array dar"""

import numpy as np
from pieces import Piece, BlackPawn, WhitePawn, LeftRook, RightRook, Knight, Queen, King, Bishop


class Board:
    """ Repräsentiert das Schachbrett
	Attribute:
		squares: enthält den Wert einer Figur auf einem Schachbrett
	"""

    def __init__(self):
        """ Konstruktor """
        self.squares = np.full((8, 8), None, dtype=object)
        
        # Figuren-Listen
        self.white_pieces = []
        self.black_pieces = []
        
        # Direkte König-Referenzen
        self.white_king = None
        self.black_king = None

    def setup_startpos(self):
        """ Erzeugt die Startaufstellung eines Schachbrettes """
        # Listen leeren
        self.white_pieces = []
        self.black_pieces = []
        
        # Pawns
        for col in range(8):
            bp = BlackPawn('black', (1, col))
            wp = WhitePawn('white', (6, col))
            self.squares[1, col] = bp
            self.squares[6, col] = wp
            self.black_pieces.append(bp)
            self.white_pieces.append(wp)

        # Rooks
        blr = LeftRook('black', (0, 0))
        brr = RightRook('black', (0, 7))
        wlr = LeftRook('white', (7, 0))
        wrr = RightRook('white', (7, 7))
        
        self.squares[0, 0] = blr
        self.squares[0, 7] = brr
        self.squares[7, 0] = wlr
        self.squares[7, 7] = wrr
        
        self.black_pieces.extend([blr, brr])
        self.white_pieces.extend([wlr, wrr])

        # Knights
        bn1 = Knight('black', (0, 1))
        bn2 = Knight('black', (0, 6))
        wn1 = Knight('white', (7, 1))
        wn2 = Knight('white', (7, 6))
        
        self.squares[0, 1] = bn1
        self.squares[0, 6] = bn2
        self.squares[7, 1] = wn1
        self.squares[7, 6] = wn2
        
        self.black_pieces.extend([bn1, bn2])
        self.white_pieces.extend([wn1, wn2])

        # Bishops
        bb1 = Bishop('black', (0, 2))
        bb2 = Bishop('black', (0, 5))
        wb1 = Bishop('white', (7, 2))
        wb2 = Bishop('white', (7, 5))
        
        self.squares[0, 2] = bb1
        self.squares[0, 5] = bb2
        self.squares[7, 2] = wb1
        self.squares[7, 5] = wb2
        
        self.black_pieces.extend([bb1, bb2])
        self.white_pieces.extend([wb1, wb2])

        # Queens
        bq = Queen('black', (0, 3))
        wq = Queen('white', (7, 3))
        
        self.squares[0, 3] = bq
        self.squares[7, 3] = wq
        
        self.black_pieces.append(bq)
        self.white_pieces.append(wq)
        
        # Kings (speichern!)
        self.black_king = King('black', (0, 4))
        self.white_king = King('white', (7, 4))
        
        self.squares[0, 4] = self.black_king
        self.squares[7, 4] = self.white_king
        
        self.black_pieces.append(self.black_king)
        self.white_pieces.append(self.white_king)
    
    def remove_piece(self, piece):
        """Entfernt geschlagene Figur aus Listen."""
        if piece.color == 'white':
            if piece in self.white_pieces:
                self.white_pieces.remove(piece)
        else:
            if piece in self.black_pieces:
                self.black_pieces.remove(piece)

    def make_move(self, piece: Piece, next_position: tuple, target: Piece = None) -> bool:
        """ Zieht eine Figur auf dem Schachfeld """
        if target is not None:
            self.remove_piece(target)
        row, col = piece.position
        if (0 <= row < 8 and 0 <= col < 8):
            self.squares[row, col] = None
            self.squares[row, col] = piece
            piece.move_to = next_position

    def __str__(self):
        display = ""
        for row in self.squares:
            display += " ".join(str(cell) if cell is not None else "." for cell in row)
            display += "\n"
        return display
