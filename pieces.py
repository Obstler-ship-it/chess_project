""" Enthält die Klassen der Spielfiguren """

import numpy as np

class Piece:
    """  Elternklasse der Spielfiguren """
    # Rochade möglich Attribut/Methode
    def __init__(self, color: str, position: tuple, notation: str, value: int):
        self.color = color
        self.position = position
        self.value = value
        self.notation = notation

    def move_to(self, next_position):
        """ Aktualisiert die Position der Figur """
        self.position = next_position

    def ___del___(self):
        print(f"{self.notation} - {self.color} piece destroyed")


class King(Piece):
    """ König
    :Attribut: moved gibt an, ob die Figur bewegt worden ist
            checkmate gibt an, ob der König im Schach steht
    """
    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='K', value=50_000)
        self.moved = False  #Für O-O wichtig
        self.checkmate = False
        self.castling_rights = {'kingside': True, 'queenside': True}

    @staticmethod
    def calculate_value(row, col):
        """ Soll auf Eigenschaft der Figur bassierend schnell eine Grobe vorhersage über den Wert des Zuges schätzen"""
        return True

    def get_legal_moves(self, board) -> list:
        """
        Gibt alle legalen Züge des Königs zurück.
        :param board: Board-Objekt mit board.squares als np.array
        :return: Tuple (legal_moves, blocked_by)
        legal_moves: Liste von Tupeln (row, col, blocked, value, self)
        blocked_by: Liste von (row, col), Felder die blockiert sind
        """
        legal_moves = []
        blocked_by = []

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

                if not target: #leeres Feld
                    value = self.calculate_value(row, col)
                    legal_moves.append((row, col, False, value, self))

                elif target.color != self.color: #schlagen möglich
                    value = self.value - target.value
                    legal_moves.append((row, col, True, value, self))
                    blocked_by.append((row, col))

                else: #eigene Figur blockiert
                    blocked_by.append((row, col, self))

        return legal_moves, blocked_by

    def __str__(self):
        # Unicode: ♔ (white) U+2654, ♚ (black) U+265A
        return "♚" if self.color == "black" else "♔"

class Queen(Piece):
    """ Dame """

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='Q', value=900)

    def get_legal_moves(self, board: np.ndarray) -> tuple[list, list]:
        """
        Gibt alle legalen Züge der Dame zurück.
        :param board: 2D np.array mit Figurenobjekten oder None
        :return: Tuple (legal_moves, blocked_by)
        """
        legal_moves = []
        blocked_by = []

        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),   # vertikal & horizontal
            (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal
        ]

        self_row, self_col = self.position

        for dx, dy in directions:
            row, col = self.position

            while True:
                row = self_row + dx
                col = self_col + dy

                if not (0 <= row < 8 and 0 <= col < 8):
                    break  # außerhalb des Brettes

                target = board[row, col]

                if target is None: #leeres Feld
                    value = self.calculate_value(row, col)  #  für Move-Ordering
                    legal_moves.append((row, col, False, value, self))

                elif target.color != self.color: #schlagen möglich
                    value = self.value - target.value
                    legal_moves.append((row, col, True, value, self))
                    blocked_by.append((row, col))
                    break

                else:  # eigene Figur blockiert
                    blocked_by.append((row, col))
                    break

        return legal_moves, blocked_by

    def __str__(self):
        return "♛" if self.color == "black" else "♕"

class Rook(Piece):
    """ Turm """

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='R', value=500)

    def get_legal_moves(self, board: np.ndarray) -> tuple[list, list]:
        """
        Gibt alle legalen Züge des Turms zurück.
        :param board: 2D np.array mit Figurenobjekten oder None
        :return: Tuple (legal_moves, blocked_by)
        """
        legal_moves = []
        blocked_by = []

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        self_row, self_col = self.position

        for dx, dy in directions:
            row, col = self.position

            while True:
                row = self_row + dx
                col = self_col + dy

                if not (0 <= row < 8 and 0 <= col < 8):
                    break

                target = board[row, col]

                if target is None: #leeres Feld
                    value = self.calculate_value(row, col)
                    legal_moves.append((row, col, False, value, self))

                elif target.color != self.color: #schlagen möglich
                    value = self.value - target.value
                    legal_moves.append((row, col, True, value, self))
                    blocked_by.append((row, col))
                    break

                else:  # eigene Figur blockiert
                    blocked_by.append((row, col))
                    break 

        return legal_moves, blocked_by

    def __str__(self):
        return "♜" if self.color == "black" else "♖"

class Bishop(Piece):
    """ Läufer"""

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='B', value=300)

    def get_legal_moves(self, board: np.ndarray) -> tuple[list, list]:
        """
        Gibt alle legalen Züge des Läufers zurück.
        :param board: 2D np.array mit Figurenobjekten oder None
        :return: Tuple (legal_moves, blocked_by)
        """
        legal_moves = []
        blocked_by = []

        directions = [(1, 1), (-1, 1), (-1, 1), (1, -1)]

        self_row, self_col = self.position

        for dx, dy in directions:

            while True:

                row = self_row + dx
                col = self_col + dy

                if not (0 <= row < 8 and 0 <= col < 8):
                    break

                target = board[row, col]

                if target is None: #leeres Feld
                    value = self.calculate_value(row, col)
                    legal_moves.append((row, col, False, value, self))

                elif target.color != self.color: #schlagen möglich
                    value = self.value - target.value
                    legal_moves.append((row, col, True, value, self))
                    blocked_by.append((row, col))
                    break

                else:  # eigene Figur blockiert
                    blocked_by.append((row, col))
                    break

        return legal_moves, blocked_by

    def __str__(self):
        return "♝" if self.color == "black" else "♗"

class Knight(Piece):
    """ Springer """

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='N', value=300)

    def get_legal_moves(self, board: np.ndarray) -> tuple[list, list]:
        """
        Gibt alle legalen Züge des Springers zurück.
        :param board: 2D np.array mit Figurenobjekten oder None
        :return: Tuple (legal_moves, blocked_by)
        """
        legal_moves = []
        blocked_by = []

        directions = [(3, 1), (3, -1), (-3, 1), (-3, -1), (1, 3), (-1, 3), (1, -3), (-1, -3)]

        self_row, self_col = self.position

        for dx, dy in directions:

            row = self_row + dx
            col = self_col + dy

            if (0 <= row < 8 and 0 <= col < 8):

                target = board[row, col]

                if target is None: #leeres Feld
                    value = self.calculate_value(row, col)
                    legal_moves.append((row, col, False, value, self))

                elif target.color != self.color: #schlagen möglich
                    value = self.value - target.value
                    legal_moves.append((row, col, True, value, self))
                    blocked_by.append((row, col))
                    break

                else:  # eigene Figur blockiert
                    blocked_by.append((row, col))
                    break

        return legal_moves, blocked_by

    def __str__(self):
        return "♞" if self.color == "black" else "♘"

class Pawn(Piece):
    """ Bauer """

    def __init__(self, color: str, position: tuple):
        super().__init__(color, position, notation='P', value=100)

    def get_legal_moves(self, board: np.ndarray) -> tuple[list, list]:
        """
        Gibt alle legalen Züge des Bauers zurück.
        :param board: 2D np.array mit Figurenobjekten oder None
        :return: Tuple (legal_moves, blocked_by)
        """
        legal_moves = []
        blocked_by = []

        row, col = self.position

        if not board[row + 1, col]:
            legal_moves.append((row + 1, col, False, self)) # ziehen möglich
        else:
            blocked_by.append((row + 1, col)) #von Spielfigur geblockt

        for (x, y) in [(row + 1, col +1), (row + 1, col - 1)]:
            if (0 <= x < 8 and 0 <= y < 8):
                if board[x, y]:
                    legal_moves.append((x, y, True, self)) #schlagen möglich
                else:
                    if board[row, y] and board[row, y].notation == self.notation: # en' passant
                        print(" en Passant möglich!")
                        legal_moves.append((x, y, True, self))

        return legal_moves, blocked_by

    def __str__(self):
        return "♟" if self.color == "black" else "♙"
