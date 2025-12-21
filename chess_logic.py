from board import Board
from move import Move
from pieces import Piece
from typing import Optional

class chess_logik:
    """ Überprüft auf höchster Ebene die Zulässigkeit von Zügen"""

    def __init__(self, bd: Board):
        self.bd = bd
        self.legal_moves = []
        self.blocked_by = []

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
            self.legal_moves.extend(legal_moves)
            self.blocked_by.extend(blocked_by)

        for piece in self.bd.black_pieces:
            legal_moves, blocked_by = piece.get_legal_moves(self.bd)
            self.legal_moves.extend(legal_moves)
            self.blocked_by.extend(blocked_by)

        return self.legal_moves

    def last_move(self, last_move: Move):
        """Gibt alle legalen Züge zurück unter Berücksichtigung des letzten Zugs."""

        if last_move is None:
            raise ValueError("last_move darf nicht None sein - En-passant benötigt vorherigen Zug!")

        for move in self.legal_moves:
            if last_move.to_pos == move[0:2]:
                piece = move[3]
                self.remove_legal_moves(piece)
                self.remove_blocked_by(piece)
                legal_moves, blocked_by = piece.get_legal_moves(self.bd)
                self.legal_moves.extend(legal_moves)
                self.blocked_by.extend(blocked_by)
            
        for pos in self.blocked_by:
            if pos[0:2] == last_move.from_pos or pos[0:2] == last_move.to_pos:
                piece = pos[2]
                legal_moves, blocked_by = piece.get_legal_moves(self.bd)
                self.legal_moves.extend(legal_moves)
                self.blocked_by.extend(blocked_by)

        return self.all_legal_moves()
    
    def remove_legal_moves(self, piece: Piece):
        """ Entfernt alle Züge einer bestimmten Figur aus legal_moves. """
        # List comprehension: Erstellt neue Liste ohne Züge dieser Figur
        self.legal_moves = [move for move in self.legal_moves if move[3] != piece]

    def remove_blocked_by(self, piece: Piece):
        """ Entfernt alle Züge einer bestimmten Figur aus blocked_by. """
        # List comprehension: Erstellt neue Liste ohne Züge dieser Figur
        self.blocked_by = [move for move in self.blocked_by if move[2] != piece]


    def all_legal_moves(self, last_move: Optional[Move] = None) -> list:
        """ Gibt alle legalen Züge für zurück.
        
        Überprüft:
            - Ob Züge den König ins Schach setzen würden
            - Ob Rochade möglich ist
            - Ob Bauern-Promotion nötig ist
            - En passant basierend auf last_move
            
        :param: last_move, Move-Objekt des letzten Zugs (für En passant)
        :return: Liste aller legalen Züge
        """
        # TODO: Implementiere die Logik
        return self.legal_moves  # Vorerst gibt es die aktuellen legal_moves zurück
        """
        return []


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



        



