from board import Board
from move import Move
from pieces import Piece
from typing import Optional

class chess_logic:
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
    
    def calculate_all_moves(self) -> list[Move]:
        """ Initialisiert alle legal_moves """

        self._all_moves = []

        for piece in self.bd.white_pieces:
            get_moves = piece.get_legal_moves(self.bd)
            self._all_moves.extend(get_moves)
        for piece in self.bd.black_pieces:
            get_moves = piece.get_legal_moves(self.bd)
            self._all_moves.extend(get_moves)

        return self._all_moves

    def all_legal_moves(self, last_move: Move, curent_turn: str) -> list[Move] or str:
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
            piece = move.piece

            if piece.color != curent_turn:
                continue
                
            # En-passant prüfen
            if move.en_passant:
                if not self.en_passant(move.captured, last_move):
                    continue

            # Prüfe ob Zug den eigenen König gefährdet
            if self.would_leave_king_in_check(move, king):
                continue
            
            legal_moves.append(move)
                
        # Rochade prüfen
        legal_moves.extend(self.castle(king))
    
        # Schachmatt/Stalemate prüfen
        if not legal_moves:
            return str(self.check_or_stalemate(king, self.all_moves))

        return legal_moves

    def en_passant(self, captured: Piece, last_move: Move) -> bool:
        """ Zu schlagende Figur muss direkt vorher gezogen haben """

        if last_move.piece == captured:
            return True
        return False

    def is_in_check(self, king: Piece, all_moves: list[Move]) -> bool:
        """
        Prüft ob der König im Schach steht.
        
        :param king_pos: Position des Königs
        :param all_moves: Liste aller möglichen Züge
        :return: True wenn König im Schach steht
        """

        for move in all_moves:
            if move.captured == king:
                return True
        
        return False
    
    def would_leave_king_in_check(self, move: Move, king: Piece) -> bool:
        """
        Simuliert einen Zug und prüft ob der eigene König danach im Schach steht.
        
        :param move: Zug-Tupel (row, col, captured, piece, ...)
        :param color: Farbe des ziehenden Spielers
        :return: True wenn Zug den eigenen König gefährdet
        """

        Board_copy = self.bd.deep_copy()
        legal_moves = []

        from_row, from_col = move.from_pos

        # Finde die entsprechende Figur im kopierten Board
        piece_copy = Board_copy.squares[from_row, from_col]
        if move.captured is not None:
            target_pos = move.captured.position
            target_copy = Board_copy.squares[target_pos]
        else:
            target_copy = None

        king_copy = Board_copy.white_king if king.color == 'white' else Board_copy.black_king

         # Move-Objekt erstellen mit kopierten Figuren
        move_obj = Move(
            from_pos=(from_row, from_col),
            to_pos=move.to_pos,
            piece=piece_copy,
            captured=target_copy
        )
        
        # Zug im Board ausführen
        Board_copy.make_move(move_obj)

        if king.color == 'white':
            for piece in Board_copy.black_pieces:
                get_moves = piece.get_legal_moves(Board_copy)
                legal_moves.extend(get_moves)
        else:
            for piece in Board_copy.white_pieces:
                get_moves = piece.get_legal_moves(Board_copy)
                legal_moves.extend(get_moves)

        if self.is_in_check(king_copy, legal_moves):
            return True
        return False

    def check_or_stalemate(self, king: Piece, all_moves) -> str:
        """
        Prüft ob Schachmatt vorliegt.
        
        :param color: Farbe des Spielers der am Zug ist
        :return: True wenn Schachmatt
        """
        # Keine legalen Züge verfügbar und König im Schach
        if self.is_in_check(king, all_moves):
            return 'checkmate'
        else:
            return 'stalemate'

    def castle(self, king: Piece) -> list:
        """
        Prüft ob Rochade möglich ist.
        
        :param color: 'white' oder 'black'
        :param side: 'kingside' oder 'queenside'
        :return: True wenn Rochade möglich ist
        """

        if king.moved:
            return []
        
        if self.is_in_check(king, self.all_moves):
            return []
        
        moves = []
        king_row = king.position[0]
        rook1 = self.bd.squares[king_row, 0]  # Queenside
        rook2 = self.bd.squares[king_row, 7]  # Kingside

        # Queenside (lange Rochade): König nach c (col=2), Turm nach d (col=3)
        if hasattr(rook1, 'moved') and rook1.moved is False:
            can_castle = True
            
            # Prüfe ob Felder zwischen König und Turm frei sind (cols 1, 2, 3)
            for col in [1, 2, 3]:
                if self.bd.squares[king_row, col] is not None:
                    can_castle = False
                    break
            
            # Prüfe ob König durch Schach ziehen würde (cols 2, 3)
            if can_castle:
                for col in [2, 3]:
                    king_pos = (king_row, col)
                    move = Move(
                        from_pos=king.position,
                        to_pos=king_pos,
                        piece=king
                    )
                    if self.would_leave_king_in_check(move, king):
                        can_castle = False
                        break
            
            if can_castle:
                moves.append(Move(king.position, (king_row, 2), king, None, castelling=rook1))

        # Kingside (kurze Rochade): König nach g (col=6), Turm nach f (col=5)
        if hasattr(rook2, 'moved') and rook2.moved is False:
            can_castle = True
            
            # Prüfe ob Felder zwischen König und Turm frei sind (cols 5, 6)
            for col in [5, 6]:
                if self.bd.squares[king_row, col] is not None:
                    can_castle = False
                    break
            
            # Prüfe ob König durch Schach ziehen würde (cols 5, 6)
            if can_castle:
                for col in [5, 6]:
                    king_pos = (king_row, col)
                    move = Move(
                        from_pos=king.position,
                        to_pos=king_pos,
                        piece=king
                    )
                    if self.would_leave_king_in_check(move, king):
                        can_castle = False
                        break
            
            if can_castle:
                moves.append(Move(king.position, (king_row, 6), king, None, castelling=rook2))
        
        return moves
        







