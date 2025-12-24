"""Tests für die Zeiterfassung bei Schachzügen."""

import pytest
from move import Move
from database import DatabaseManager
from chess_timer import ChessTimer


class MockPiece:
    """Mock-Klasse für Piece-Objekte in Tests."""
    def __init__(self, color='white', notation='P'):
        self.color = color
        self.notation = notation
        self.position = (0, 0)


def test_move_with_time_attribute():
    """Test dass Move-Objekte ein time-Attribut haben können."""
    piece = MockPiece()
    move = Move(
        from_pos=(6, 4),
        to_pos=(4, 4),
        piece=piece,
        time={'white': '10:00', 'black': '10:00'}
    )
    
    assert move.time is not None
    assert move.time['white'] == '10:00'
    assert move.time['black'] == '10:00'


def test_move_without_time_attribute():
    """Test dass Move-Objekte auch ohne time-Attribut funktionieren."""
    piece = MockPiece()
    move = Move(
        from_pos=(6, 4),
        to_pos=(4, 4),
        piece=piece
    )
    
    assert move.time is None


def test_database_add_move_with_time(tmp_path):
    """Test dass add_move Zeit-Informationen speichern kann."""
    # Temporäre Datenbank für Test
    db_path = tmp_path / "test.db"
    
    db = DatabaseManager(str(db_path))
    
    # Erstelle Spieler und Spiel
    white_id = db.create_player("TestWhite")
    black_id = db.create_player("TestBlack")
    game_id = db.create_game(white_id, black_id, "timed", 10)
    
    # Füge Zug mit Zeit hinzu
    db.add_move(
        game_id=game_id,
        move_number=1,
        notation="e2-e4",
        white_time="09:58",
        black_time="10:00"
    )
    
    # Hole Züge und prüfe
    moves = db.get_moves(game_id)
    assert len(moves) == 1
    assert moves[0]['notation'] == "e2-e4"
    assert moves[0]['white_time'] == "09:58"
    assert moves[0]['black_time'] == "10:00"
    
    db.close()


def test_database_add_move_without_time(tmp_path):
    """Test dass add_move auch ohne Zeit-Informationen funktioniert."""
    # Temporäre Datenbank für Test
    db_path = tmp_path / "test.db"
    
    db = DatabaseManager(str(db_path))
    
    # Erstelle Spieler und Spiel
    white_id = db.create_player("TestWhite2")
    black_id = db.create_player("TestBlack2")
    game_id = db.create_game(white_id, black_id, "untimed")
    
    # Füge Zug ohne Zeit hinzu
    db.add_move(
        game_id=game_id,
        move_number=1,
        notation="d2-d4"
    )
    
    # Hole Züge und prüfe
    moves = db.get_moves(game_id)
    assert len(moves) == 1
    assert moves[0]['notation'] == "d2-d4"
    assert moves[0]['white_time'] is None
    assert moves[0]['black_time'] is None
    
    db.close()


def test_chess_timer_time_strings():
    """Test dass ChessTimer Zeit-Strings korrekt formatiert."""
    # Countdown-Modus
    timer = ChessTimer(time_per_player_minutes=5, stopwatch_mode=False)
    
    # 5 Minuten = 300 Sekunden
    assert timer.white_time == 300
    assert timer.get_white_time_string() == "05:00"
    assert timer.get_black_time_string() == "05:00"
    
    # Ändere Zeit manuell
    timer.white_time = 90  # 1:30
    timer.black_time = 45  # 0:45
    
    assert timer.get_white_time_string() == "01:30"
    assert timer.get_black_time_string() == "00:45"


def test_chess_timer_stopwatch_mode():
    """Test dass ChessTimer im Stopwatch-Modus funktioniert."""
    # Stopwatch-Modus
    timer = ChessTimer(time_per_player_minutes=0, stopwatch_mode=True)
    
    # Startet bei 0
    assert timer.white_time == 0
    assert timer.get_white_time_string() == "00:00"
    
    # Simuliere Zeit
    timer.white_time = 120  # 2:00
    assert timer.get_white_time_string() == "02:00"


def test_database_migration_adds_time_columns(tmp_path):
    """Test dass die Migration Zeit-Spalten zur moves-Tabelle hinzufügt."""
    # Temporäre Datenbank für Test
    db_path = tmp_path / "test.db"
    
    # Erstelle alte Datenbank-Struktur
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Alte Schema ohne Zeit-Spalten
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            move_number INTEGER NOT NULL,
            notation TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    
    # Öffne mit DatabaseManager (sollte Migration durchführen)
    db = DatabaseManager(str(db_path))
    
    # Prüfe ob Spalten existieren
    cursor = db.conn.cursor()
    cursor.execute("PRAGMA table_info(moves)")
    columns = [row[1] for row in cursor.fetchall()]
    
    assert 'white_time' in columns
    assert 'black_time' in columns
    
    db.close()
