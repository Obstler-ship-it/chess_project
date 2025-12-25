"""
Application Controller für die Schach-App.

Der GameController verwaltet:
1. Navigation zwischen Screens (Menüs, Spiel, Statistiken)
2. App-Zustand (welcher Screen aktiv, Spieler-Infos, etc.)
3. Spiellogik-Vermittlung (Board ↔ GUI)

Trennung der Verantwortlichkeiten:
- kivy_main.py: UI-Darstellung (Frontend)
- game_controller.py: Logik und Navigation
- board.py/chess_logic.py: Spielregeln (Backend)
"""

import json
from typing import Optional
from board import Board
import board
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
        self.draw_offer = False 

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
        
        self.reset_game_state()
        
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

    def reset_game_state(self):
        """Setzt den Spielzustand zurück (ohne Spieler-Infos)."""
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
        self.draw_offer = False
        
        # Timer stoppen
        if self.timer:
            try:
                self.timer.stop()
            except:
                pass
        self.timer = None

    def start_new_game(self):
        """
        Startet ein neues Spiel (wird aufgerufen wenn GameScreen geladen wird).
        
        Erstellt Board und chess_logic erst HIER, nicht im __init__!
        """
        try:
            # Setze Spielzustand zurück
            self.reset_game_state()
            
            # Initialisiere Spielzustand
            self.current_turn = 'white'

            # Backend initialisieren
            self.board = Board()
            self.board.setup_startpos()  # Explizit aufrufen für neues Spiel
            self.chess_logic = ChessLogic(self.board)

            # Spiel in Datenbank erstellen
            self._create_game_in_database()
            
            # Berechne initiale legale Züge
            self.valid_moves = self.chess_logic.calculate_all_moves()  # Methode mit () aufrufen!
            
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

            # Auswahl aufheben
            self._deselect_piece()
            
            # UI aktualisieren
            if self.board_widget:
                self.board_widget.update_board(self.board.squares, self.checkmate)
            
            # Timer umschalten
            if self.timer:
                self.timer.switch_player()

            # DB aktualisieren
            if self.current_game_id:
                self.db.add_board(
                    game_id=self.current_game_id,
                    board_number=len(self.move_history),
                    board_JSON=self._serialize_board(),
                    notation=self.get_move_notation(self.last_move),
                    white_time=str(self.timer.white_time) if self.timer else "0",
                    black_time=str(self.timer.black_time) if self.timer else "0"
                )
            
            # Remis-Angebot zurücksetzen
            self.draw_offer = False

            # Gültige Züge für nächsten Spieler berechnen
            self._update_valid_moves()

            if self.game_screen:
                self.game_screen.update_turn_info(self.current_turn)
                self.game_screen.update_move_history(self.move_history)
        except Exception as e:
            self._handle_game_error(e, "bei der Zugvervollständigung")

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
            self._save_game_result(f'{winner}_win', 'checkmate')
            self._show_game_over_popup('checkmate', winner)
            return
        elif result_type == 'stalemate':
            self._save_game_result(None, 'Patt')
            self._show_game_over_popup('draw')
            return
        elif result_type == 'draw':
            self._save_game_result(None, 'Remis')
            self._show_game_over_popup('draw')
            return
        elif result_type == 'remis':
            self._save_game_result(None, 'Remis')
            self._show_game_over_popup('remis')
            return
        elif result_type == 'timeover':
            self._save_game_result(f'{winner}_win', 'timeover')
            self._show_time_up_popup(winner)
            return
        else:
            raise NotImplementedError('undefined')

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
            self.draw_offer = True
    
    def confirm_draw(self):
        """
        Wird aufgerufen wenn Remis im Popup bestätigt wurde.
        Beendet das Spiel mit Remis-Ergebnis.
        """
        if self.game_is_over:
            return
        
        # Speichere finalen Board-Zustand mit akzeptiertem Remis
        # (beide Spieler haben zugestimmt)
        if self.current_game_id:
            # Setze draw_offer auf True für BEIDE Spieler, um zu zeigen dass es akzeptiert wurde
            old_draw_offer = self.draw_offer
            self.draw_offer = True  # Temporär für Serialisierung
            
            self.db.add_board(
                game_id=self.current_game_id,
                board_number=len(self.move_history) + 1,
                board_JSON=self._serialize_board_with_accepted_draw(),
                notation="Remis akzeptiert",
                white_time=str(self.timer.white_time) if self.timer else "0",
                black_time=str(self.timer.black_time) if self.timer else "0"
            )
            
            self.draw_offer = old_draw_offer
        
        # Spiel als beendet markieren
        self.game_over('remis', None)
    
    # ==================== Hilfsmethoden ====================

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
        
        # Startposition speichern (board_number = 0)
        if self.current_game_id and self.board:
            self.db.add_board(
                game_id=self.current_game_id,
                board_number=0,
                board_JSON=self._serialize_board(),
                notation="Startposition",
                white_time=str(self.timer.white_time) if self.timer else "0",
                black_time=str(self.timer.black_time) if self.timer else "0"
            )
    
    def _save_game_result(self, winner, result_type):
        """
        Speichert Spielergebnis in Datenbank.
        
        Args:
            winner: 'white', 'black', oder None für Remis
        """
        if not self.current_game_id:
            return  # Kein Spiel zu speichern
        
        # Spiel beenden und Statistiken aktualisieren
        self.db.finish_game(self.current_game_id, winner, result_type)
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
                board_data.append({
                    "row": row,
                    "col": col,
                    "image_path": piece.get_image_path() if piece else None,
                })

        board_data.append({
            "turn": self.current_turn,
            "white_time": self.timer.white_time if self.timer else None,
            "black_time": self.timer.black_time if self.timer else None,
            "draw_offers": {"white": self.draw_offer and self.current_turn == 'black', "black": self.draw_offer and self.current_turn == 'white'},
        })

        return json.dumps(board_data)
    
    def _serialize_board_with_accepted_draw(self) -> str:
        """
        Serialisiert das Board mit akzeptiertem Remis (beide Spieler haben zugestimmt).
        
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
                board_data.append({
                    "row": row,
                    "col": col,
                    "image_path": piece.get_image_path() if piece else None,
                })

        # Beide Spieler haben Remis akzeptiert
        board_data.append({
            "turn": self.current_turn,
            "white_time": self.timer.white_time if self.timer else None,
            "black_time": self.timer.black_time if self.timer else None,
            "draw_offers": {"white": True, "black": True},  # BEIDE haben akzeptiert
        })

        return json.dumps(board_data)
    
    def _deserialize_board(self, board_json: str):
        """
        Deserialisiert ein Board aus einem JSON-String.
        
        Args:
            board_json: JSON-String mit Board-Zustand
            
        Returns:
            numpy array mit Board-Zustand
        """
        import json
        import numpy as np
        from pieces import King, Queen, Rook, Bishop, Knight, Pawn
        
        board_data = json.loads(board_json)
        
        # Erstelle leeres 8x8 Board
        board_array = np.empty((8, 8), dtype=object)
        
        # Mapping von Notation zu Klassen
        piece_classes = {
            'K': King,
            'Q': Queen,
            'R': Rook,
            'B': Bishop,
            'N': Knight,
            'P': Pawn
        }
        
        # Fülle Board mit Figuren aus JSON
        for item in board_data:
            if 'row' in item and 'col' in item:
                row, col = item['row'], item['col']
                image_path = item['image_path']
                
                if image_path:
                    # Parse image_path: 'pieces/white_K.png' -> color='white', notation='K'
                    parts = image_path.split('/')[-1].replace('.png', '').split('_')
                    if len(parts) == 2:
                        color, notation = parts
                        
                        # Erstelle entsprechende Figur
                        piece_class = piece_classes.get(notation)
                        if piece_class:
                            board_array[row, col] = piece_class(color, (row, col))
        
        return board_array
    
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
        Lädt ein Spiel und seine Boards für das Replay.
        
        Args:
            game_id: ID des Spiels
            
        Returns:
            Tuple (game_data, boards_list) - Spieldaten und Liste der Board-Daten
        """
        game_data = self.db.get_game(game_id)
        
        if not game_data:
            return None, []
        
        # Boards aus der Datenbank holen
        boards = self.db.get_game_boards(game_id)
        
        # Boards für Replay speichern
        self._replay_boards = boards
        
        return game_data, boards
    
    def get_replay_position(self, move_index: int):
        """
        Gibt das Board-Array für eine bestimmte Zugposition im Replay zurück.
        
        Args:
            move_index: Index des Boards (0 = Startposition)
            
        Returns:
            numpy array mit der Board-Position
        """
        # Prüfe ob Replay-Boards geladen sind
        if not hasattr(self, '_replay_boards') or not self._replay_boards:
            # Fallback: Erstelle Startposition
            replay_board = board.Board()
            replay_board.setup_startpos()
            return replay_board.squares
        
        # Index 0 sollte die Startposition sein
        if move_index < 0 or move_index >= len(self._replay_boards):
            # Fallback: Erstelle Startposition
            replay_board = board.Board()
            replay_board.setup_startpos()
            return replay_board.squares
        
        # Lade das entsprechende Board aus der Datenbank
        board_data = self._replay_boards[move_index]
        board_json = board_data['board_JSON']
        
        # Deserialisiere und gib Board zurück
        return self._deserialize_board(board_json)
        return replay_board.squares
