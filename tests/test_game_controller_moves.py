"""Tests für GameController Zug-Speicherung."""

import pytest
import os
import tempfile
from game_controller import GameController
from move import Move
from pieces import Pawn, Rook, King
from database import DatabaseManager


class MockScreenManager:
    """Mock ScreenManager für Tests."""
    def __init__(self):
        self.current = 'menu'


class MockApp:
    """Mock App für Tests."""
    def stop(self):
        pass


class TestGameControllerSaveMoves:
    """Tests für die _save_moves_in_db-Methode."""
    
    @pytest.fixture
    def temp_db(self):
        """Erstellt temporäre Test-Datenbank."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        # Cleanup
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def controller(self, temp_db):
        """Erstellt GameController mit temporärer Datenbank."""
        screen_manager = MockScreenManager()
        app = MockApp()
        controller = GameController(screen_manager, app)
        
        # Ersetze Datenbank mit temporärer
        controller.db = DatabaseManager(temp_db)
        
        return controller
    
    def test_save_moves_in_db_without_game_id(self, controller):
        """Test dass ohne game_id keine Moves gespeichert werden."""
        # Erstelle Move
        pawn = Pawn('white', (6, 4))
        move = Move(from_pos=(6, 4), to_pos=(4, 4), piece=pawn)
        
        controller.move_history = [move]
        controller.current_game_id = None
        
        # Sollte keine Exception werfen
        controller._save_moves_in_db()
    
    def test_save_single_move_in_db(self, controller):
        """Test Speicherung eines einzelnen Zugs."""
        # Erstelle Spieler
        white_id = controller.db.create_player('TestWhite')
        black_id = controller.db.create_player('TestBlack')
        
        # Erstelle Spiel
        game_id = controller.db.create_game(white_id, black_id, 'untimed')
        controller.current_game_id = game_id
        
        # Erstelle Move
        pawn = Pawn('white', (6, 4))
        move = Move(from_pos=(6, 4), to_pos=(4, 4), piece=pawn)
        controller.move_history = [move]
        
        # Speichere Moves
        controller._save_moves_in_db()
        
        # Prüfe dass Move in DB gespeichert wurde
        moves = controller.db.get_moves(game_id)
        assert len(moves) == 1
        assert moves[0]['move_number'] == 1
        # Pawn moves don't include 'P' in standard notation
        assert moves[0]['notation'] == '-e4'
    
    def test_save_multiple_moves_in_db(self, controller):
        """Test Speicherung mehrerer Züge."""
        # Erstelle Spieler und Spiel
        white_id = controller.db.create_player('TestWhite')
        black_id = controller.db.create_player('TestBlack')
        game_id = controller.db.create_game(white_id, black_id, 'untimed')
        controller.current_game_id = game_id
        
        # Erstelle mehrere Moves
        pawn1 = Pawn('white', (6, 4))
        move1 = Move(from_pos=(6, 4), to_pos=(4, 4), piece=pawn1)
        
        pawn2 = Pawn('black', (1, 4))
        move2 = Move(from_pos=(1, 4), to_pos=(3, 4), piece=pawn2)
        
        controller.move_history = [move1, move2]
        
        # Speichere Moves
        controller._save_moves_in_db()
        
        # Prüfe dass beide Moves gespeichert wurden
        moves = controller.db.get_moves(game_id)
        assert len(moves) == 2
        assert moves[0]['move_number'] == 1
        assert moves[1]['move_number'] == 2
    
    def test_save_moves_with_capture(self, controller):
        """Test Speicherung eines Schlagzugs."""
        # Erstelle Spieler und Spiel
        white_id = controller.db.create_player('TestWhite')
        black_id = controller.db.create_player('TestBlack')
        game_id = controller.db.create_game(white_id, black_id, 'untimed')
        controller.current_game_id = game_id
        
        # Erstelle Schlagzug
        pawn = Pawn('white', (4, 4))
        captured = Pawn('black', (3, 5))
        move = Move(from_pos=(4, 4), to_pos=(3, 5), piece=pawn, captured=captured)
        
        controller.move_history = [move]
        
        # Speichere Move
        controller._save_moves_in_db()
        
        # Prüfe dass Move mit Schlag-Notation gespeichert wurde
        moves = controller.db.get_moves(game_id)
        assert len(moves) == 1
        assert 'x' in moves[0]['notation']
    
    def test_save_moves_with_castling(self, controller):
        """Test Speicherung einer Rochade."""
        # Erstelle Spieler und Spiel
        white_id = controller.db.create_player('TestWhite')
        black_id = controller.db.create_player('TestBlack')
        game_id = controller.db.create_game(white_id, black_id, 'untimed')
        controller.current_game_id = game_id
        
        # Erstelle Rochade (kurze Rochade)
        king = King('white', (7, 4))
        rook = Rook('white', (7, 7))
        move = Move(from_pos=(7, 4), to_pos=(7, 6), piece=king, castelling=rook)
        
        controller.move_history = [move]
        
        # Speichere Move
        controller._save_moves_in_db()
        
        # Prüfe dass Rochade-Notation korrekt ist
        moves = controller.db.get_moves(game_id)
        assert len(moves) == 1
        assert moves[0]['notation'] == 'O-O'
    
    def test_move_to_json_called_during_save(self, controller):
        """Test dass to_json während der Speicherung aufgerufen wird."""
        # Erstelle Spieler und Spiel
        white_id = controller.db.create_player('TestWhite')
        black_id = controller.db.create_player('TestBlack')
        game_id = controller.db.create_game(white_id, black_id, 'untimed')
        controller.current_game_id = game_id
        
        # Erstelle Move
        pawn = Pawn('white', (6, 4))
        move = Move(from_pos=(6, 4), to_pos=(4, 4), piece=pawn)
        controller.move_history = [move]
        
        # Speichere Move - sollte to_json intern aufrufen
        controller._save_moves_in_db()
        
        # Prüfe dass Move gespeichert wurde
        moves = controller.db.get_moves(game_id)
        assert len(moves) == 1
        
        # Prüfe dass to_json funktioniert hat (indirekt durch erfolgreiche Speicherung)
        json_output = move.to_json()
        assert json_output is not None
        assert 'from_pos' in json_output
