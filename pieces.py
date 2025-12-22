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
    
    def __del__(self):
        """ War nur für Debug """
        # Destruktor: Wird aufgerufen, wenn Figur gelöscht wird
        #print(f"{self.notation} - {self.color} piece destroyed")


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

                if not (0 <= row < 8 and 0 <= col < 8):
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

            if (0 <= row < 8 and 0 <= col < 8):

                target = board.squares[row, col]

                if target is None:  # Leeres Feld
                    legal_moves.append(Move(self.position, (row, col), self, None))

                elif target.color != self.color:  # Schlagen möglich
                    legal_moves.append(Move(self.position, (row, col), self, target))

        return legal_moves

    def __str__(self):
        return "♞" if self.color == "black" else "♘"


class BlackPawn(Piece):
    """ Schwarzer Bauer """

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='P', is_pawn=True)
        self.moved = False
        self.moved_2_once = False

    def get_legal_moves(self, board: 'bd.Board') -> list[Move]:
        """
        Gibt alle legalen Züge des Bauers zurück.
        :param board: 2D np.array mit Figurenobjekten oder None
        :return: Liste von Move-Objekten
        """
        legal_moves = []

        row, col = self.position

        if row + 1 < 8:
            if board.squares[row + 1, col] is None: # Ziehen möglich
                legal_moves.append(Move(self.position, (row + 1, col), self, None))

        if 0 <= col -1 and col + 1 < 8:  # En-passant
            for (x, y) in [(row, col + 1), (row, col - 1)]:
                target = board.squares[x, y]
                square = board.squares[row + 1 , col]
                if target is not None and target.is_pawn and target.color != self.color and square is None:
                    legal_moves.append(Move(self.position, (x + 1, y), self, target, en_passant=True))

        if (self.moved is False) and (board.squares[row + 2, col] is None) and (board.squares[row + 1, col] is None):
            legal_moves.append(Move(self.position, (row + 2, col), self, None))  # Zwei Felder ziehen möglich

        for (x, y) in [(row + 1, col +1), (row + 1, col - 1)]:
            if (0 <= x < 8 and 0 <= y < 8):
                target = board.squares[x, y]
                if target is not None and target.color != self.color:
                    legal_moves.append(Move(self.position, (x, y), self, target))  # Schlagen möglich

        return legal_moves

    def __str__(self):
        return "♙"


class WhitePawn(Piece):
    """ Weißer Bauer """

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='P', is_pawn=True)
        self.moved = False
        self.moved_2_once = False

    def get_legal_moves(self, board: 'bd.Board') -> list[Move]:
        """
        Gibt alle legalen Züge des Bauers zurück.
        :param board: 2D np.array mit Figurenobjekten oder None
        :return: Liste von Move-Objekten
        """
        legal_moves = []

        row, col = self.position

        if 0 <= row - 1:
            if board.squares[row - 1, col] is None:
                    legal_moves.append(Move(self.position, (row - 1, col), self, None))  # Ziehen möglich

        if 0 <= col -1 and col + 1 < 8:  # En-passant
            for (x, y) in [(row, col + 1), (row, col - 1)]:
                target = board.squares[x, y]
                square = board.squares[row - 1 , col]
                if target is not None and target.is_pawn and target.color != self.color and square is None:
                    legal_moves.append(Move(self.position, (x - 1, y), self, target, en_passant=True))

        if (self.moved is False) and (board.squares[row - 2, col] is None) and (board.squares[row - 1, col] is None):
            legal_moves.append(Move(self.position, (row - 2, col), self, None))  # Zwei Felder ziehen möglich

        for (x, y) in [(row - 1, col + 1), (row - 1, col - 1)]:
            if (0 <= x < 8 and 0 <= y < 8):
                target = board.squares[x, y]
                if target is not None and target.color != self.color:
                    legal_moves.append(Move(self.position, (x, y), self, target))  # Schlagen möglich

        return legal_moves

    def __str__(self):
        return "♟"

