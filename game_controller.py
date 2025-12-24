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
from pieces import Piece
from chess_logic import ChessLogic
from move import Move
from chess_timer import ChessTimer
from database import DatabaseManager


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
        
        # Datenbank
        self.db = DatabaseManager()
        self.current_game_id = None
        
        # Spielzustand (nur während aktiven Spiels)
        self.board = None
        self.chess_logic = None
        self.current_turn = None
        self.selected_piece = None
        self.game_is_over = False
        self.last_move: Optional[Move] = None
        self.checkmate: Optional[tuple] = None
        self.move_history = []
        self.valid_moves = []  # Alle gültigen Züge für aktuellen Spieler
        self.legal_moves = [] # Alle legalen Züge für die ausgewähle Figur 
        self.pending_promotion_move: Optional[Move] = None  # Move der auf Promotion wartet
        
        # Spieler-Informationen
        self.white_player = None
        self.black_player = None
        self.use_timer = False
        self.time_per_player = None
        
        # Timer
        self.timer = None
        
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
        # Timer fortsetzen, falls pausiert
        if self.timer and self.timer.is_paused:
            self.timer.resume()
    
    def go_to_pause_menu(self):
        """Navigiert zum Pause-Menü."""
        # Timer pausieren
        if self.timer:
            self.timer.pause()
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
    
    def go_to_game_replay(self):
        """Navigiert zum Game Replay Screen."""
        self.current_screen = 'game_replay'
        self.screen_manager.current = 'game_replay'
    
    def quit_app(self):
        """Beendet die App."""
        self.app.stop()
    
    # ==================== Error Handling ====================
    
    def _handle_game_error(self, error: Exception, context: str = ""):
        """
        Zentrale Error-Handler-Methode.
        
        Bei einem Fehler:
        1. Spiel zurücksetzen
        2. Zum Hauptmenü navigieren
        
        Args:
            error: Die aufgetretene Exception
            context: Optionale Beschreibung wo der Fehler auftrat
        """
        print(f"❌ Fehler im Spiel {context}: {type(error).__name__}: {error}")
        
        # Timer stoppen falls aktiv
        if self.timer:
            try:
                self.timer.stop()
            except:
                pass
        
        # Spiel zurücksetzen
        self.board = None
        self.chess_logic = None
        self.current_turn = None
        self.selected_piece = None
        self.game_is_over = False
        self.last_move = None
        self.checkmate = None
        self.move_history = []
        self.valid_moves = []
        self.legal_moves = []
        self.pending_promotion_move = None
        self.current_game_id = None
        
        # Zurück zum Hauptmenü
        self.go_to_menu()

    
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
        try:
            # Backend initialisieren
            self.board = Board()
            self.board.setup_startpos()  # Explizit aufrufen für neues Spiel
            self.chess_logic = ChessLogic(self.board)
            
            # Spielzustand zurücksetzen
            self.current_turn = 'white'
            self.selected_piece = None
            self.last_move = None
            self.checkmate = None
            self.game_is_over = False
            self.move_history = []
            self.valid_moves = []
            
            # Berechne initiale legale Züge
            self.valid_moves = self.chess_logic.calculate_all_moves()  # Methode mit () aufrufen!
            
            # Spiel in Datenbank erstellen
            self._create_game_in_database()
            
            # Timer initialisieren
            if self.use_timer and self.time_per_player:
                # Countdown-Timer (klassischer Schach-Timer)
                self.timer = ChessTimer(
                    time_per_player_minutes=self.time_per_player,
                    on_time_up_callback=self._on_timer_expired,
                    stopwatch_mode=False
                )
            else:
                # Stoppuhr-Modus (zählt Zeit hoch)
                self.timer = ChessTimer(
                    time_per_player_minutes=0,
                    on_time_up_callback=None,
                    stopwatch_mode=True
                )
            
            # Setze UI-Update Callback
            if self.game_screen:
                self.timer.on_timer_update = self.game_screen.update_timer_display
            # Starte Timer
            self.timer.start()
            
            # UI aktualisieren
            if self.board_widget:
                self.board_widget.set_board(self.board)
                self.board_widget.update_board(self.board.squares, self.checkmate)
                self.board_widget.clear_highlights()
            
            if self.game_screen:
                # Spieler-Informationen an GameScreen weitergeben
                self.game_screen.set_players(self.white_player, self.black_player, self.use_timer, self.time_per_player)
                self.game_screen.update_turn_info(self.current_turn)
                self.game_screen.update_move_history([])
                # Initiale Timer-Anzeige aktualisieren
                if self.timer:
                    self.game_screen.update_timer_display(
                        self.timer.white_time,
                        self.timer.black_time,
                        self.timer.current_player
                    )
        except Exception as e:
            self._handle_game_error(e, "beim Spielstart")
    
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
            raise ValueError('ChessLogic ist nicht initialisiert!')
        
        try:
            moves = self.chess_logic.all_legal_moves(self.last_move, self.current_turn)
            # Fallback: Falls all_legal_moves() None zurückgibt, leere Liste verwenden
            if isinstance(moves, str):
                # Spielende (Checkmate oder Stalemate)
                self.game_over(moves, 'black' if self.current_turn == 'white' else 'white')
                self.valid_moves = []
            else:
                self.valid_moves = moves
            
            # Prüfe ob der aktuelle König im Schach steht
            king = self.board.white_king if self.current_turn == 'white' else self.board.black_king
            if king and self.chess_logic.is_in_check(king, self.chess_logic.all_moves):
                self.checkmate = king.position
            else:
                self.checkmate = None
        except Exception as e:
            self._handle_game_error(e, "bei der Berechnung gültiger Züge")
    
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
        try:
            if not self.board:
                return
            
            if self.game_is_over:
                return  # Kein Zug mehr möglich nach Spielende
            
            piece = self.board.squares[row, col]
            
            # Fall 1: Keine Figur ausgewählt -> Figur auswählen
            if self.selected_piece is None:
                if piece and piece.color == self.current_turn:
                    self.legal_moves = self._select_piece(piece)

            # Fall 2: Figur bereits ausgewählt
            else:
                # Klick auf gleiches Feld -> Auswahl aufheben
                if piece == self.selected_piece:
                    self._deselect_piece()
                
                # Klick auf eigene andere Figur -> andere Figur auswählen
                elif piece and piece.color == self.current_turn:
                    self._deselect_piece()
                    self.legal_moves = self._select_piece(piece)
                
                # Klick auf ein anderes Feld -> prüfe ob legaler Zug
                else:
                    move_executed = False
                    for move in self.legal_moves:
                        if (row, col) == move.to_pos:
                            # Klick auf legalen Zug -> Zug ausführen
                            self._execute_move(move)
                            move_executed = True
                            break
                    
                    # Wenn kein legaler Zug -> Auswahl aufheben
                    if not move_executed:
                        self._deselect_piece()
        except Exception as e:
            self._handle_game_error(e, "bei der Spielfeld-Interaktion")
    
    def _select_piece(self, piece) -> list[Move]:
        """
        Wählt eine Figur aus und zeigt legale Züge.
        
        Args:
            piece: Das Piece-Objekt
        """
        self.selected_piece = piece
        
        # Finde legale Positionen für diese Figur aus valid_moves
        legal_positions = []
        for move in self.valid_moves:
            if move.piece == piece:
                legal_positions.append(move)
        
        # UI aktualisieren: Highlights setzen
        if self.board_widget:
            self.board_widget.clear_highlights()
            
            # Markiere das ausgewählte Feld
            if piece.position in self.board_widget.squares:
                self.board_widget.squares[piece.position].add_selection_highlight()
            
            # Markiere legale Zielfelder
            for move in legal_positions:
                if move.to_pos in self.board_widget.squares:
                    # Rote Punkte für Schlagzüge, graue für normale Züge
                    if move.captured:
                        self.board_widget.squares[move.to_pos].add_highlight_dot('red')
                    else:
                        self.board_widget.squares[move.to_pos].add_highlight_dot('gray')
        return legal_positions
    
    def _deselect_piece(self):
        """Hebt die Auswahl auf und entfernt Highlights."""
        self.selected_piece = None
        
        if self.board_widget:
            self.board_widget.clear_highlights()
    
    def _execute_move(self, move: Move):
        """
        Führt einen Zug aus und aktualisiert alles.
        
        Args:
            move: Move-Objekt mit allen Zug-Informationen
        """
        try:
            # Prüfe ob Promotion nötig ist
            if move.promotion is not None:
                # Speichere Move und öffne Popup
                self.pending_promotion_move = move
                self._show_promotion_dialog(self.current_turn, self._on_promotion_selected)
            else:
                # Kein Promotion -> direkt ausführen
                self._complete_move(move)
        except Exception as e:
            self._handle_game_error(e, "bei der Zugausführung")
    
    def _on_promotion_selected(self, piece_type: str):
        """
        Callback wenn Spieler Promotion-Figur gewählt hat.
        
        Args:
            piece_type: 'Q', 'R', 'B' oder 'N'
        """
        if self.pending_promotion_move:
            # Setze gewählte Figur
            self.pending_promotion_move.promotion = piece_type
            # Führe Move aus
            self._complete_move(self.pending_promotion_move)
            # Reset pending move
            self.pending_promotion_move = None
    
    def _show_promotion_dialog(self, color, callback):
        """
        Öffnet Promotion-Popup und ruft callback mit gewählter Figur auf.
        
        Args:
            color: 'white' oder 'black'
            callback: Funktion die mit 'Q', 'R', 'B' oder 'N' aufgerufen wird
        """
        if self.game_screen:
            self.game_screen.show_promotion_popup(color, callback)
        else:
            # Fallback: Standardmäßig Dame
            callback('Q')
    
    def _show_game_over_popup(self, result_type, winner=None):
        """
        Zeigt Game-Over Popup an (Checkmate oder Stalemate).
        
        Args:
            result_type: 'checkmate' oder 'stalemate'
            winner: 'white' oder 'black' (nur bei checkmate)
        """
        if self.game_screen:
            self.game_screen.show_game_over_popup(result_type, winner, self)

    def _show_time_up_popup(self, winner=None):
        """
        Zeigt Game-Over Popup an wenn Zeit abgelaufen ist.
        
        Args:
            result_type: 'checkmate' oder 'stalemate'
            winner: 'white' oder 'black' (nur bei checkmate)
        """
        if self.game_screen:
            self.game_screen.show_time_up_popup(winner, self)
    
    def _complete_move(self, move: Move):
        """
        Führt den Zug komplett aus (nachdem evtl. Promotion gewählt wurde).
        
        Args:
            move: Move-Objekt mit allen Zug-Informationen
        """
        try:
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
                self.board_widget.update_board(self.board.squares, self.checkmate)
            
            # Timer umschalten
            if self.timer:
                self.timer.switch_player()

            if self.game_screen:
                self.game_screen.update_turn_info(self.current_turn)
                self.game_screen.update_move_history(self.move_history)
        except Exception as e:
            self._handle_game_error(e, "bei der Zugvervollständigung")
    
    # ==================== Timer-Management ====================
    
    def _on_timer_expired(self, color):
        """
        Callback wenn die Zeit eines Spielers abgelaufen ist.
        
        Args:
            color: 'white' oder 'black' - wer hat keine Zeit mehr
        """
        # Gewinner ist der andere Spieler
        winner = 'black' if color == 'white' else 'white'
        
        # Zeige Game-Over Popup
        self.game_over('timeover', winner)
    
    # ==================== Hilfsmethoden ====================
    
    def game_over(self, result_type, winner=None):
        """
        Beendet das Spiel und zeigt Game-Over Popup an.
        
        Args:
            result_type: 'checkmate' oder 'stalemate' oder 'timeover'
            winner: 'white' oder 'black' (nur bei checkmate/timeover)
        """
        # Timer stoppen
        if self.timer:
            self.timer.stop()   

        self.game_is_over = True
        self._deselect_piece()
        
        # Gewinner ist der ANDERE Spieler (der gerade gezogen hat)
        winner = 'black' if self.current_turn == 'white' else 'white'
            
        # Spielergebnis in Datenbank speichern
        if result_type == 'checkmate':
            self._save_game_result(f'{winner}_win')
            self._show_game_over_popup('checkmate', winner)
            return
        elif result_type == 'stalemate':
            self._save_game_result('Patt')
            self._show_game_over_popup('draw')
            return
        elif result_type == 'draw':
            self._save_game_result('Remis')
            self._show_game_over_popup('draw')
            return
        elif result_type == 'timeover':
            self._save_game_result(f'{winner}_win')
            self._show_time_up_popup(winner)
            return
        else:
            raise NotImplementedError('undefined')
            
        for index, move in enumerate(self.move_historie):
            # Zug in Datenbank speichern
            if self.current_game_id:
                notation = self.get_move_notation(move)
                self.db.add_move(
                    game_id=self.current_game_id,
                    move_number=index,
                    move = move,
                    notation=notation
                )

    def get_move_notation(self, move: Move) -> str:
        """
        Konvertiert einen Move in Schachnotation (z.B. "e2-e4").
        
        Args:
            move: Move-Objekt
        
        Returns:
            String mit Zugnotation
        """
        # Rochade
        if move.castelling:
            if move.to_pos[1] == 6:  # Kurze Rochade
                return "O-O"
            else:  # Lange Rochade
                return "O-O-O"
        
        # Normale Züge
        to_row, to_col = move.to_pos
        to_notation = chr(ord('a') + to_col) + str(8 - to_row)
        
        symbol = move.piece.notation
        piece_symbol = '' if symbol == 'P' else symbol
        capture_symbol = 'x' if move.captured else '-'
        
        notation = f"{piece_symbol}{capture_symbol}{to_notation}"
        
        # Promotion
        if move.promotion:
            notation += '=' + move.promotion.upper()
        
        return notation

    # ==================== Datenbank-Integration ====================
    
    def _create_game_in_database(self):
        """Erstellt neues Spiel in der Datenbank."""
        if not self.white_player or not self.black_player:
            return  # Kein Spiel ohne Spieler
        
        # Spieler in Datenbank holen oder erstellen
        white_username = self.white_player[1] if isinstance(self.white_player, tuple) else self.white_player.get('username')
        black_username = self.black_player[1] if isinstance(self.black_player, tuple) else self.black_player.get('username')
        
        white_player_data = self.db.get_player_by_username(white_username)
        if not white_player_data:
            white_player_id = self.db.create_player(white_username)
        else:
            white_player_id = white_player_data['id']
        
        black_player_data = self.db.get_player_by_username(black_username)
        if not black_player_data:
            black_player_id = self.db.create_player(black_username)
        else:
            black_player_id = black_player_data['id']
        
        # Spiel erstellen
        game_type = 'timed' if self.use_timer else 'untimed'
        self.current_game_id = self.db.create_game(
            white_player_id=white_player_id,
            black_player_id=black_player_id,
            game_type=game_type,
            time_per_player=self.time_per_player
        )
    
    def _save_game_result(self, result):
        """
        Speichert Spielergebnis in Datenbank.
        
        Args:
            result: 'white_win', 'black_win', oder 'draw'
        """
        if not self.current_game_id:
            return  # Kein Spiel zu speichern
        
        # Board-Zustand als JSON serialisieren
        final_position = self._serialize_board()
        
        # Spiel beenden und Statistiken aktualisieren
        self.db.finish_game(self.current_game_id, result, final_position)
        self.current_game_id = None
    
    def _serialize_board(self) -> str:
        """
        Serialisiert das aktuelle Board als JSON-String.
        
        Returns:
            JSON-String mit Board-Zustand
        """
        if not self.board:
            return ""
        
        import json
        board_data = []
        
        for row in range(8):
            for col in range(8):
                piece = self.board.squares[row, col]
                if piece:
                    board_data.append({
                        "row": row,
                        "col": col,
                        "type": piece.__class__.__name__,
                        "color": piece.color
                    })
        
        return json.dumps(board_data)
    
    # ==================== Remis-Funktionalität ====================
    
    def request_draw(self):
        """
        Wird aufgerufen wenn Remis-Button gedrückt wird.
        Öffnet Bestätigungs-Popup.
        """
        if self.game_is_over:
            return  # Kein Remis nach Spielende möglich
        
        if self.game_screen:
            self.game_screen.show_draw_confirm_popup()
    
    def confirm_draw(self):
        """
        Wird aufgerufen wenn Remis im Popup bestätigt wurde.
        Beendet das Spiel mit Remis-Ergebnis.
        """
        if self.game_is_over:
            return
        
        # Spiel als beendet markieren
        self.game_over('draw', None)
    
    # ==================== Öffentliche Datenbank-API für UI ====================
    
    def get_or_create_player(self, username: str):
        """
        Holt Spieler aus DB oder erstellt ihn, falls nicht vorhanden.
        Diese Methode wird vom Frontend (PlayerSelectionScreen) aufgerufen.
        
        Args:
            username: Benutzername des Spielers
            
        Returns:
            Dict mit Spielerdaten
        """
        player = self.db.get_player_by_username(username)
        if not player:
            player_id = self.db.create_player(username)
            player = self.db.get_player(player_id)
        return player
    
    def get_leaderboard(self, limit: int = 50):
        """
        Holt Rangliste aus der Datenbank.
        Diese Methode wird vom Frontend (LeaderboardScreen) aufgerufen.
        
        Args:
            limit: Anzahl der anzuzeigenden Spieler
            
        Returns:
            Liste von Spieler-Dicts
        """
        return self.db.get_leaderboard(limit)
    
    def get_games_list(self, limit: int = 50):
        """
        Holt Spieleliste aus der Datenbank.
        Diese Methode wird vom Frontend (HistoryScreen) aufgerufen.
        
        Args:
            limit: Anzahl der anzuzeigenden Spiele
            
        Returns:
            Liste von Spiel-Dicts
        """
        return self.db.list_games(limit=limit)
    
    def get_player_by_id(self, player_id: int):
        """
        Holt Spieler nach ID aus der Datenbank.
        Diese Methode wird vom Frontend (HistoryScreen) aufgerufen.
        
        Args:
            player_id: ID des Spielers
            
        Returns:
            Dict mit Spielerdaten oder None
        """
        return self.db.get_player(player_id)
    
    # ==================== Game Replay Funktionalität ====================
    
    def view_game_replay(self, game_id: int):
        """
        Öffnet das Game Replay für ein bestimmtes Spiel.
        
        Args:
            game_id: ID des Spiels
        """
        # Navigiere zum Replay Screen
        self.go_to_game_replay()
        
        # Lade das Spiel im Replay Screen
        replay_screen = self.screen_manager.get_screen('game_replay')
        replay_screen.load_game(game_id)
    
    def load_game_for_replay(self, game_id: int):
        """
        Lädt ein Spiel und seine Züge für das Replay.
        
        Args:
            game_id: ID des Spiels
            
        Returns:
            Tuple (game_data, moves_list) - Spieldaten und Liste der Zugnotationen
        """
        game_data = self.db.get_game(game_id)
        
        if not game_data:
            return None, []
        
        # Züge aus der Datenbank holen
        moves = self.db.get_moves(game_id)
        
        # Nur die Notationen extrahieren
        move_notations = [move['notation'] for move in moves]
        
        return game_data, move_notations
    
    def get_replay_position(self, move_index: int):
        """
        Gibt das Board-Array für eine bestimmte Zugposition im Replay zurück.
        
        Args:
            move_index: Index des Zugs (0 = Startposition)
            
        Returns:
            numpy array mit der Board-Position
        """
        # Erstelle ein neues Board in Startposition
        from board import Board
        replay_board = Board()
        replay_board.setup_startpos()
        
        # Wenn move_index 0 ist, gib Startposition zurück
        if move_index == 0:
            return replay_board.squares
        
        # Lade Züge aus der Datenbank (wird in load_game_for_replay gesetzt)
        if not hasattr(self, '_replay_moves') or not self._replay_moves:
            return replay_board.squares
        
        # Spiele Züge bis zum angegebenen Index nach
        # HINWEIS: Dies ist eine vereinfachte Version
        # Für vollständiges Replay müsste man die Züge wirklich ausführen
        # Das würde erfordern, die Notation in Move-Objekte zu parsen
        # Für jetzt geben wir die Startposition zurück
        
        return replay_board.squares
