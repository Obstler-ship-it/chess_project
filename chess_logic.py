from board import Board
from move import Move
from pieces import Piece
from typing import Optional

class chess_logik:
    """ Überprüft auf höchster Ebene die Zulässigkeit von Zügen"""

    def __init__(self, bd: Board):
        self.bd = bd
        self._all_moves = []

    @property
    def get_white_pieces(self) -> list:
        """ Gibt eine Liste mit allen existierenden Figuren zurück """
        return self.bd.white_pieces
    
    @property
    def all_moves(self) -> list:
        """ Gibt eine Liste mit allen existierenden Zügen zurück """
        return self._all_moves
    
    @property
    def get_black_pieces(self) -> list:
        """ Gibt eine Liste mit allen existierenden Figuren zurück """
        return self.bd.black_pieces
    
    def calculate_all_moves(self) -> list:
        """ Initialisiert alle legal_moves """

        self._all_moves = []

        for piece in self.bd.white_pieces:
            get_moves = piece.get_legal_moves(self.bd)
            self._all_moves.extend(get_moves)
        for piece in self.bd.black_pieces:
            get_moves = piece.get_legal_moves(self.bd)
            self._all_moves.extend(get_moves)

        return self._all_moves

    def all_legal_moves(self, last_move: Move, curent_turn: str) -> list:
        """ Gibt alle legalen Züge zurück.
        
        Überprüft:
            - Ob Züge den König ins Schach setzen würden
            - Ob Rochade möglich ist
            - Ob Bauern-Promotion nötig ist
            - En passant basierend auf last_move
            
        :param: last_move, Move-Objekt des letzten Zugs (für En passant)
        :param: curent_turn, Farbe des aktuellen Spielers
        :return: Liste aller legalen Züge
        """

        legal_moves = []
        self.calculate_all_moves()

        if self.bd.white_king.color == curent_turn:
            king = self.bd.white_king
        else:
            king = self.bd.black_king

        if king is None:
            raise ValueError('King not found!')

        for move in self.all_moves:
            piece = move[3]
            target = move[2]

            if piece.color != curent_turn:
                continue
                
            # En-passant prüfen
            if len(move) == 5 and move[4]:
                if not self.en_passant(target, last_move):
                    continue

            # Prüfe ob Zug den eigenen König gefährdet
            if self.would_leave_king_in_check(move, curent_turn, king):
                continue
            
            legal_moves.append(move)
                
        # Rochade prüfen
        legal_moves.extend(self.castle(king))
    
        # Schachmatt/Stalemate prüfen
        if legal_moves == []:
            return [self.check_or_stalemate(king, self.all_moves)]

        return legal_moves

    def en_passant(self, target: Piece, last_move: Move) -> bool:
        """ Zu schlagende Figur muss direkt vorher gezogen haben """
        if last_move.piece == target:
            if abs(last_move.from_pos[0] - last_move.to_pos[0]) == 2:
                return True
        return False

    def is_in_check(self, king_pos: tuple, all_moves) -> bool:
        """
        Prüft ob der König im Schach steht.
        
        :param king_pos: Position des Königs
        :param all_moves: Liste aller möglichen Züge
        :return: True wenn König im Schach steht
        """
        
        for move in all_moves:
            target_pos = (move[0], move[1])
            if target_pos == king_pos:
                return True
        
        return False
    
    def would_leave_king_in_check(self, move: tuple, color: str, king: Piece) -> bool:
        """
        Simuliert einen Zug und prüft ob der eigene König danach im Schach steht.
        
        :param move: Zug-Tupel (row, col, captured, piece, ...)
        :param color: Farbe des ziehenden Spielers
        :return: True wenn Zug den eigenen König gefährdet
        """

        Board_copy = self.bd.deep_copy()
        legal_moves = []
        piece = move[3]
        target = move[2]

        from_row, from_col = piece.position
        to_row, to_col = move[0:2]

        # Finde die entsprechende Figur im kopierten Board
        piece_copy = Board_copy.squares[from_row, from_col]
        target_copy = Board_copy.squares[to_row, to_col] if target else None

         # Move-Objekt erstellen mit kopierten Figuren
        move_obj = Move(
            from_pos=(from_row, from_col),
            to_pos=(to_row, to_col),
            piece=piece_copy,
            captured=target_copy,
            promotion=False
        )
        
        # Zug im Board ausführen
        Board_copy.make_move(move_obj)
        
        for piece in Board_copy.white_pieces:
            get_moves = piece.get_legal_moves(Board_copy)
            legal_moves.extend(get_moves)

        for piece in Board_copy.black_pieces:
            get_moves = piece.get_legal_moves(Board_copy)
            legal_moves.extend(get_moves)

        king_copy = Board_copy.white_king if color == 'white' else Board_copy.black_king

        if self.is_in_check(king_copy.position, legal_moves):
                 return True
        return False

    def check_or_stalemate(self, king: Piece, all_moves) -> str:
        """
        Prüft ob Schachmatt vorliegt.
        
        :param color: Farbe des Spielers der am Zug ist
        :return: True wenn Schachmatt
        """
        # Keine legalen Züge verfügbar und König im Schach
        king_pos = king.position
        if self.is_in_check(king_pos, all_moves):
            return f'checkmate'
        else:
            return f'stalemate'

    def castle(self, king: Piece) -> list:
        """
        Prüft ob Rochade möglich ist.
        
        :param color: 'white' oder 'black'
        :param side: 'kingside' oder 'queenside'
        :return: True wenn Rochade möglich ist
        """

        if king.moved:
            return []
        
        moves = []
        king_row = king.position[0]
        rook1 = self.bd.squares[king_row, 0]
        rook2 = self.bd.squares[king_row, 7]

        if hasattr(rook1, 'moved') and rook1.moved == False:

            for col in [1, 2, 3]:
                king_pos = (king_row, col)
                if self.bd.squares[king_pos] is not None:
                    break
                if self.is_in_check(king_pos, self.all_moves):
                    break
                king_pos = (king_row, 0)
                if self.is_in_check(king_pos, self.all_moves):
                    break
                moves.append((king_row, 0, None, king,'queenside', rook1))

        if hasattr(rook2, 'moved') and rook2.moved == False:

            for col in [5, 6]:
                king_pos = (king_row, col)
                if self.bd.squares[king_pos] is not None:
                    break
                if self.is_in_check(king_pos, self.all_moves):
                    break
                king_pos = (king_row, 7)
                if self.is_in_check(king_pos, self.all_moves):
                    break
                moves.append((king_row, 7, None, king,'kingside', rook2))
        return moves
        







