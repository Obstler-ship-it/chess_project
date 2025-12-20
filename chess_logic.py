from board import Board
from move import Move
from typing import Optional

class chess_logik:
    """ Überprüft auf höchster Ebene die Zulässigkeit von Zügen"""

    def __init__(self, bd: Board):
        self.bd = bd
        self.white_legal_moves = []
        self.black_legal_moves = []
        self.white_blocked_by = []
        self.black_blocked_by = []

    @property
    def get_white_pieces(self) -> list:
        """ Gibt eine Liste mit allen existierenden Figuren zurück """
        return self.bd.white_pieces
    
    @property
    def get_black_pieces(self) -> list:
        """ Gibt eine Liste mit allen existierenden Figuren zurück """
        return self.bd.black_pieces
    
    def starting_moves(self):
        """ Initialisiert alle legal_moves und blocked_by """

        for piece in self.bd.white_pieces:
            legal_moves, blocked_by = piece.get_legal_moves(self.bd)
            self.white_legal_moves.extend(legal_moves)
            self.white_blocked_by.extend(blocked_by)

        for piece in self.bd.black_pieces:
            legal_moves, blocked_by = piece.get_legal_moves(self.bd)
            self.black_legal_moves.extend(legal_moves)
            self.black_blocked_by.extend(blocked_by)

        return self.white_legal_moves

    def last_move_white(self, last_move: Optional[Move] = None):
        """Gibt alle legalen Züge für Weiß zurück unter Berücksichtigung des letzten Zugs."""
        return self.all_legal_moves('white', last_move)

    def last_move_black(self, last_move: Optional[Move] = None):
        """Gibt alle legalen Züge für Schwarz zurück unter Berücksichtigung des letzten Zugs."""
        return self.all_legal_moves('black', last_move)

    def all_legal_moves(self, color: str, last_move: Optional[Move] = None) -> list:
        """ Gibt alle legalen Züge für eine Farbe zurück.
        
        Überprüft:
            - Ob Züge den König ins Schach setzen würden
            - Ob Rochade möglich ist
            - Ob Bauern-Promotion nötig ist
            - En passant basierend auf last_move
            
        :param: color, 'white' oder 'black'
        :param: last_move, Move-Objekt des letzten Zugs (für En passant)
        :return: Liste aller legalen Züge
        """
        return


    def ispawn_promotion(self):
        """ Gibt"""
        pass

    def is_checkmate(self):
        """ Wird durch all_legal_moves aufgerufen testet die beiden Fälle"""
        pass

    def rochade(self):
        pass

    def zugzwang(self):
        """ Gibt bei Checkmate alle legalen Züge zurück
            oder ruft stealmate oder checkmate auf
        """
        pass

    def delete_piece(self, piece):
        self.bd.remove_piece(piece)

    def stealmate(self):
        return f'stealmate'

    def checkmate(self):
        return f'checkmate'



        



