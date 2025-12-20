"""
Application Controller für die Schach-App.

Der GameController verwaltet:
1. Navigation zwischen Screens (Menüs, Spiel, Statistiken)
2. App-Zustand (welcher Screen aktiv, Spieler-Infos, etc.)
3. Spiellogik-Vermittlung (Board ↔ GUI)

Trennung der Verantwortlichkeiten:
- kivy_main.py: UI-Darstellung (WIE sieht es aus?)
- game_controller.py: Logik und Navigation (WAS passiert?)
- board.py/chess_logic.py: Spielregeln (Backend)
"""

from typing import Optional
from board import Board
from chess_logic import chess_logik
from move import Move


class GameController:
    """
    Zentraler Controller für die gesamte Schach-App.
    
    Verwaltet:
    - App-Navigation (zwischen allen Screens)
    - Spielzustand (nur während aktiven Spiels)
    - Kommunikation zwischen Frontend und Backend
    
    Design Pattern: Application Controller + Mediator
    """
    
    def __init__(self, screen_manager, app):
        """
        Initialisiert Controller.
        
        Args:
            screen_manager: Kivy ScreenManager für Navigation
        """
        self.screen_manager = screen_manager
        
        # App-Zustand
        self.current_screen = 'menu'  # Aktueller Screen
        self.app = app
        
        # Spielzustand (nur während aktiven Spiels)
        self.board = None
        self.chess_logic = None
        self.current_turn = None
        self.selected_piece = None
        self.last_move: Optional[Move] = None
        self.move_history = []
        self.valid_moves = []  # Alle gültigen Züge für aktuellen Spieler
        
        # Spieler-Informationen
        self.white_player = None
        self.black_player = None
        self.use_timer = False
        self.time_per_player = None
        
        # UI-Referenzen (werden von Screens gesetzt)
        self.board_widget = None
        self.game_screen = None
    
    # ==================== Navigation ====================
    
    def go_to_menu(self):
        """Navigiert zum Hauptmenü."""
        self.current_screen = 'menu'
        self.screen_manager.current = 'menu'
    
    def go_to_player_selection(self):
        """Navigiert zur Spielerauswahl."""
        self.current_screen = 'player_selection'
        self.screen_manager.current = 'player_selection'
    
    def go_to_game(self):
        """Navigiert zum Spiel-Screen."""
        self.current_screen = 'game'
        self.screen_manager.current = 'game'
    
    def go_to_pause_menu(self):
        """Navigiert zum Pause-Menü."""
        self.current_screen = 'pause'
        self.screen_manager.current = 'pause'
    
    def go_to_stats_menu(self):
        """Navigiert zum Statistik-Menü."""
        self.current_screen = 'stats_menu'
        self.screen_manager.current = 'stats_menu'
    
    def go_to_leaderboard(self):
        """Navigiert zur Rangliste."""
        self.current_screen = 'leaderboard'
        self.screen_manager.current = 'leaderboard'
    
    def go_to_game_history(self):
        """Navigiert zur Spielhistorie."""
        self.current_screen = 'game_history'
        self.screen_manager.current = 'game_history'
    
    def quit_app(self):
        """Beendet die App."""
        self.app.stop()
    
    # ==================== Spiel-Management ====================
    
    def set_players(self, white_player, black_player, use_timer=False, time_per_player=None):
        """
        Setzt Spieler-Informationen für neues Spiel.
        
        Args:
            white_player: Dict mit Spieler-Daten (white)
            black_player: Dict mit Spieler-Daten (black)
            use_timer: Bool, ob Timer aktiviert
            time_per_player: Minuten pro Spieler (falls Timer aktiv)
        """
        self.white_player = white_player
        self.black_player = black_player
        self.use_timer = use_timer
        self.time_per_player = time_per_player
    
    def start_new_game(self):
        """
        Startet ein neues Spiel (wird aufgerufen wenn GameScreen geladen wird).
        
        Erstellt Board und chess_logic erst HIER, nicht im __init__!
        """
        # Backend initialisieren
        self.board = Board()
        self.board.setup_startpos()  # Explizit aufrufen für neues Spiel
        self.chess_logic = chess_logik(self.board)
        
        # Spielzustand zurücksetzen
        self.current_turn = 'white'
        self.selected_piece = None
        self.last_move = None
        self.move_history = []
        
        # Berechne initiale legale Züge
        self.valid_moves = self.chess_logic.starting_moves()  # Methode mit () aufrufen!
        
        # UI aktualisieren
        if self.board_widget:
            self.board_widget.set_board(self.board)
            self.board_widget.update_board(self.board.squares)
            self.board_widget.clear_highlights()
        
        if self.game_screen:
            self.game_screen.update_turn_info(self.current_turn)
            self.game_screen.update_move_history([])
    
    def restart_game(self):
        """Startet aktuelles Spiel neu (behält Spieler)."""
        self.start_new_game()
        self.go_to_game()
    
    # ==================== UI-Referenzen ====================
    
    def set_board_widget(self, board_widget):
        """
        Setzt Referenz zum ChessBoard Widget.
        
        Args:
            board_widget: Das ChessBoard Kivy-Widget
        """
        self.board_widget = board_widget
        if self.board:
            board_widget.set_board(self.board)
    
    def set_game_screen(self, game_screen):
        """
        Setzt Referenz zum GameScreen Widget.
        
        Args:
            game_screen: Das GameScreen Kivy-Widget
        """
        self.game_screen = game_screen
    
    # ==================== Spiel-Logik ====================
    
    def _update_valid_moves(self):
        """Aktualisiert alle gültigen Züge für aktuellen Spieler."""
        if not self.chess_logic:
            self.valid_moves = []
            return
        
        result = self.chess_logic.all_legal_moves(
            self.current_turn, 
            self.last_move
        )
        # Fallback: Falls all_legal_moves() None zurückgibt, leere Liste verwenden
        self.valid_moves = result if result is not None else []
    
    def on_square_clicked(self, row, col):
        """
        Callback wenn ein Schachfeld geklickt wird.
        
        Implementiert die Spiellogik:
        1. Falls keine Figur ausgewählt: Wähle Figur aus (falls eigene Farbe)
        2. Falls Figur ausgewählt: Führe Zug aus oder wähle andere Figur
        
        Args:
            row: Zeile (0-7)
            col: Spalte (0-7)
        """
        if not self.board:
            return
        
        piece = self.board.squares[row, col]
        
        # Fall 1: Keine Figur ausgewählt -> Figur auswählen
        if self.selected_piece is None:
            if piece and piece.color == self.current_turn:
                self._select_piece(piece)
        
        # Fall 2: Figur bereits ausgewählt
        else:
            # Klick auf gleiches Feld -> Auswahl aufheben
            if piece == self.selected_piece:
                self._deselect_piece()
            
            # Klick auf eigene andere Figur -> andere Figur auswählen
            elif piece and piece.color == self.current_turn:
                self._deselect_piece()
                self._select_piece(piece)
            
            # Klick auf legalen Zug -> Zug ausführen
            elif self._is_valid_move(self.selected_piece, (row, col)):
                self._execute_move(self.selected_piece, (row, col))
            
            # Klick auf illegales Feld -> Auswahl aufheben
            else:
                self._deselect_piece()
    
    def _select_piece(self, piece):
        """
        Wählt eine Figur aus und zeigt legale Züge.
        
        Args:
            piece: Das Piece-Objekt
        """
        self.selected_piece = piece
        
        # Finde legale Positionen für diese Figur aus valid_moves
        legal_positions = []
        for move_tuple in self.valid_moves:
            # Flexibles Unpacking: Bauern haben 5 Elemente (mit promotion), andere 4
            if len(move_tuple) == 5:
                target_row, target_col, captured, move_piece, promotion = move_tuple
            else:
                target_row, target_col, captured, move_piece = move_tuple
            
            if move_piece == piece:
                legal_positions.append((target_row, target_col))
        
        # UI aktualisieren: Highlights setzen
        if self.board_widget:
            self.board_widget.clear_highlights()
            for row, col in legal_positions:
                if (row, col) in self.board_widget.squares:
                    self.board_widget.squares[(row, col)].add_highlight_dot()
    
    def _deselect_piece(self):
        """Hebt die Auswahl auf und entfernt Highlights."""
        self.selected_piece = None
        
        if self.board_widget:
            self.board_widget.clear_highlights()
    
    def _is_valid_move(self, piece, target_pos: tuple) -> bool:
        """
        Prüft ob Zug gültig ist (in valid_moves Liste).
        
        Args:
            piece: Figur die bewegt werden soll
            target_pos: Zielposition (row, col)
            
        Returns:
            True wenn Zug erlaubt
        """
        row, col = target_pos
        for move_tuple in self.valid_moves:
            # Flexibles Unpacking: Bauern haben 5 Elemente, andere 4
            if len(move_tuple) == 5:
                target_row, target_col, captured, move_piece, promotion = move_tuple
            else:
                target_row, target_col, captured, move_piece = move_tuple
                
            if move_piece == piece and (target_row, target_col) == (row, col):
                return True
        return False
    
    def _execute_move(self, piece, target_pos: tuple):
        """
        Führt einen Zug aus und aktualisiert alles.
        
        Args:
            piece: Figur die bewegt wird
            target_pos: Zielposition (row, col)
        """
        from_row, from_col = piece.position
        to_row, to_col = target_pos
        target_piece = self.board.squares[to_row, to_col]
        
        # Move-Objekt erstellen
        move = Move(
            from_pos=(from_row, from_col),
            to_pos=(to_row, to_col),
            piece=piece,
            captured=target_piece,
            promotion=None  # TODO: Bauern-Promotion implementieren
        )
        
        # Zug im Board ausführen
        self.board.make_move(move)
        
        # last_move speichern
        self.last_move = move
        
        # In Historie speichern
        self.move_history.append(move)
        
        # Spieler wechseln
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        
        # Gültige Züge für nächsten Spieler berechnen
        self._update_valid_moves()
        
        # Auswahl aufheben
        self._deselect_piece()
        
        # UI aktualisieren
        if self.board_widget:
            self.board_widget.update_board(self.board.squares)
        
        if self.game_screen:
            self.game_screen.update_turn_info(self.current_turn)
            self.game_screen.update_move_history(self.move_history)
        
        # TODO: Spiel-Ende prüfen (Checkmate, Stalemate)
    
    # ==================== Hilfsmethoden ====================
    
    def undo_last_move(self):
        """Macht den letzten Zug rückgängig (optional)."""
        if not self.move_history:
            return False
        
        # TODO: Implementiere Undo-Funktion
        return False
    
    def get_move_notation(self, move: Move) -> str:
        """
        Konvertiert einen Move in Schachnotation (z.B. "e2-e4").
        
        Args:
            move: Move-Objekt
        
        Returns:
            String mit Zugnotation
        """
        to_row, to_col = move.to_pos
        symbol = move.piece.notation
        
        to_notation = chr(ord('a') + to_col) + str(8 - to_row)
        piece_symbol = symbol if symbol != 'P'  else ''
        capture_symbol = 'x' if move.captured else '-'
        
        return f"{piece_symbol}{capture_symbol}{to_notation}"
