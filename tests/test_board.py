"""Unit Tests für Board-Klasse."""

import pytest
import numpy as np
from chess_project.board import Board
from chess_project.pieces import King, Queen, Rook, Bishop, Knight, Pawn


class TestBoard:
    """Test-Suite für Board-Klasse."""
    
    def test_board_initialization(self):
        """Test: Board wird korrekt initialisiert."""
        board = Board()
        assert board.squares.shape == (8, 8)
        assert isinstance(board.squares, np.ndarray)
        assert board.white_king is None
        assert board.black_king is None
    
    def test_setup_startpos(self):
        """Test: Startposition wird korrekt aufgebaut."""
        board = Board()
        board.setup_startpos()
        
        # Prüfe weiße Figuren
        assert isinstance(board.squares[7, 0], Rook)
        assert board.squares[7, 0].color == 'white'
        assert isinstance(board.squares[7, 1], Knight)
        assert isinstance(board.squares[7, 2], Bishop)
        assert isinstance(board.squares[7, 3], Queen)
        assert isinstance(board.squares[7, 4], King)
        
        # Prüfe weiße Bauern
        for col in range(8):
            assert isinstance(board.squares[6, col], Pawn)
            assert board.squares[6, col].color == 'white'
        
        # Prüfe schwarze Figuren
        assert isinstance(board.squares[0, 0], Rook)
        assert board.squares[0, 0].color == 'black'
        assert isinstance(board.squares[0, 4], King)
        
        # Prüfe schwarze Bauern
        for col in range(8):
            assert isinstance(board.squares[1, col], Pawn)
            assert board.squares[1, col].color == 'black'
        
        # Prüfe leere Felder
        for row in range(2, 6):
            for col in range(8):
                assert board.squares[row, col] is None
        
        # Prüfe Könige-Referenzen
        assert isinstance(board.white_king, King)
        assert isinstance(board.black_king, King)
        assert board.white_king.color == 'white'
        assert board.black_king.color == 'black'
    
    def test_make_move_simple(self):
        """Test: Einfacher Zug wird korrekt ausgeführt."""
        from chess_project.move import Move
        board = Board()
        board.setup_startpos()
        
        # Weißer Bauer von e2 nach e4
        move = Move(from_pos=(6, 4), to_pos=(4, 4), piece=board.white_pieces[0])
        board.make_move(move)
        
        # Prüfe neue Position
        assert isinstance(board.squares[4, 4], Pawn)
        assert board.squares[4, 4].color == 'white'
        assert board.squares[4, 4].position == (4, 4)
        
        # Prüfe alte Position ist leer
        assert board.squares[6, 4] is None
    
    def test_make_move_capture(self):
        """Test: Schlagen funktioniert korrekt."""
        from chess_project.move import Move
        board = Board()
        board.setup_startpos()
        
        # Setze weißen Bauern manuell auf eine Position wo er schlagen kann
        white_pawn = board.squares[6, 4]
        board.squares[6, 4] = None
        board.squares[4, 4] = white_pawn
        white_pawn.position = (4, 4)
        
        # Setze schwarzen Bauern als Ziel
        black_pawn = board.squares[1, 5]
        board.squares[1, 5] = None
        board.squares[3, 5] = black_pawn
        black_pawn.position = (3, 5)
        
        # Führe Schlag-Zug aus
        move = Move((4, 4), (3, 5), white_pawn, captured=black_pawn)
        board.make_move(move)
        
        # Prüfe dass weißer Bauer jetzt auf (3, 5) steht
        assert isinstance(board.squares[3, 5], Pawn)
        assert board.squares[3, 5].color == 'white'
        assert board.squares[4, 4] is None
    
    def test_make_move_castling_kingside(self):
        """Test: Kurze Rochade wird korrekt ausgeführt."""
        from chess_project.move import Move
        board = Board()
        board.setup_startpos()
        
        # Räume Felder für kurze Rochade
        board.squares[7, 5] = None  # Bishop
        board.squares[7, 6] = None  # Knight
        
        # Führe kurze Rochade aus
        king = board.squares[7, 4]
        rook = board.squares[7, 7]
        move = Move((7, 4), (7, 6), king, castelling=rook)
        board.make_move(move)
        
        # Prüfe König-Position
        assert isinstance(board.squares[7, 6], King)
        assert board.squares[7, 4] is None
        
        # Prüfe Turm-Position
        assert isinstance(board.squares[7, 5], Rook)
        assert board.squares[7, 7] is None
    
    def test_make_move_en_passant(self):
        """Test: En Passant wird korrekt ausgeführt."""
        from chess_project.move import Move
        board = Board()
        board.setup_startpos()
        
        # Setze Bauern für En Passant auf
        white_pawn = board.squares[6, 4]
        board.squares[6, 4] = None
        board.squares[3, 4] = white_pawn
        white_pawn.position = (3, 4)
        
        black_pawn = board.squares[1, 5]
        board.squares[1, 5] = None
        board.squares[3, 5] = black_pawn
        black_pawn.position = (3, 5)
        
        # En Passant-Zug
        move = Move((3, 4), (2, 5), white_pawn, captured=black_pawn, en_passant=True)
        board.make_move(move)
        
        # Prüfe neue Position
        assert isinstance(board.squares[2, 5], Pawn)
        assert board.squares[2, 5].color == 'white'
        
        # Prüfe dass geschlagener Bauer weg ist
        assert board.squares[3, 5] is None
        assert board.squares[3, 4] is None
    
    def test_make_move_promotion(self):
        """Test: Bauernumwandlung wird korrekt ausgeführt."""
        from chess_project.move import Move
        board = Board()
        
        # Setze weißen Bauern auf vorletzte Reihe
        white_pawn = Pawn('white', (1, 4))
        board.squares[1, 4] = white_pawn
        board.white_pieces.append(white_pawn)
        
        # Promotion zu Dame
        move = Move((1, 4), (0, 4), white_pawn, promotion='Q')
        board.make_move(move)
        
        # Prüfe dass Dame auf dem Feld steht
        assert isinstance(board.squares[0, 4], Queen)
        assert board.squares[0, 4].color == 'white'
        assert board.squares[1, 4] is None
    
    def test_is_square_attacked_by_white(self):
        """Test: Erkennt ob ein Feld von Weiß angegriffen wird."""
        board = Board()
        board.setup_startpos()
        
        # Feld diagonal vor weißem Bauern wird angegriffen
        assert board.is_square_attacked_by((5, 3), 'white')
        assert board.is_square_attacked_by((5, 5), 'white')
        
        # Feld weit weg wird nicht angegriffen
        assert not board.is_square_attacked_by((2, 4), 'white')
    
    def test_is_square_attacked_by_black(self):
        """Test: Erkennt ob ein Feld von Schwarz angegriffen wird."""
        board = Board()
        board.setup_startpos()
        
        # Feld diagonal vor schwarzem Bauern wird angegriffen
        assert board.is_square_attacked_by((2, 3), 'black')
        assert board.is_square_attacked_by((2, 5), 'black')
        
        # Feld weit weg wird nicht angegriffen
        assert not board.is_square_attacked_by((5, 4), 'black')
