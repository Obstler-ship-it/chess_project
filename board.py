""" Diese Klasse stellt das Schachbrett mit allen Figuren als numpy 8x8 Array dar"""

import numpy as np
from pieces import Piece, BlackPawn, WhitePawn, Rook, Knight, Queen, King, Bishop
from move import Move


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
        br1 = Rook('black', (0, 0))
        br2 = Rook('black', (0, 7))
        wr1 = Rook('white', (7, 0))
        wr2 = Rook('white', (7, 7))
        
        self.squares[0, 0] = br1
        self.squares[0, 7] = br2
        self.squares[7, 0] = wr1
        self.squares[7, 7] = wr2
        
        self.black_pieces.extend([br1, br2])
        self.white_pieces.extend([wr1, wr2])

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
    
    def remove_piece(self, piece: Piece):
        """Entfernt geschlagene Figur aus Listen."""

        if piece in self.white_pieces:
            self.white_pieces.remove(piece)

        elif piece in self.black_pieces:
            self.black_pieces.remove(piece)

        else:
            raise ValueError('Unknown Piece!')

    def make_move(self, last_move: Move) -> bool:
        """ Zieht eine Figur auf dem Schachfeld """

        piece = last_move.piece
        old_pos = last_move.from_pos
        new_pos = last_move.to_pos
        captured = last_move.captured
        
        old_row, old_col = old_pos
        new_row, new_col = new_pos

        # Führe den Zug aus
        if (0 <= new_row < 8 and 0 <= new_col < 8):
            # Alte Position leer setzen
            self.squares[old_row, old_col] = None
            
            # Figur auf neue Position setzen
            self.squares[new_row, new_col] = piece
            
            # Position der Figur aktualisieren
            piece.move_to(new_pos)

            # Entferne geschlagene Figur falls vorhanden
            if captured:
                self.remove_piece(captured)
                # Wenn geschlagene Figur NICHT auf Zielfeld steht → En-passant!
                if captured.position != new_pos:
                    captured_row, captured_col = captured.position
                    self.squares[captured_row, captured_col] = None
            
            # Setze moved-Flag für Türme, Könige und Bauern
            if hasattr(piece, 'moved'):
                piece.moved = True
            
            return True
        
        return False

    def __str__(self):
        display = ""
        for row in self.squares:
            display += " ".join(str(cell) if cell is not None else "." for cell in row)
            display += "\n"
        return display
