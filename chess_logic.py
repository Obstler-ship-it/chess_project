from board import Board
from move import Move
from pieces import Piece
from typing import Optional, Union

class ChessLogic:
    """Überprüft auf höchster Ebene die Zulässigkeit von Zügen."""

    def __init__(self, bd: Board):
        self.bd = bd
        self._all_moves = []

    @property
    def white_pieces(self) -> list[Piece]:
        """Gibt eine Liste mit allen existierenden weißen Figuren zurück."""
        return self.bd.white_pieces
    
    @property
    def all_moves(self) -> list[Move]:
        """Gibt eine Liste mit allen existierenden Zügen zurück."""
        return self._all_moves
    
    @property
    def black_pieces(self) -> list[Piece]:
        """Gibt eine Liste mit allen existierenden schwarzen Figuren zurück."""
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

    def all_legal_moves(
        self, last_move: Move, current_turn: str
    ) -> Union[list[Move], str]:
        """Gibt alle legalen Züge zurück.
        
        Überprüft:
            - Ob Züge den König ins Schach setzen würden
            - Ob Rochade möglich ist
            - Ob Bauern-Promotion nötig ist
            - En passant basierend auf last_move
            
        Args:
            last_move: Move-Objekt des letzten Zugs (für En passant)
            current_turn: Farbe des aktuellen Spielers ('white' oder 'black')
            
        Returns:
            Liste aller legalen Züge oder 'checkmate'/'stalemate'
        """

        legal_moves = []
        self.calculate_all_moves()

        king = self._get_king(current_turn)
        if king is None:
            raise ValueError('King not found!')

        for move in self.all_moves:
            piece = move.piece

            if piece.color != current_turn:
                continue
                
            # En-passant prüfen
            if move.en_passant and move.captured:
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

    def _get_king(self, color: str) -> Optional[Piece]:
        """Gibt den König der angegebenen Farbe zurück.
        
        Args:
            color: 'white' oder 'black'
            
        Returns:
            King-Objekt der entsprechenden Farbe oder None
        """
        return (
            self.bd.white_king if color == 'white'
            else self.bd.black_king
        )

    def en_passant(self, captured: Piece, last_move: Move) -> bool:
        """Zu schlagende Figur muss direkt vorher gezogen haben.
        
        Args:
            captured: Die zu schlagende Figur
            last_move: Der letzte ausgeführte Zug
            
        Returns:
            True wenn En passant gültig ist
        """
        return last_move.piece == captured

    def is_in_check(self, king: Piece, all_moves: list[Move]) -> bool:
        """Prüft ob der König im Schach steht.
        
        Args:
            king: König-Objekt
            all_moves: Liste aller möglichen gegnerischen Züge
            
        Returns:
            True wenn König im Schach steht
        """

        for move in all_moves:
            if move.captured == king:
                return True
        
        return False
    
    def would_leave_king_in_check(self, move: Move, king: Piece) -> bool:
        """Simuliert einen Zug und prüft ob der eigene König im Schach steht.
        
        Args:
            move: Der zu prüfende Zug
            king: König-Objekt des ziehenden Spielers
            
        Returns:
            True wenn Zug den eigenen König gefährdet
        """

        board_copy = self.bd.deep_copy()
        legal_moves = []

        from_row, from_col = move.from_pos

        # Finde die entsprechende Figur im kopierten Board
        piece_copy = board_copy.squares[from_row, from_col]
        target_copy = None
        if move.captured is not None:
            target_pos = move.captured.position
            target_copy = board_copy.squares[target_pos]

        king_copy = (
            board_copy.white_king if king.color == 'white'
            else board_copy.black_king
        )

        # Move-Objekt erstellen mit kopierten Figuren
        move_obj = Move(
            from_pos=(from_row, from_col),
            to_pos=move.to_pos,
            piece=piece_copy,
            captured=target_copy
        )
        
        # Zug im Board ausführen
        board_copy.make_move(move_obj)

        # Berechne gegnerische Züge
        opponent_pieces = (
            board_copy.black_pieces if king.color == 'white'
            else board_copy.white_pieces
        )
        for piece in opponent_pieces:
            legal_moves.extend(piece.get_legal_moves(board_copy))

        if king_copy and self.is_in_check(king_copy, legal_moves):
            return True
        return False

    def check_or_stalemate(
        self, king: Piece, all_moves: list[Move]
    ) -> str:
        """Prüft ob Schachmatt oder Patt vorliegt.
        
        Args:
            king: König-Objekt des Spielers am Zug
            all_moves: Alle möglichen gegnerischen Züge
            
        Returns:
            'checkmate' oder 'stalemate'
        """
        # Keine legalen Züge verfügbar und König im Schach
        return 'checkmate' if self.is_in_check(king, all_moves) else 'stalemate'

    def castle(self, king: Piece) -> list[Move]:
        """Prüft ob Rochade möglich ist.
        
        Args:
            king: König-Objekt
            
        Returns:
            Liste mit möglichen Rochade-Zügen (0-2 Züge)
        """

        if not hasattr(king, 'moved') or king.moved:
            return []
        
        if self.is_in_check(king, self.all_moves):
            return []
        
        moves = []
        king_row = king.position[0]
        rook1 = self.bd.squares[king_row, 0]  # Queenside
        rook2 = self.bd.squares[king_row, 7]  # Kingside

        # Queenside (lange Rochade): König nach c (col=2), Turm nach d (col=3)
        if hasattr(rook1, 'moved') and not rook1.moved:
            can_castle = self._check_castling_path(
                king, king_row, [1, 2, 3], [2, 3]
            )
            if can_castle:
                moves.append(
                    Move(
                        king.position, (king_row, 2), king,
                        None, castelling=rook1
                    )
                )

        # Kingside (kurze Rochade): König nach g (col=6), Turm nach f (col=5)
        if hasattr(rook2, 'moved') and not rook2.moved:
            can_castle = self._check_castling_path(
                king, king_row, [5, 6], [5, 6]
            )
            if can_castle:
                moves.append(
                    Move(
                        king.position, (king_row, 6), king,
                        None, castelling=rook2
                    )
                )
        
        return moves

    def _check_castling_path(
        self, king: Piece, king_row: int,
        empty_cols: list[int], check_cols: list[int]
    ) -> bool:
        """Prüft ob der Weg für Rochade frei ist.
        
        Args:
            king: König-Objekt
            king_row: Reihe des Königs
            empty_cols: Spalten die leer sein müssen
            check_cols: Spalten durch die der König nicht im Schach ziehen darf
            
        Returns:
            True wenn Rochade möglich ist
        """
        # Prüfe ob Felder frei sind
        for col in empty_cols:
            if self.bd.squares[king_row, col] is not None:
                return False
        
        # Prüfe ob König durch Schach ziehen würde
        for col in check_cols:
            move = Move(
                from_pos=king.position,
                to_pos=(king_row, col),
                piece=king
            )
            if self.would_leave_king_in_check(move, king):
                return False
        
        return True
        







