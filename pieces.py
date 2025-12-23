""" Enthält die Klassen der Spielfiguren """

from typing import TYPE_CHECKING
from move import Move
if TYPE_CHECKING:
    import board as bd


class Piece:
    """  Elternklasse der Spielfiguren """
    # Rochade möglich Attribut/Methode
    def __init__(self, color: str, position: tuple, notation: str, is_pawn: bool = False):
        self.color = color
        self._position = position
        self.notation = notation
        self.pawn = is_pawn

    def move_to(self, next_position):
        """ Aktualisiert die Position der Figur """
        self.position = next_position

    @property
    def is_pawn(self) -> bool:
        """ Ist die Figur ein Bauer """
        return self.pawn
    
    def get_image_path(self) -> str:
        """ Gibt den Pfad zum Bild der Figur zurück """
        return f'pieces/{self.color}_{self.notation}.png'

    @property
    def position(self) -> tuple:
        """ Getter für die Position der Figur """
        return self._position

    @position.setter
    def position(self, value: tuple):
        """ Setter für die Position der Figur """
        self._position = value

    @staticmethod
    def _is_valid_square(row: int, col: int) -> bool:
        """Prüft ob eine Position auf dem Brett liegt.
        
        Args:
            row: Zeile (0-7)
            col: Spalte (0-7)
            
        Returns:
            True wenn Position gültig ist
        """
        return 0 <= row < 8 and 0 <= col < 8


class King(Piece):
    """ König
    :Attribut: moved gibt an, ob die Figur bewegt worden ist
            checkmate gibt an, ob der König im Schach steht
    """
    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='K')
        self.moved = False  # Für Rochade (O-O) wichtig
        self.checkmate = False
        self.castling_rights = {'kingside': True, 'queenside': True}

    def get_legal_moves(self, board: 'bd.Board') -> list[Move]:
        """
        Gibt alle legalen Züge des Königs zurück.
        :param board: Board-Objekt mit board.squares als np.array
        :return: Liste von Move-Objekten
        """
        legal_moves = []

        directions = [
            (1, 0), (0, 1), (-1, 0), (0, -1),
            (1, 1), (-1, -1), (-1, 1), (1, -1)
        ]

        self_row, self_col = self.position

        for (dx, dy) in directions:

            row = self_row + dx
            col = self_col + dy

            if 0 <= row < 8 and 0 <= col < 8:
                target = board.squares[row, col]

                if not target:  # Leeres Feld
                    legal_moves.append(Move(self.position, (row, col), self, None))

                elif target.color != self.color:  # Schlagen möglich
                    legal_moves.append(Move(self.position, (row, col), self, target))

        return legal_moves

    def __str__(self):
        # Unicode: ♔ (white) U+2654, ♚ (black) U+265A
        return "♚" if self.color == "black" else "♔"


class Queen(Piece):
    """ Dame """

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='Q')

    def get_legal_moves(self, board: 'bd.Board') -> list[Move]:
        """
        Gibt alle legalen Züge der Dame zurück.
        :param board: 2D np.array mit Figurenobjekten oder None
        :return: Liste von Move-Objekten
        """
        legal_moves = []

        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),   # vertikal & horizontal
            (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal
        ]

        for dx, dy in directions:

            row, col = self.position

            while True:
                row += dx
                col += dy

                if not self._is_valid_square(row, col):
                    break  # außerhalb des Brettes

                target = board.squares[row, col]

                if target is None:  # Leeres Feld
                    legal_moves.append(Move(self.position, (row, col), self, None))

                elif target.color != self.color:  # Schlagen möglich
                    legal_moves.append(Move(self.position, (row, col), self, target))
                    break

                else:  # Eigene Figur blockiert
                    break

        return legal_moves

    def __str__(self):
        return "♛" if self.color == "black" else "♕"


class Rook(Piece):
    """ Turm """

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='R')
        self.moved = False

    def get_legal_moves(self, board: 'bd.Board') -> list[Move]:
        """
        Gibt alle legalen Züge des Turms zurück.
        :param board: 2D np.array mit Figurenobjekten oder None
        :return: Liste von Move-Objekten
        """
        legal_moves = []

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in directions:

            row, col = self.position

            while True:
                row += dx
                col += dy

                if not (0 <= row < 8 and 0 <= col < 8):
                    break

                target = board.squares[row, col]

                if target is None:  # Leeres Feld
                    legal_moves.append(Move(self.position, (row, col), self, None))

                elif target.color != self.color:  # Schlagen möglich
                    legal_moves.append(Move(self.position, (row, col), self, target))
                    break

                else:  # Eigene Figur blockiert
                    break

        return legal_moves

    def __str__(self):
        return "♜" if self.color == "black" else "♖"


class Bishop(Piece):
    """ Läufer"""

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='B')

    def get_legal_moves(self, board: 'bd.Board') -> list[Move]:
        """
        Gibt alle legalen Züge des Läufers zurück.
        :param board: 2D np.array mit Figurenobjekten oder None
        :return: Liste von Move-Objekten
        """
        legal_moves = []

        directions = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

        for dx, dy in directions:

            row, col = self.position

            while True:
                row += dx
                col += dy

                if not self._is_valid_square(row, col):
                    break

                target = board.squares[row, col]

                if target is None:  # Leeres Feld
                    legal_moves.append(Move(self.position, (row, col), self, None))

                elif target.color != self.color:  # Schlagen möglich
                    legal_moves.append(Move(self.position, (row, col), self, target))
                    break

                else:  # Eigene Figur blockiert
                    break

        return legal_moves

    def __str__(self):
        return "♝" if self.color == "black" else "♗"
    

class Knight(Piece):
    """ Springer """

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='N')

    def get_legal_moves(self, board: 'bd.Board') -> list[Move]:
        """
        Gibt alle legalen Züge des Springers zurück.
        :param board: 2D np.array mit Figurenobjekten oder None
        :return: Liste von Move-Objekten
        """
        legal_moves = []

        directions = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]

        self_row, self_col = self.position

        for dx, dy in directions:
            row = self_row + dx
            col = self_col + dy

            if self._is_valid_square(row, col):
                target = board.squares[row, col]

                if target is None:  # Leeres Feld
                    legal_moves.append(Move(self.position, (row, col), self, None))

                elif target.color != self.color:  # Schlagen möglich
                    legal_moves.append(Move(self.position, (row, col), self, target))

        return legal_moves

    def __str__(self):
        return "♞" if self.color == "black" else "♘"


class Pawn(Piece):
    """Bauer-Klasse für beide Farben."""

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='P', is_pawn=True)
        self.moved = False

    def get_legal_moves(self, board: 'bd.Board') -> list[Move]:
        """Gibt alle legalen Züge des Bauers zurück.
        
        Args:
            board: Board-Objekt mit board.squares als np.array
            
        Returns:
            Liste von Move-Objekten
        """
        # Richtung und Promotion-Reihe basierend auf Farbe
        direction = 1 if self.color == 'black' else -1
        promotion_row = 7 if self.color == 'black' else 0
        
        legal_moves = []
        row, col = self.position
        next_row = row + direction

        # Normaler Zug vorwärts
        if self._is_valid_square(next_row, col):
            if board.squares[next_row, col] is None:
                promotion = 'Q' if next_row == promotion_row else None
                legal_moves.append(
                    Move(self.position, (next_row, col), self, None,
                         promotion=promotion)
                )

        # En-passant
        if 0 <= col - 1 and col + 1 < 8:
            for y in [col + 1, col - 1]:
                target = board.squares[row, y]
                square_ahead = board.squares[next_row, col]
                if (target is not None and target.is_pawn and
                    target.color != self.color and square_ahead is None):
                    legal_moves.append(
                        Move(self.position, (next_row, y), self, target,
                             en_passant=True)
                    )

        # Zwei Felder vorwärts (erster Zug)
        double_row = row + 2 * direction
        if (not self.moved and self._is_valid_square(double_row, col) and
            board.squares[double_row, col] is None and
            board.squares[next_row, col] is None):
            legal_moves.append(
                Move(self.position, (double_row, col), self, None)
            )

        # Schlagen diagonal
        for dy in [1, -1]:
            target_row, target_col = next_row, col + dy
            if self._is_valid_square(target_row, target_col):
                target = board.squares[target_row, target_col]
                if target is not None and target.color != self.color:
                    promotion = 'Q' if target_row == promotion_row else None
                    legal_moves.append(
                        Move(self.position, (target_row, target_col),
                             self, target, promotion=promotion)
                    )

        return legal_moves
    
    def __str__(self):
        return "♙" if self.color == "black" else "♟"




