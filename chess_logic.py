from board import Board
from move import Move
from pieces import Piece

class chess_logik:
    """ Überprüft auf höchster Ebene die Zulässigkeit von Zügen"""

    def __init__(self, bd: Board):
        self.bd = bd
        self.last_moved_piece = None

    @property
    def get_white_pieces(self) -> list:
        """ Gibt eine Liste mit allen existierenden Figuren zurück """
        return self.bd.white_pieces
    
    @property
    def get_black_pieces(self) -> list:
        """ Gibt eine Liste mit allen existierenden Figuren zurück """
        return self.bd.black_pieces
    
    def all_moves(self):
        """ Initialisiert alle legal_moves """

        legal_moves = []

        for piece in self.bd.white_pieces:
            get_moves = piece.get_legal_moves(self.bd)
            legal_moves.extend(get_moves)

        for piece in self.bd.black_pieces:
            get_moves = piece.get_legal_moves(self.bd)
            legal_moves.extend(get_moves)

        return legal_moves

    def last_move(self, last_move: Move):
        """ Speichert die letzt bewegte Figur ab """

        if last_move:
            if self.last_moved_piece.is_pawn:
                if abs(last_move.from_pos[0] - last_move.to_pos[0]) == 2:
                    self.en_passant_posible = True
            
        else:
            raise ValueError('last_move is None or False')

    def all_legal_moves(self, last_move: Optional[Move], curent_turn: str) -> list:
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

        for move in self.all_moves():
            piece = move[3]
            if piece.color != curent_turn:
                continue

            # En-passant prüfen
            if len(move) == 5 and move[4]:
                if not last_move or not self.en_passant(move[2], last_move):
                    continue
            
            # Prüfe ob Zug den eigenen König gefährdet
            if self.would_leave_king_in_check(move, curent_turn):
                continue
            
            # Bauern-Promotion: Wenn Bauer letzte Reihe erreicht
            if piece.is_pawn:
                target_row = move[0]
                if (piece.color == 'white' and target_row == 0) or (piece.color == 'black' and target_row == 7):
                    # Füge 4 Promotion-Optionen hinzu
                    for promo_type in ['queen', 'rook', 'bishop', 'knight']:
                        legal_moves.append((move[0], move[1], move[2], move[3], promo_type))
                    continue
            
            legal_moves.append(move)
                
        # Rochade prüfen
        if curent_turn == 'black':
            if self.can_castle('black', 'queenside'):
                # (king_row, king_col, None, king, 'castling', side)
                legal_moves.append((0, 2, None, self.bd.black_king, 'castling', 'queenside'))
            if self.can_castle('black', 'kingside'):
                legal_moves.append((0, 6, None, self.bd.black_king, 'castling', 'kingside'))
        else:
            if self.can_castle('white', 'queenside'):
                legal_moves.append((7, 2, None, self.bd.white_king, 'castling', 'queenside'))
            if self.can_castle('white', 'kingside'):
                legal_moves.append((7, 6, None, self.bd.white_king, 'castling', 'kingside'))
            
        return legal_moves

    def en_passant(self, target: Piece, last_move: Move) -> bool:
        """ Zu schlagende Figur muss direkt vorher gezogen haben """
        if self.last_moved_piece == target:
            if abs(last_move.from_pos[0] - last_move.to_pos[0]) == 2:
                return True
        return False


    def is_in_check(self, color: str) -> bool:
        """
        Prüft ob der König der angegebenen Farbe im Schach steht.
        
        :param color: 'white' oder 'black'
        :return: True wenn König im Schach steht
        """
        king = self.bd.white_king if color == 'white' else self.bd.black_king
        king_pos = king.position
        
        # Prüfe alle gegnerischen Figuren
        enemy_pieces = self.bd.black_pieces if color == 'white' else self.bd.white_pieces
        
        for piece in enemy_pieces:
            moves = piece.get_legal_moves(self.bd)
            for move in moves:
                target_pos = (move[0], move[1])
                if target_pos == king_pos:
                    return True
        
        return False
    
    def would_leave_king_in_check(self, move: tuple, color: str) -> bool:
        """
        Simuliert einen Zug und prüft ob der eigene König danach im Schach steht.
        
        :param move: Zug-Tupel (row, col, captured, piece, ...)
        :param color: Farbe des ziehenden Spielers
        :return: True wenn Zug den eigenen König gefährdet
        """
        piece = move[3]
        old_pos = piece.position
        new_pos = (move[0], move[1])
        captured = move[2]
        
        # Zug simulieren
        old_row, old_col = old_pos
        new_row, new_col = new_pos
        
        self.bd.squares[old_row, old_col] = None
        temp_piece = self.bd.squares[new_row, new_col]
        self.bd.squares[new_row, new_col] = piece
        piece.position = new_pos
        
        # Geschlagene Figur temporär aus Liste entfernen
        if captured:
            if captured in self.bd.white_pieces:
                self.bd.white_pieces.remove(captured)
            elif captured in self.bd.black_pieces:
                self.bd.black_pieces.remove(captured)
        
        # Prüfe Schach
        in_check = self.is_in_check(color)
        
        # Zug rückgängig machen
        self.bd.squares[old_row, old_col] = piece
        self.bd.squares[new_row, new_col] = temp_piece
        piece.position = old_pos
        
        if captured:
            if captured.color == 'white':
                self.bd.white_pieces.append(captured)
            else:
                self.bd.black_pieces.append(captured)
        
        return in_check

    def is_checkmate(self, color: str) -> bool:
        """
        Prüft ob Schachmatt vorliegt.
        
        :param color: Farbe des Spielers der am Zug ist
        :return: True wenn Schachmatt
        """
        # Keine legalen Züge verfügbar und König im Schach
        if len(self.all_legal_moves(None, color)) == 0:
            return self.is_in_check(color)
        return False
    
    def is_stalemate(self, color: str) -> bool:
        """
        Prüft ob Patt vorliegt.
        
        :param color: Farbe des Spielers der am Zug ist
        :return: True wenn Patt
        """
        # Keine legalen Züge verfügbar aber König NICHT im Schach
        if len(self.all_legal_moves(None, color)) == 0:
            return not self.is_in_check(color)
        return False

    def can_castle(self, color: str, side: str) -> bool:
        """
        Prüft ob Rochade möglich ist.
        
        :param color: 'white' oder 'black'
        :param side: 'kingside' oder 'queenside'
        :return: True wenn Rochade möglich ist
        """
        if color == 'black':
            king = self.bd.black_king
            king_row = 0
            
            if side == 'queenside':
                rook_col = 0
                empty_cols = [1, 2, 3]
            else:  # kingside
                rook_col = 7
                empty_cols = [5, 6]
                
        else:  # white
            king = self.bd.white_king
            king_row = 7
            
            if side == 'queenside':
                rook_col = 0
                empty_cols = [1, 2, 3]
            else:  # kingside
                rook_col = 7
                empty_cols = [5, 6]
        
        # König darf nicht bewegt worden sein
        if king.moved:
            return False
        
        # Turm muss existieren und darf nicht bewegt worden sein
        rook = self.bd.squares[king_row, rook_col]
        if rook is None or not hasattr(rook, 'moved') or rook.moved:
            return False
        
        # Felder zwischen König und Turm müssen leer sein
        for col in empty_cols:
            if self.bd.squares[king_row, col] is not None:
                return False
        
        # König darf nicht im Schach stehen
        if self.is_in_check(color):
            return False
        
        # König darf nicht durch Schach ziehen (nur mittleres Feld prüfen)
        king_col = 4
        if side == 'queenside':
            check_cols = [3, 2]  # König zieht über diese Felder
        else:
            check_cols = [5, 6]
        
        for col in check_cols:
            # Simuliere König auf diesem Feld
            original = self.bd.squares[king_row, col]
            self.bd.squares[king_row, king_col] = None
            self.bd.squares[king_row, col] = king
            
            in_check = self.is_in_check(color)
            
            # Zurücksetzen
            self.bd.squares[king_row, king_col] = king
            self.bd.squares[king_row, col] = original
            
            if in_check:
                return False
        
        return True

    def delete_piece(self, piece):
        """Entfernt eine Figur aus dem Spiel."""
        self.bd.remove_piece(piece)







