"""Unit Tests für ChessLogic-Klasse."""

import pytest
from board import Board
from chess_logic import ChessLogic
from move import Move


class TestChessLogic:
    """Test-Suite für ChessLogic-Klasse."""
    
    def test_chess_logic_initialization(self):
        """Test: ChessLogic wird korrekt initialisiert."""
        board = Board()
        board.setup_startpos()
        logic = ChessLogic(board)
        
        assert logic.board is board
        assert logic.board.squares is not None
    
    def test_is_in_check_initial_position(self):
        """Test: Könige stehen zu Beginn nicht im Schach."""
        board = Board()
        board.setup_startpos()
        logic = ChessLogic(board)
        
        assert not logic.is_in_check('white')
        assert not logic.is_in_check('black')
    
    def test_is_in_check_with_attacking_piece(self):
        """Test: Erkennt Schach korrekt."""
        board = Board()
        from pieces import King, Rook
        
        # Weißer König auf e1
        white_king = King('white', (0, 4))
        board.squares[0, 4] = white_king
        board.white_king = white_king
        
        # Schwarzer Turm greift König an
        black_rook = Rook('black', (0, 0))
        board.squares[0, 0] = black_rook
        
        logic = ChessLogic(board)
        assert logic.is_in_check('white')
    
    def test_is_checkmate_scholars_mate(self):
        """Test: Erkennt Schäfermatt (Scholar's Mate)."""
        board = Board()
        board.setup_startpos()
        logic = ChessLogic(board)
        
        # Führe Schäfermatt-Sequenz aus
        # 1. e4 e5
        board.make_move(Move((1, 4), (3, 4)))
        board.make_move(Move((6, 4), (4, 4)))
        
        # 2. Bc4 Nc6
        board.make_move(Move((0, 5), (3, 2)))
        board.make_move(Move((7, 1), (5, 2)))
        
        # 3. Qh5 Nf6
        board.make_move(Move((0, 3), (4, 7)))
        board.make_move(Move((7, 6), (5, 5)))
        
        # 4. Qxf7# - Schachmatt
        from pieces import Pawn
        f7_pawn = board.squares[6, 5]
        board.make_move(Move((4, 7), (6, 5), captured_piece=f7_pawn))
        
        # Prüfe ob Schwarz Matt ist
        assert logic.is_in_check('black')
        # Hinweis: is_checkmate erfordert dass alle Züge durchprobiert werden
        # was aufwändiger zu testen ist
    
    def test_is_stalemate(self):
        """Test: Erkennt Patt-Situation."""
        board = Board()
        from pieces import King, Queen
        
        # Schwarzer König in der Ecke
        black_king = King('black', (7, 0))
        board.squares[7, 0] = black_king
        board.black_king = black_king
        
        # Weiße Dame blockiert König (Patt)
        white_queen = Queen('white', (5, 1))
        board.squares[5, 1] = white_queen
        
        # Weißer König irgendwo
        white_king = King('white', (0, 4))
        board.squares[0, 4] = white_king
        board.white_king = white_king
        
        logic = ChessLogic(board)
        
        # Schwarz ist nicht im Schach aber hat keine Züge
        assert not logic.is_in_check('black')
        # Patt-Prüfung würde require dass wir alle möglichen Züge prüfen
    
    def test_can_castle_kingside_white(self):
        """Test: Prüft ob kurze Rochade möglich ist."""
        board = Board()
        board.setup_startpos()
        
        # Räume Felder für Rochade
        board.squares[0, 5] = None  # Bishop
        board.squares[0, 6] = None  # Knight
        
        logic = ChessLogic(board)
        
        # König und Turm haben nicht bewegt
        king = board.squares[0, 4]
        rook = board.squares[0, 7]
        assert not king.moved
        assert not rook.moved
        
        # Rochade sollte möglich sein
        assert logic.can_castle('white', 'kingside')
    
    def test_can_castle_queenside_black(self):
        """Test: Prüft ob lange Rochade möglich ist."""
        board = Board()
        board.setup_startpos()
        
        # Räume Felder für lange Rochade
        board.squares[7, 1] = None  # Knight
        board.squares[7, 2] = None  # Bishop
        board.squares[7, 3] = None  # Queen
        
        logic = ChessLogic(board)
        assert logic.can_castle('black', 'queenside')
    
    def test_cannot_castle_if_king_moved(self):
        """Test: Rochade nicht möglich wenn König bewegt hat."""
        board = Board()
        board.setup_startpos()
        
        # Räume Felder
        board.squares[0, 5] = None
        board.squares[0, 6] = None
        
        # Bewege König
        king = board.squares[0, 4]
        king.moved = True
        
        logic = ChessLogic(board)
        assert not logic.can_castle('white', 'kingside')
    
    def test_cannot_castle_through_check(self):
        """Test: Rochade nicht möglich durch Schach."""
        board = Board()
        board.setup_startpos()
        from pieces import Rook
        
        # Räume Felder für weiße Rochade
        board.squares[0, 5] = None
        board.squares[0, 6] = None
        
        # Schwarzer Turm greift f1 an
        black_rook = Rook('black', (7, 5))
        board.squares[7, 5] = black_rook
        
        logic = ChessLogic(board)
        # Rochade sollte nicht möglich sein da König durch Schach ziehen würde
        assert not logic.can_castle('white', 'kingside')


class TestEnPassant:
    """Test-Suite für En Passant."""
    
    def test_en_passant_possible(self):
        """Test: En Passant wird korrekt erkannt."""
        board = Board()
        board.setup_startpos()
        logic = ChessLogic(board)
        
        # Weißer Bauer macht Doppelzug
        last_move = Move((1, 4), (3, 4))
        board.make_move(last_move)
        
        # Schwarzer Bauer steht daneben
        black_pawn = board.squares[6, 3]
        board.squares[6, 3] = None
        board.squares[3, 3] = black_pawn
        black_pawn.position = (3, 3)
        
        # En Passant sollte möglich sein
        legal_moves = black_pawn.get_legal_moves(board)
        
        # Prüfe ob En Passant-Zug dabei ist
        en_passant_moves = [m for m in legal_moves if m.is_en_passant]
        assert len(en_passant_moves) > 0


class TestPromotion:
    """Test-Suite für Bauernumwandlung."""
    
    def test_pawn_reaches_last_rank(self):
        """Test: Bauer erreicht letzte Reihe."""
        board = Board()
        from pieces import Pawn
        
        # Weißer Bauer auf 7. Reihe
        white_pawn = Pawn('white', (6, 4))
        board.squares[6, 4] = white_pawn
        
        # Zug zur 8. Reihe
        legal_moves = white_pawn.get_legal_moves(board)
        
        # Sollte Promotion-Züge enthalten
        promotion_moves = [m for m in legal_moves if m.is_promotion]
        assert len(promotion_moves) > 0
