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
        self.setup_startpos()

    def setup_startpos(self):
        """ Erzeugt die Startaufstellung eines Schachbrettes """
		# Pawns
        for col in range(8):
            self.squares[1, col] = BlackPawn('black', (1, col))
            self.squares[6, col] = WhitePawn('white', (6, col))

        # Rooks
        self.squares[0, 0] = BlackPawn('black', (0, 0))
        self.squares[0, 7] = RightRook('black', (0, 7))
        self.squares[7, 0] = LeftRook('white', (7, 0))
        self.squares[7, 7] = RightRook('white', (7, 7))

        # Knights
        self.squares[0, 1] = Knight('black', (0, 1))
        self.squares[0, 6] = Knight('black', (0, 6))
        self.squares[7, 1] = Knight('white', (7, 1))
        self.squares[7, 6] = Knight('white', (7, 6))

        # Bishops
        self.squares[0, 2] = Bishop('black', (0, 2))
        self.squares[0, 5] = Bishop('black', (0, 5))
        self.squares[7, 2] = Bishop('white', (7, 2))
        self.squares[7, 5] = Bishop('white', (7, 5))

        # Queens / Kings
        self.squares[0, 3] = Queen('black', (0, 3))
        self.squares[7, 3] = Queen('white', (7, 3))
        self.squares[0, 4] = King('black', (0, 4))
        self.squares[7, 4] = King('white', (7, 4))

    def make_move(self, piece: Piece, next_position: tuple, target: Piece) -> bool:
        """ Zieht eine Figur auf dem Schachfeld """
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

    
if __name__ == "__main__":
    k = Board()
    print(k)