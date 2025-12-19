"""Datenbank-Management für Schach-Anwendung mit SQLite."""

import sqlite3
from typing import Optional, List, Tuple
from datetime import datetime


class DatabaseManager:
    """Verwaltet alle Datenbankoperationen für Spieler, Spiele und Züge."""
    
    def __init__(self, db_path: str = "chess.db"):
        """
        Initialisiert die Datenbankverbindung und erstellt Tabellen falls nötig.
        
        :param db_path: Pfad zur SQLite-Datenbankdatei
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Stellt Verbindung zur Datenbank her."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Ermöglicht Zugriff per Spaltenname
    
    def _create_tables(self):
        """Erstellt die erforderlichen Tabellen falls sie nicht existieren."""
        cursor = self.conn.cursor()
        
        # Spieler-Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                points INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                games_won INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Spiele-Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                white_player_id INTEGER NOT NULL,
                black_player_id INTEGER NOT NULL,
                game_type TEXT NOT NULL,
                time_per_player INTEGER,
                start_time TEXT NOT NULL,
                end_time TEXT,
                result TEXT,
                final_position TEXT,
                FOREIGN KEY (white_player_id) REFERENCES players(id),
                FOREIGN KEY (black_player_id) REFERENCES players(id)
            )
        ''')
        
        # Züge-Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                move_number INTEGER NOT NULL,
                notation TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        ''')
        
        # Remis-Angebote-Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS draw_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                offered_by TEXT NOT NULL,
                move_number INTEGER NOT NULL,
                accepted BOOLEAN,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        ''')
        
        self.conn.commit()
    
    # ==================== SPIELER-VERWALTUNG ====================
    
    def create_player(self, username: str) -> Optional[int]:
        """
        Erstellt einen neuen Spieler.
        
        :param username: Eindeutiger Benutzername
        :return: ID des erstellten Spielers oder None bei Fehler
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO players (username) VALUES (?)',
                (username,)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # Username existiert bereits
    
    def get_player(self, player_id: int) -> Optional[dict]:
        """
        Holt einen Spieler nach ID.
        
        :param player_id: ID des Spielers
        :return: Dict mit Spielerdaten oder None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM players WHERE id = ?', (player_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_player_by_username(self, username: str) -> Optional[dict]:
        """
        Holt einen Spieler nach Benutzername.
        
        :param username: Benutzername des Spielers
        :return: Dict mit Spielerdaten oder None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM players WHERE username = ?', (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def list_all_players(self) -> List[dict]:
        """
        Listet alle registrierten Spieler auf.
        
        :return: Liste von Dicts mit Spielerdaten
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM players ORDER BY username')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_leaderboard(self, limit: int = 10) -> List[dict]:
        """
        Holt die Top-Spieler sortiert nach Punkten.
        
        :param limit: Anzahl der anzuzeigenden Spieler
        :return: Liste von Dicts mit Spielerdaten
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM players ORDER BY points DESC, games_won DESC LIMIT ?',
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def update_player_stats(self, player_id: int, points_delta: int, 
                           won: bool = False):
        """
        Aktualisiert Spieler-Statistiken nach Spielende.
        
        :param player_id: ID des Spielers
        :param points_delta: Punkteänderung (+3, +1, 0)
        :param won: Ob der Spieler gewonnen hat
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE players 
            SET points = points + ?,
                games_played = games_played + 1,
                games_won = games_won + ?
            WHERE id = ?
        ''', (points_delta, 1 if won else 0, player_id))
        self.conn.commit()
    
    # ==================== SPIEL-VERWALTUNG ====================
    
    def create_game(self, white_player_id: int, black_player_id: int,
                   game_type: str, time_per_player: Optional[int] = None) -> int:
        """
        Erstellt ein neues Spiel.
        
        :param white_player_id: ID des weißen Spielers
        :param black_player_id: ID des schwarzen Spielers
        :param game_type: 'timed' oder 'untimed'
        :param time_per_player: Minuten pro Spieler (nur bei timed)
        :return: ID des erstellten Spiels
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO games 
            (white_player_id, black_player_id, game_type, time_per_player, start_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (white_player_id, black_player_id, game_type, time_per_player, 
              datetime.now().isoformat()))
        self.conn.commit()
        return cursor.lastrowid
    
    def finish_game(self, game_id: int, result: str, final_position: str):
        """
        Beendet ein Spiel und aktualisiert Spieler-Statistiken.
        
        :param game_id: ID des Spiels
        :param result: 'white_win', 'black_win', oder 'draw'
        :param final_position: FEN-String der Endstellung
        """
        cursor = self.conn.cursor()
        
        # Spiel aktualisieren
        cursor.execute('''
            UPDATE games 
            SET end_time = ?, result = ?, final_position = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), result, final_position, game_id))
        
        # Spieler-IDs holen
        cursor.execute(
            'SELECT white_player_id, black_player_id FROM games WHERE id = ?',
            (game_id,)
        )
        white_id, black_id = cursor.fetchone()
        
        # Punkte vergeben
        if result == 'white_win':
            self.update_player_stats(white_id, 3, won=True)
            self.update_player_stats(black_id, 0)
        elif result == 'black_win':
            self.update_player_stats(black_id, 3, won=True)
            self.update_player_stats(white_id, 0)
        else:  # draw
            self.update_player_stats(white_id, 1)
            self.update_player_stats(black_id, 1)
        
        self.conn.commit()
    
    def get_game(self, game_id: int) -> Optional[dict]:
        """
        Holt ein Spiel nach ID.
        
        :param game_id: ID des Spiels
        :return: Dict mit Spieldaten oder None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM games WHERE id = ?', (game_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def list_games(self, player_id: Optional[int] = None, 
                   limit: int = 50) -> List[dict]:
        """
        Listet Spiele auf, optional gefiltert nach Spieler.
        
        :param player_id: Optional: nur Spiele dieses Spielers
        :param limit: Max. Anzahl zurückzugebender Spiele
        :return: Liste von Dicts mit Spieldaten
        """
        cursor = self.conn.cursor()
        
        if player_id:
            cursor.execute('''
                SELECT * FROM games 
                WHERE white_player_id = ? OR black_player_id = ?
                ORDER BY start_time DESC LIMIT ?
            ''', (player_id, player_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM games 
                ORDER BY start_time DESC LIMIT ?
            ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== ZUG-VERWALTUNG ====================
    
    def add_move(self, game_id: int, move_number: int, notation: str):
        """
        Fügt einen Zug zu einem Spiel hinzu.
        
        :param game_id: ID des Spiels
        :param move_number: Zugnummer
        :param notation: Standard-Schachnotation (z.B. 'e4', 'Nf3')
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO moves (game_id, move_number, notation, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (game_id, move_number, notation, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_game_moves(self, game_id: int) -> List[dict]:
        """
        Holt alle Züge eines Spiels in chronologischer Reihenfolge.
        
        :param game_id: ID des Spiels
        :return: Liste von Dicts mit Zugdaten
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM moves 
            WHERE game_id = ? 
            ORDER BY move_number
        ''', (game_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== REMIS-ANGEBOTE ====================
    
    def add_draw_offer(self, game_id: int, offered_by: str, 
                      move_number: int) -> int:
        """
        Fügt ein Remis-Angebot hinzu.
        
        :param game_id: ID des Spiels
        :param offered_by: 'white' oder 'black'
        :param move_number: Bei welchem Zug angeboten
        :return: ID des Angebots
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO draw_offers (game_id, offered_by, move_number, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (game_id, offered_by, move_number, datetime.now().isoformat()))
        self.conn.commit()
        return cursor.lastrowid
    
    def respond_to_draw_offer(self, offer_id: int, accepted: bool):
        """
        Aktualisiert ein Remis-Angebot mit Antwort.
        
        :param offer_id: ID des Angebots
        :param accepted: True wenn angenommen, False wenn abgelehnt
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE draw_offers SET accepted = ? WHERE id = ?
        ''', (accepted, offer_id))
        self.conn.commit()
    
    def get_game_draw_offers(self, game_id: int) -> List[dict]:
        """
        Holt alle Remis-Angebote eines Spiels.
        
        :param game_id: ID des Spiels
        :return: Liste von Dicts mit Angebotsdaten
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM draw_offers 
            WHERE game_id = ? 
            ORDER BY move_number
        ''', (game_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== UTILITY ====================
    
    def close(self):
        """Schließt die Datenbankverbindung."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context Manager Unterstützung."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager Unterstützung."""
        self.close()
