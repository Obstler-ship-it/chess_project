"""Unit Tests für DatabaseManager-Klasse."""

import pytest
import os
import tempfile
from chess_project.database import DatabaseManager


class TestDatabaseManager:
    """Test-Suite für DatabaseManager-Klasse."""
    
    @pytest.fixture
    def temp_db(self):
        """Erstellt eine temporäre Test-Datenbank."""
        # Erstelle temporäre Datei
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        db = DatabaseManager(path)
        yield db
        
        # Cleanup
        db.close()
        if os.path.exists(path):
            os.remove(path)
    
    def test_database_initialization(self, temp_db):
        """Test: Datenbank wird korrekt initialisiert."""
        assert temp_db.conn is not None
        
        # Prüfe ob Tabellen existieren
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'players' in tables
        assert 'games' in tables
        assert 'boards' in tables
    
    def test_create_player(self, temp_db):
        """Test: Spieler wird korrekt erstellt."""
        player_id = temp_db.create_player("TestPlayer")
        
        assert player_id is not None
        assert isinstance(player_id, int)
        
        # Prüfe Spieler in DB
        player = temp_db.get_player(player_id)
        assert player is not None
        assert player['username'] == "TestPlayer"
        assert player['points'] == 0
        assert player['games_played'] == 0
    
    def test_create_duplicate_player(self, temp_db):
        """Test: Doppelter Spielername wird verhindert."""
        temp_db.create_player("TestPlayer")
        
        # Versuch zweiten Spieler mit gleichem Namen zu erstellen
        duplicate_id = temp_db.create_player("TestPlayer")
        assert duplicate_id is None
    
    def test_get_player_by_username(self, temp_db):
        """Test: Spieler kann per Username gefunden werden."""
        player_id = temp_db.create_player("FindMe")
        
        player = temp_db.get_player_by_username("FindMe")
        assert player is not None
        assert player['id'] == player_id
        assert player['username'] == "FindMe"
    
    def test_update_player_stats_win(self, temp_db):
        """Test: Spielerstatistiken bei Sieg werden korrekt aktualisiert."""
        player_id = temp_db.create_player("Winner")
        
        # Sieg: +3 Punkte
        temp_db.update_player_stats(player_id, 3, won=True)
        
        player = temp_db.get_player(player_id)
        assert player['points'] == 3
        assert player['games_won'] == 1
        assert player['games_played'] == 1
    
    def test_update_player_stats_draw(self, temp_db):
        """Test: Spielerstatistiken bei Remis werden korrekt aktualisiert."""
        player_id = temp_db.create_player("Drawer")
        
        # Remis: +1 Punkt
        temp_db.update_player_stats(player_id, 1)
        
        player = temp_db.get_player(player_id)
        assert player['points'] == 1
        assert player['games_won'] == 0
        assert player['games_played'] == 1
    
    def test_create_game(self, temp_db):
        """Test: Spiel wird korrekt erstellt."""
        white_id = temp_db.create_player("White")
        black_id = temp_db.create_player("Black")
        
        game_id = temp_db.create_game(
            white_player_id=white_id,
            black_player_id=black_id,
            game_type='timed',
            time_per_player=10
        )
        
        assert game_id is not None
        
        game = temp_db.get_game(game_id)
        assert game is not None
        assert game['white_player_id'] == white_id
        assert game['black_player_id'] == black_id
        assert game['game_type'] == 'timed'
    
    def test_finish_game_white_wins(self, temp_db):
        """Test: Spiel wird korrekt beendet (Weiß gewinnt)."""
        white_id = temp_db.create_player("WhiteWinner")
        black_id = temp_db.create_player("BlackLoser")
        
        game_id = temp_db.create_game(white_id, black_id, 'untimed')
        temp_db.finish_game(game_id, 'white_win', 'checkmate')
        
        # Prüfe Spiel
        game = temp_db.get_game(game_id)
        assert game['result'] == 'white_win'
        assert game['final_position'] == 'checkmate'
        assert game['end_time'] is not None
        
        # Prüfe Statistiken
        white = temp_db.get_player(white_id)
        black = temp_db.get_player(black_id)
        
        assert white['points'] == 3
        assert white['games_won'] == 1
        assert black['points'] == 0
        assert black['games_won'] == 0
    
    def test_finish_game_draw(self, temp_db):
        """Test: Spiel endet Remis."""
        white_id = temp_db.create_player("White")
        black_id = temp_db.create_player("Black")
        
        game_id = temp_db.create_game(white_id, black_id, 'untimed')
        temp_db.finish_game(game_id, 'draw', 'Patt')
        
        # Prüfe Spiel
        game = temp_db.get_game(game_id)
        assert game['result'] == 'draw'
        assert game['final_position'] == 'Patt'
        
        # Beide Spieler bekommen 1 Punkt
        white = temp_db.get_player(white_id)
        black = temp_db.get_player(black_id)
        
        assert white['points'] == 1
        assert black['points'] == 1
    
    def test_add_board(self, temp_db):
        """Test: Board wird korrekt gespeichert."""
        white_id = temp_db.create_player("White")
        black_id = temp_db.create_player("Black")
        game_id = temp_db.create_game(white_id, black_id, 'untimed')
        
        board_json = '{"test": "board_data"}'
        temp_db.add_board(
            game_id=game_id,
            board_number=1,
            board_JSON=board_json,
            notation="e4",
            white_time="10:00",
            black_time="10:00"
        )
        
        # Boards abrufen
        boards = temp_db.get_game_boards(game_id)
        assert len(boards) == 1
        assert boards[0]['board_JSON'] == board_json
        assert boards[0]['notation'] == "e4"
    
    def test_get_leaderboard(self, temp_db):
        """Test: Rangliste wird korrekt abgerufen."""
        # Erstelle mehrere Spieler mit unterschiedlichen Punkten
        player1 = temp_db.create_player("Player1")
        player2 = temp_db.create_player("Player2")
        player3 = temp_db.create_player("Player3")
        
        temp_db.update_player_stats(player1, 10, won=True)
        temp_db.update_player_stats(player2, 5, won=True)
        temp_db.update_player_stats(player3, 15, won=True)
        
        leaderboard = temp_db.get_leaderboard(limit=10)
        
        # Sollte nach Punkten sortiert sein
        assert len(leaderboard) == 3
        assert leaderboard[0]['username'] == "Player3"  # 15 Punkte
        assert leaderboard[1]['username'] == "Player1"  # 10 Punkte
        assert leaderboard[2]['username'] == "Player2"  # 5 Punkte
    
    def test_get_all_games(self, temp_db):
        """Test: Alle Spiele werden abgerufen."""
        white_id = temp_db.create_player("White")
        black_id = temp_db.create_player("Black")
        
        game1_id = temp_db.create_game(white_id, black_id, 'timed')
        game2_id = temp_db.create_game(black_id, white_id, 'untimed')
        
        games = temp_db.list_games(limit=10)
        
        assert len(games) >= 2
        game_ids = [g['id'] for g in games]
        assert game1_id in game_ids
        assert game2_id in game_ids
