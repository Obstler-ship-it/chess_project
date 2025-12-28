"""Unit Tests für Piece-Klassen."""

import pytest
import numpy as np
from chess_project.board import Board
from chess_project.pieces import King, Queen, Rook, Bishop, Knight, Pawn
from chess_project.move import Move


class TestPawn:
    """Test-Suite für Pawn-Klasse."""
    
    def test_pawn_initial_position(self):
        """Test: Bauer wird korrekt initialisiert."""
        pawn = Pawn('white', (1, 4))
        assert pawn.color == 'white'
        assert pawn.position == (1, 4)
        assert pawn.notation == 'P'
        assert pawn.pawn
    
    def test_pawn_image_path(self):
        """Test: Bildpfad wird korrekt generiert."""
        white_pawn = Pawn('white', (1, 0))
        black_pawn = Pawn('black', (6, 0))
        assert white_pawn.get_image_path().endswith('white_P.png')
        assert black_pawn.get_image_path().endswith('black_P.png')
    
    def test_pawn_single_move_forward(self):
        """Test: Bauer kann ein Feld vorwärts ziehen."""
        board = Board()
        board.setup_startpos()
        pawn = board.squares[1, 4]  # e2
        
        legal_moves = pawn.get_legal_moves(board)
        
        # Sollte e3 und e4 enthalten
        move_targets = [move.to_pos for move in legal_moves]
        assert (2, 4) in move_targets  # e3
        assert (3, 4) in move_targets  # e4
    
    def test_pawn_double_move_first_time(self):
        """Test: Bauer kann beim ersten Zug zwei Felder vorwärts."""
        board = Board()
        board.setup_startpos()
        pawn = board.squares[1, 4]
        
        legal_moves = pawn.get_legal_moves(board)
        move_targets = [move.to_pos for move in legal_moves]
        
        assert (3, 4) in move_targets  # Doppelzug möglich


class TestKnight:
    """Test-Suite für Knight-Klasse."""
    
    def test_knight_initial_position(self):
        """Test: Springer wird korrekt initialisiert."""
        knight = Knight('white', (0, 1))
        assert knight.color == 'white'
        assert knight.notation == 'N'
        assert not knight.pawn
    
    def test_knight_moves_from_start(self):
        """Test: Springer kann L-förmig ziehen."""
        board = Board()
        board.setup_startpos()
        knight = board.squares[0, 1]  # b1
        
        legal_moves = knight.get_legal_moves(board)
        move_targets = [move.to_pos for move in legal_moves]
        
        # Springer auf b1 kann nach a3 und c3
        assert (2, 0) in move_targets  # a3
        assert (2, 2) in move_targets  # c3


class TestBishop:
    """Test-Suite für Bishop-Klasse."""
    
    def test_bishop_initialization(self):
        """Test: Läufer wird korrekt initialisiert."""
        bishop = Bishop('black', (7, 2))
        assert bishop.color == 'black'
        assert bishop.notation == 'B'
    
    def test_bishop_diagonal_moves(self):
        """Test: Läufer bewegt sich diagonal."""
        board = Board()
        bishop = Bishop('white', (3, 3))  # d4
        board.squares[3, 3] = bishop
        
        legal_moves = bishop.get_legal_moves(board)
        move_targets = [move.to_pos for move in legal_moves]
        
        # Diagonal nach oben-rechts
        assert (4, 4) in move_targets
        assert (5, 5) in move_targets
        
        # Diagonal nach unten-links
        assert (2, 2) in move_targets
        assert (1, 1) in move_targets


class TestRook:
    """Test-Suite für Rook-Klasse."""
    
    def test_rook_initialization(self):
        """Test: Turm wird korrekt initialisiert."""
        rook = Rook('white', (0, 0))
        assert rook.color == 'white'
        assert rook.notation == 'R'
        assert not rook.moved
    
    def test_rook_horizontal_vertical_moves(self):
        """Test: Turm bewegt sich horizontal und vertikal."""
        board = Board()
        rook = Rook('white', (3, 3))  # d4
        board.squares[3, 3] = rook
        
        legal_moves = rook.get_legal_moves(board)
        move_targets = [move.to_pos for move in legal_moves]
        
        # Vertikal nach oben
        assert (4, 3) in move_targets
        assert (7, 3) in move_targets
        
        # Horizontal nach rechts
        assert (3, 4) in move_targets
        assert (3, 7) in move_targets


class TestQueen:
    """Test-Suite für Queen-Klasse."""
    
    def test_queen_initialization(self):
        """Test: Dame wird korrekt initialisiert."""
        queen = Queen('black', (7, 3))
        assert queen.color == 'black'
        assert queen.notation == 'Q'
    
    def test_queen_all_directions(self):
        """Test: Dame bewegt sich in alle Richtungen."""
        board = Board()
        queen = Queen('white', (3, 3))  # d4
        board.squares[3, 3] = queen
        
        legal_moves = queen.get_legal_moves(board)
        move_targets = [move.to_pos for move in legal_moves]
        
        # Vertikal
        assert (4, 3) in move_targets
        assert (2, 3) in move_targets
        
        # Horizontal
        assert (3, 4) in move_targets
        assert (3, 2) in move_targets
        
        # Diagonal
        assert (4, 4) in move_targets
        assert (2, 2) in move_targets


class TestKing:
    """Test-Suite für King-Klasse."""
    
    def test_king_initialization(self):
        """Test: König wird korrekt initialisiert."""
        king = King('white', (0, 4))
        assert king.color == 'white'
        assert king.notation == 'K'
        assert not king.moved
        assert not king.checkmate
    
    def test_king_one_square_moves(self):
        """Test: König bewegt sich ein Feld in alle Richtungen."""
        board = Board()
        king = King('white', (3, 3))  # d4
        board.squares[3, 3] = king
        board.white_king = king
        
        legal_moves = king.get_legal_moves(board)
        move_targets = [move.to_pos for move in legal_moves]
        
        # Alle 8 Richtungen
        expected_moves = [
            (4, 3), (4, 4), (3, 4), (2, 4),
            (2, 3), (2, 2), (3, 2), (4, 2)
        ]
        
        for move in expected_moves:
            assert move in move_targets
    
    def test_king_cannot_move_into_check(self):
        """Test: König kann nicht ins Schach ziehen."""
        board = Board()
        white_king = King('white', (3, 3))
        board.squares[3, 3] = white_king
        board.white_king = white_king
        
        # Schwarzer Turm bedroht (3, 4)
        black_rook = Rook('black', (3, 7))
        board.squares[3, 7] = black_rook
        
        from chess_project.chess_logic import ChessLogic
        logic = ChessLogic(board)
        legal_moves = logic.all_legal_moves(last_move=None, current_turn='white')
        king_moves = [move for move in legal_moves if move.piece == white_king]
        move_targets = [move.to_pos for move in king_moves]
        
        # König darf nicht nach (3, 4) ziehen
        assert (3, 4) not in move_targets
