from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.window import Window
from kivy.uix.popup import Popup
import sys
sys.path.append('..')
from database import DatabaseManager
from game_controller import GameController


class ChessSquare(BoxLayout):
    """Ein einzelnes Schachfeld mit optionaler Figur."""
    def __init__(self, light, piece=None, **kwargs):
        super().__init__(**kwargs)
        self.light = light
        self.piece = piece
        self.press_callback = None
        self.dot = None  # Ellipse highlight for legal move
        self.selection_overlay = None  # Rectangle für ausgewähltes Feld
        self.check_overlay = None  # Rectangle für König im Schach (separater Layer)
        self.check_event = None  # Scheduled event zum Entfernen der Check-Markierung
        self.bind(pos=self.update_rect, size=self.update_rect)

        with self.canvas.before:
            if self.light:
                Color(0.9, 0.9, 0.95)
            else:
                Color(0.45, 0.55, 0.75)
            self.rect = Rectangle()
        
        # Füge Figurenbild hinzu
        if piece:
            self.piece_image = Image(
                source=piece.get_image_path(),
                fit_mode='contain'
            )
            self.add_widget(self.piece_image)

    def update_rect(self, *args):
        """ Zentralisiert die Mitte des Schachbrettes """
        self.rect.pos = self.pos
        self.rect.size = self.size
        if self.dot is not None:
            d = min(self.width, self.height) * 0.25
            self.dot.pos = (self.x + self.width / 2 - d / 2,
                            self.y + self.height / 2 - d / 2)
            self.dot.size = (d, d)
        if self.selection_overlay is not None:
            self.selection_overlay.pos = self.pos
            self.selection_overlay.size = self.size
        if self.check_overlay is not None:
            self.check_overlay.pos = self.pos
            self.check_overlay.size = self.size
    
    def set_piece(self, piece):
        """Setzt oder aktualisiert die Figur auf diesem Feld."""
        self.clear_widgets()
        self.piece = piece
        
        if piece:
            self.piece_image = Image(
                source=piece.get_image_path(),
                fit_mode='contain'
            )
            self.add_widget(self.piece_image)

    def set_press_callback(self, callback):
        """Setzt Callback, der bei Klick auf das Feld ausgelöst wird."""
        self.press_callback = callback

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if callable(self.press_callback):
                self.press_callback(self)
                return True
        return super().on_touch_down(touch)

    def add_highlight_dot(self, color='gray'):
        """Zeigt einen Punkt auf dem Feld (legal move).
        
        Args:
            color: 'gray' für normalen Zug, 'red' für Schlagzug
        """
        # Draw in canvas.after to be above background but under children widgets
        with self.canvas.after:
            if color == 'red':
                Color(1, 0, 0, 0.7)  # Rot mit 70% Deckkraft
            else:
                Color(0.2, 0.2, 0.2, 0.8)  # Dunkelgrau mit 80% Deckkraft
            
            d = min(self.width, self.height) * 0.25
            self.dot = Ellipse(pos=(self.x + self.width / 2 - d / 2,
                                    self.y + self.height / 2 - d / 2),
                               size=(d, d))

    def clear_highlight(self):
        """Entfernt den Punkt und Selection-Overlay vom Feld, falls vorhanden."""
        # Immer canvas.after löschen, unabhängig ob dot oder selection_overlay existiert
        self.canvas.after.clear()
        self.dot = None
        self.selection_overlay = None
    
    def add_selection_highlight(self):
        """Markiert dieses Feld als ausgewählt (graue Transparenz)."""
        with self.canvas.after:
            Color(0.5, 0.5, 0.5, 0.3)  # Grau mit 30% Transparenz
            self.selection_overlay = Rectangle(pos=self.pos, size=self.size)
    
    def add_check_highlight(self):
        """Markiert König im Schach (rot, verschwindet nach 0.8 Sekunden)."""
        from kivy.clock import Clock
        
        # Entferne vorherige Check-Markierung falls vorhanden
        self.remove_check_highlight()
        
        # Füge neue Markierung hinzu (in canvas, nicht canvas.after!)
        with self.canvas:
            Color(1, 0, 0, 0.4)  # Rot, 40% Transparenz
            self.check_overlay = Rectangle(pos=self.pos, size=self.size)
        
        # Schedule zum Entfernen nach 0.8 Sekunden
        self.check_event = Clock.schedule_once(lambda dt: self.remove_check_highlight(), 0.8)
    
    def remove_check_highlight(self):
        """Entfernt Check-Markierung vom König."""
        if self.check_event:
            self.check_event.cancel()
            self.check_event = None
        
        if self.check_overlay:
            self.canvas.remove(self.check_overlay)
            self.check_overlay = None


class ChessBoard(GridLayout):
    """10×10 Brett mit dünnem Rahmen & Koordinaten."""
    def __init__(self, board_array=None, **kwargs):
        super().__init__(**kwargs)
        self.cols = 10
        self.rows = 10
        self.spacing = 0.2  # Minimaler Rahmen
        self.padding = 0.2  # Minimaler Rahmen
        self.board_array = board_array  # numpy array mit Piece-Objekten
        self.board_obj = None  # Referenz auf Board-Objekt für legal_moves
        self.squares = {}  # Dictionary zur Speicherung der ChessSquare-Widgets
        self.checkmate_position = None  # (row, col) des Königs in Schachmatt oder None
        
        # Rahmen-Hintergrund (dunkle Metallfarbe)
        with self.canvas.before:
            Color(0.35, 0.35, 0.4, 1)  # Dunkles Metall für Rahmen
            self.bg_rect = Rectangle()
        self.bind(pos=self._update_bg, size=self._update_bg)

        for row in range(10):
            for col in range(10):

                # Ecken und Ränder - alle mit fester Größe
                if (row == 0 or row == 9) and (col == 0 or col == 9):
                    # Ecken leer
                    self.add_widget(Label(text="", size_hint=(None, None), size=(20, 20)))
                    continue

                # obere Buchstabenreihe
                if row == 0 and 1 <= col <= 8:
                    letter = chr(ord('a') + (col - 1))
                    lbl = Label(text=letter, font_size=13, size_hint=(None, None), size=(25, 25), bold=True)
                    self.add_widget(lbl)
                    continue

                # untere Buchstabenreihe
                if row == 9 and 1 <= col <= 8:
                    letter = chr(ord('a') + (col - 1))
                    lbl = Label(text=letter, font_size=13, size_hint=(None, None), size=(20, 20), bold=True)
                    self.add_widget(lbl)
                    continue

                # linke Zahlenreihe
                if col == 0 and 1 <= row <= 8:
                    number = str(9 - row)
                    lbl = Label(text=number, font_size=13, size_hint=(None, None), size=(20, 20), bold=True)
                    self.add_widget(lbl)
                    continue

                # rechte Randspalte
                if col == 9 and 1 <= row <= 8:
                    self.add_widget(Label(text="", size_hint=(None, None), size=(20, 20)))
                    continue

                # Schachfeld innen
                board_row = row - 1
                board_col = col - 1

                if 0 <= board_row <= 7 and 0 <= board_col <= 7:
                    is_light = (board_row + board_col) % 2 == 0
                    
                    # Hole Figur aus board_array, falls vorhanden
                    piece = None
                    if board_array is not None:
                        piece = board_array[board_row, board_col]
                    
                    square = ChessSquare(is_light, piece)
                    self.squares[(board_row, board_col)] = square
                    # Klick-Handler setzen
                    square.set_press_callback(lambda _sq, r=board_row, c=board_col: self._on_square_pressed(r, c))
                    self.add_widget(square)
                else:
                    self.add_widget(Label(text=""))
    
    def _update_bg(self, *args):
        """Aktualisiert den Rahmen-Hintergrund."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def update_board(self, board_array, checkmate_position: tuple = None):
        """Aktualisiert das Brett mit einem neuen board_array."""
        self.board_array = board_array
        for (row, col), square in self.squares.items():
            piece = board_array[row, col] if board_array is not None else None
            square.set_piece(piece)
            
            # Check-Highlighting: Rote transparente Farbe für König in Schach (2 Sekunden)
            if checkmate_position is not None and (row, col) == checkmate_position:
                square.add_check_highlight()

    def set_board(self, board_obj):
        """Setzt Referenz auf das Board-Objekt (für legal_moves)."""
        self.board_obj = board_obj
    
    def set_controller(self, controller):
        """
        Setzt Referenz auf den GameController.
        
        Ab jetzt werden alle Klicks über den Controller geleitet,
        der dann entscheidet, was zu tun ist.
        
        Args:
            controller: GameController Instanz
        """
        self.controller = controller

    def clear_highlights(self):
        for sq in self.squares.values():
            sq.clear_highlight()

    def _on_square_pressed(self, row, col):
        """
        Bei Klick auf ein Feld: Controller benachrichtigen.
        
        Statt selbst die Logik zu implementieren, delegieren wir
        an den Controller. Der Controller entscheidet dann:
        - Figur auswählen?
        - Zug ausführen?
        - Auswahl aufheben?
        
        Das ist das "Observer Pattern" - das Widget beobachtet Klicks
        und informiert den Controller (Observer).
        """
        # Falls Controller gesetzt ist, diesen nutzen
        if hasattr(self, 'controller') and self.controller:
            self.controller.on_square_clicked(row, col)
        
        # Alte Logik als Fallback (für Rückwärtskompatibilität)
        elif self.board_obj is not None:
            piece = self.board_obj.squares[row, col]
            # Leere vorherige Markierungen
            self.clear_highlights()
            if not piece:
                return
            try:
                moves = piece.get_legal_moves(self.board_obj)
            except Exception:
                moves = []
            # Erwartet Liste von (r, c)
            for mv in moves:
                if isinstance(mv, (tuple, list)) and len(mv) == 2:
                    r, c = mv
                    if (r, c) in self.squares:
                        self.squares[(r, c)].add_highlight_dot()


class GameOverPopup(Popup):
    """Popup für Spielende (Checkmate oder Remis)."""
    def __init__(self, result_type, winner=None, controller=None, **kwargs):
        """
        Args:
            result_type: 'checkmate' oder 'stalemate'
            winner: 'white' oder 'black' (nur bei checkmate)
            controller: GameController für Navigation
        """
        super().__init__(**kwargs)
        self.controller = controller
        
        self.size_hint = (0.6, 0.5)
        self.auto_dismiss = False
        
        # Layout
        layout = BoxLayout(orientation='vertical', spacing=20, padding=30)
        
        # Titel und Nachricht basierend auf Ergebnis
        if result_type == 'checkmate':
            self.title = 'Schachmatt!'
            winner_text = 'Weiß' if winner == 'white' else 'Schwarz'
            message = f'{winner_text} gewinnt!'
            title_color = (0.9, 0.7, 0.2, 1)  # Gold
        else:  # stalemate
            self.title = 'Remis!'
            message = 'Patt - Unentschieden!'
            title_color = (0.6, 0.6, 0.6, 1)  # Grau
        
        # Nachricht
        message_label = Label(
            text=message,
            size_hint=(1, 0.3),
            font_size='32sp',
            bold=True,
            color=title_color
        )
        layout.add_widget(message_label)
        
        # Button-Container
        button_container = BoxLayout(
            orientation='vertical',
            spacing=15,
            size_hint=(1, 0.7)
        )
        
        # Neues Spiel Button
        new_game_btn = Button(
            text='Neues Spiel',
            font_size='24sp',
            background_color=(0.2, 0.7, 0.3, 1),
            bold=True,
            size_hint=(1, 0.33)
        )
        new_game_btn.bind(on_press=self.new_game)
        button_container.add_widget(new_game_btn)
        
        # Hauptmenü Button
        menu_btn = Button(
            text='Hauptmenü',
            font_size='24sp',
            background_color=(0.3, 0.4, 0.7, 1),
            bold=True,
            size_hint=(1, 0.33)
        )
        menu_btn.bind(on_press=self.go_to_menu)
        button_container.add_widget(menu_btn)
        
        # Beenden Button
        quit_btn = Button(
            text='Beenden',
            font_size='24sp',
            background_color=(0.7, 0.2, 0.2, 1),
            bold=True,
            size_hint=(1, 0.33)
        )
        quit_btn.bind(on_press=self.quit_app)
        button_container.add_widget(quit_btn)
        
        layout.add_widget(button_container)
        self.content = layout
    
    def new_game(self, instance):
        """Startet neues Spiel."""
        self.dismiss()
        if self.controller:
            self.controller.restart_game()
    
    def go_to_menu(self, instance):
        """Geht zum Hauptmenü."""
        self.dismiss()
        if self.controller:
            self.controller.go_to_menu()
    
    def quit_app(self, instance):
        """Beendet die App."""
        self.dismiss()
        if self.controller:
            self.controller.quit_app()


class PromotionPopup(Popup):
    """Popup für Bauern-Promotion (Wahl zwischen Q, R, B, N)."""
    def __init__(self, color, callback, **kwargs):
        """
        Args:
            color: 'white' oder 'black' - Farbe der Figur
            callback: Funktion die aufgerufen wird mit gewählter Figur ('Q', 'R', 'B', 'N')
        """
        super().__init__(**kwargs)
        self.callback = callback
        self.color = color
        
        # Titel basierend auf Farbe
        color_text = 'Weißer' if color == 'white' else 'Schwarzer'
        self.title = f'Bauern-Beförderung'
        self.size_hint = (0.6, 0.5)
        self.auto_dismiss = False  # Spieler muss wählen
        
        # Layout
        layout = BoxLayout(orientation='vertical', spacing=20, padding=20)
        
        # Info-Text
        info_label = Label(
            text=f'{color_text} Bauer erreicht die gegnerische Grundlinie!\nWähle eine neue Figur:',
            size_hint=(1, 0.2),
            font_size='20sp',
            halign='center'
        )
        layout.add_widget(info_label)
        
        # Button-Container (2x2 Grid)
        button_grid = GridLayout(cols=2, spacing=15, size_hint=(1, 0.8))
        
        # Queen Button
        queen_btn = Button(
            text='Dame (Q)',
            font_size='22sp',
            background_color=(0.9, 0.7, 0.2, 1),
            bold=True
        )
        queen_btn.bind(on_press=lambda x: self.select_piece('Q'))
        button_grid.add_widget(queen_btn)
        
        # Rook Button
        rook_btn = Button(
            text='Turm (R)',
            font_size='22sp',
            background_color=(0.3, 0.6, 0.8, 1),
            bold=True
        )
        rook_btn.bind(on_press=lambda x: self.select_piece('R'))
        button_grid.add_widget(rook_btn)
        
        # Bishop Button
        bishop_btn = Button(
            text='Läufer (B)',
            font_size='22sp',
            background_color=(0.6, 0.4, 0.7, 1),
            bold=True
        )
        bishop_btn.bind(on_press=lambda x: self.select_piece('B'))
        button_grid.add_widget(bishop_btn)
        
        # Knight Button
        knight_btn = Button(
            text='Springer (N)',
            font_size='22sp',
            background_color=(0.4, 0.7, 0.4, 1),
            bold=True
        )
        knight_btn.bind(on_press=lambda x: self.select_piece('N'))
        button_grid.add_widget(knight_btn)
        
        layout.add_widget(button_grid)
        self.content = layout
    
    def select_piece(self, piece_type):
        """Wird aufgerufen wenn Spieler eine Figur wählt."""
        if self.callback:
            self.callback(piece_type)
        self.dismiss()


class StartMenuScreen(Screen):
    """Start-Menü mit New Game, Settings, Quit Buttons."""
    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        
        # Einfacher dunkler Hintergrund ohne Muster
        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_bg, size=self.update_bg)

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=[150, 100, 150, 100], spacing=30)

        # Centered panel
        panel = BoxLayout(orientation='vertical', spacing=20)

        # Panel background
        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        
        panel.bind(pos=self._update_panel, size=self._update_panel)

        # Title Section
        title_box = BoxLayout(orientation='vertical', size_hint=(1, 0.2), padding=[0, 20, 0, 10])
        
        title = Label(
            text='SCHACH',
            font_size='48sp',
            size_hint=(1, 1),
            bold=True,
            color=(0.95, 0.95, 1, 1)
        )
        title_box.add_widget(title)
        panel.add_widget(title_box)

        # Separator line
        # Separator line
        separator = Widget(size_hint=(1, 0.02))
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        panel.add_widget(separator)

        # Button container
        button_container = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint=(1, 0.68),
            padding=[80, 20, 80, 20]
        )

        # New Game Button - Grün
        new_game_btn = Button(
            text='Neues Spiel',
            font_size='26sp',
            size_hint=(1, 0.33),
            background_color=(0.2, 0.7, 0.3, 1),
            bold=True
        )
        new_game_btn.bind(on_press=self.start_game)
        button_container.add_widget(new_game_btn)

        # Stats Button - Blau
        stats_btn = Button(
            text='Statistiken',
            font_size='26sp',
            size_hint=(1, 0.33),
            background_color=(0.3, 0.4, 0.7, 1),
            bold=True
        )
        stats_btn.bind(on_press=self.open_stats)
        button_container.add_widget(stats_btn)

        # Quit Button - Rot
        quit_btn = Button(
            text='Beenden',
            font_size='26sp',
            size_hint=(1, 0.33),
            background_color=(0.7, 0.2, 0.2, 1),
            bold=True
        )
        quit_btn.bind(on_press=self.quit_app)
        button_container.add_widget(quit_btn)

        panel.add_widget(button_container)
        main_layout.add_widget(panel)
        self.add_widget(main_layout)
    
    def start_game(self, instance):
        if self.controller:
            self.controller.go_to_player_selection()
        else:
            self.manager.current = 'player_selection'
    
    def open_stats(self, instance):
        if self.controller:
            self.controller.go_to_stats_menu()
        else:
            self.manager.current = 'stats_menu'
    
    def quit_app(self, instance):
        if self.controller:
            self.controller.quit_app()
        else:
            App.get_running_app().stop()

    def _update_panel(self, instance, value):
        """Update panel rectangle."""
        self.panel_rect.pos = instance.pos
        self.panel_rect.size = instance.size
    
    def _update_separator(self, instance, value):
        """Aktualisiert Separator Position und Größe - zentriert."""
        margin = instance.width * 0.2
        self.sep_rect.pos = (instance.x + margin, instance.y + instance.height / 2 - 1)
        self.sep_rect.size = (instance.width - 2 * margin, 2)

    def update_bg(self, *args):
        """Update background rectangle."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.sep_rect.pos = (instance.x + instance.width * 0.2, instance.y)
        self.sep_rect.size = (instance.width * 0.6, 2)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class PlayerSelectionScreen(Screen):
    """Screen zur Auswahl/Registrierung beider Spieler."""
    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.db = DatabaseManager()

        # Dunkler Hintergrund wie im Hauptmenü
        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # Hauptlayout mit kompakterem Padding
        main_layout = BoxLayout(orientation='vertical', padding=[120, 60, 120, 60], spacing=20)

        # Panel in der Mitte
        panel = BoxLayout(orientation='vertical', spacing=20)
        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        panel.bind(pos=self._update_panel, size=self._update_panel)

        # Titelbereich
        title_box = BoxLayout(orientation='vertical', size_hint=(1, 0.15), padding=[0, 15, 0, 5])
        title = Label(
            text='SPIELER-ANMELDUNG',
            font_size='38sp',
            size_hint=(1, 0.6),
            bold=True,
            color=(0.95, 0.95, 1, 1)
        )
        title_box.add_widget(title)

        info_label = Label(
            text='Benutzernamen eingeben oder neuen Account erstellen',
            font_size='14sp',
            size_hint=(1, 0.4),
            color=(0.7, 0.75, 0.85, 1)
        )
        title_box.add_widget(info_label)
        panel.add_widget(title_box)

        # Trennlinie
        separator = Widget(size_hint=(1, 0.02))
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        panel.add_widget(separator)

        # Spieler-Container
        players_container = BoxLayout(
            orientation='horizontal',
            spacing=25,
            size_hint=(1, 0.38),
            padding=[50, 20, 50, 20]
        )

        # Weißer Spieler
        white_box = BoxLayout(orientation='vertical', spacing=15)
        white_label = Label(
            text='WEISS',
            font_size='22sp',
            size_hint=(1, None),
            height=35,
            bold=True,
            color=(1, 1, 1, 1)
        )
        white_box.add_widget(white_label)

        self.white_input = TextInput(
            hint_text='Benutzername',
            multiline=False,
            size_hint=(1, None),
            height=50,
            font_size='20sp',
            write_tab=False,
            text_validate_unfocus=False,
            background_color=(0.22, 0.24, 0.28, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[15, 12]
        )
        self.white_input.bind(text=lambda instance, value: self.limit_name_length(instance, value, 20))  # type: ignore
        white_box.add_widget(self.white_input)
        white_box.add_widget(Widget(size_hint=(1, 1)))
        players_container.add_widget(white_box)

        # Vertikale Trennlinie
        vsep = Widget(size_hint=(None, 1), width=1)
        with vsep.canvas:
            Color(0.35, 0.37, 0.42, 1)
            self.vsep_rect = Rectangle()
        vsep.bind(pos=self._update_vsep, size=self._update_vsep)
        players_container.add_widget(vsep)

        # Schwarzer Spieler
        black_box = BoxLayout(orientation='vertical', spacing=15)
        black_label = Label(
            text='SCHWARZ',
            font_size='22sp',
            size_hint=(1, None),
            height=35,
            bold=True,
            color=(0.85, 0.85, 0.85, 1)
        )
        black_box.add_widget(black_label)

        self.black_input = TextInput(
            hint_text='Benutzername',
            multiline=False,
            size_hint=(1, None),
            height=50,
            font_size='20sp',
            write_tab=False,
            text_validate_unfocus=False,
            background_color=(0.22, 0.24, 0.28, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[15, 12]
        )
        self.black_input.bind(text=lambda instance, value: self.limit_name_length(instance, value, 20))  # type: ignore
        black_box.add_widget(self.black_input)
        black_box.add_widget(Widget(size_hint=(1, 1)))
        players_container.add_widget(black_box)

        panel.add_widget(players_container)

        # Horizontale Trennlinie vor Timer
        timer_sep = Widget(size_hint=(1, None), height=1)
        with timer_sep.canvas:
            Color(0.3, 0.32, 0.37, 1)
            self.timer_sep_rect = Rectangle()
        timer_sep.bind(pos=self._update_timer_sep, size=self._update_timer_sep)
        panel.add_widget(timer_sep)

        # Timer-Einstellungen
        timer_box = BoxLayout(orientation='vertical', spacing=0, size_hint=(1, 0.22), padding=[50, 15, 50, 10])
        
        timer_title = Label(
            text='TIMER-EINSTELLUNGEN',
            font_size='16sp',
            size_hint=(1, None),
            height=25,
            bold=True,
            color=(0.75, 0.8, 0.9, 1)
        )
        timer_box.add_widget(timer_title)
        
        timer_box.add_widget(Widget(size_hint=(1, None), height=10))
        
        timer_container = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, None), height=45)
        timer_container.add_widget(Widget(size_hint=(0.05, 1)))

        from kivy.uix.checkbox import CheckBox
        self.timer_checkbox = CheckBox(size_hint=(None, None), size=(28, 28), active=False)
        self.timer_checkbox.bind(active=self.toggle_timer_input)
        timer_container.add_widget(self.timer_checkbox)

        timer_label = Label(text='Timer aktivieren', size_hint=(None, 1), width=140, font_size='17sp', bold=True, color=(0.9, 0.92, 1, 1), halign='left')
        timer_label.bind(size=lambda l, s: setattr(l, 'text_size', (s[0], None)))
        timer_container.add_widget(timer_label)

        timer_container.add_widget(Widget(size_hint=(1, 1)))

        self.time_input = TextInput(text='10', multiline=False, size_hint=(None, None), size=(70, 38), font_size='18sp', input_filter='int', disabled=True, background_color=(0.22, 0.24, 0.28, 1), foreground_color=(1, 1, 1, 1), padding=[12, 8], halign='center')
        timer_container.add_widget(self.time_input)

        time_info = Label(text='Minuten', size_hint=(None, 1), width=80, font_size='16sp', color=(0.75, 0.78, 0.88, 1))
        timer_container.add_widget(time_info)
        
        timer_container.add_widget(Widget(size_hint=(0.05, 1)))

        timer_box.add_widget(timer_container)
        panel.add_widget(timer_box)

        # Button-Leiste unten
        button_bar = BoxLayout(orientation='horizontal', spacing=25, size_hint=(1, 0.13), padding=[50, 15, 50, 15])
        back_btn = Button(text='Zurück', font_size='22sp', bold=True, background_color=(0.55, 0.3, 0.3, 1), size_hint=(0.4, 1))
        back_btn.bind(on_press=self.go_back)
        button_bar.add_widget(back_btn)
        start_btn = Button(text='Spiel starten', font_size='22sp', bold=True, background_color=(0.2, 0.65, 0.3, 1), size_hint=(0.6, 1))
        start_btn.bind(on_press=self.start_game)
        button_bar.add_widget(start_btn)
        panel.add_widget(button_bar)

        main_layout.add_widget(panel)
        self.add_widget(main_layout)
    
    def limit_name_length(self, instance, value, max_length):
        """Begrenzt die Länge des Eingabetexts."""
        if len(value) > max_length:
            instance.text = value[:max_length]
    
    def toggle_timer_input(self, checkbox, value):
        """Aktiviert/deaktiviert Zeit-Eingabefeld."""
        self.time_input.disabled = not value

    def _update_panel(self, instance, value):
        self.panel_rect.pos = instance.pos
        self.panel_rect.size = instance.size

    def _update_separator(self, instance, value):
        """Zentriert die horizontale Trennlinie."""
        margin = instance.width * 0.2
        self.sep_rect.pos = (instance.x + margin, instance.y)
        self.sep_rect.size = (instance.width * 0.6, 2)

    def _update_vsep(self, instance, value):
        """Zentriert die vertikale Trennlinie."""
        margin = instance.height * 0.1
        self.vsep_rect.pos = (instance.x, instance.y + margin)
        self.vsep_rect.size = (instance.width, instance.height * 0.8)

    def _update_timer_sep(self, instance, value):
        """Update horizontale Trennlinie vor Timer."""
        margin = instance.width * 0.1
        self.timer_sep_rect.pos = (instance.x + margin, instance.y)
        self.timer_sep_rect.size = (instance.width * 0.8, instance.height)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _get_or_create_player(self, username: str):
        """Holt Spieler aus DB oder erstellt ihn, falls nicht vorhanden."""
        player = self.db.get_player_by_username(username)
        if not player:
            player_id = self.db.create_player(username)
            player = self.db.get_player(player_id)
        return player
    
    def start_game(self, instance):
        """Startet das Spiel mit den eingegebenen Spielern."""
        white_name = self.white_input.text.strip()
        black_name = self.black_input.text.strip()
        
        # Validierung
        if not white_name and not black_name:
            self._show_popup('Fehler', 'Bitte Benutzername für beide Spieler eingeben!')
            return

        if not white_name:
            self._show_popup('Fehler', 'Bitte Benutzername für weißen Spieler eingeben!')
            return
        
        if not black_name:
            self._show_popup('Fehler', 'Bitte Benutzername für schwarzen Spieler eingeben!')
            return
        
        if white_name.lower() == black_name.lower():
            self._show_popup('Fehler', 'Bitte zwei verschiedene Spieler eingeben!')
            return
        
        if len(white_name) < 3 or len(black_name) < 3:
            self._show_popup('Fehler', 'Der Benutzername muss mindestens drei Zeichen enthalten!')
            return
        
        # Spieler holen oder erstellen
        white_player = self._get_or_create_player(white_name), white_name
        black_player = self._get_or_create_player(black_name), black_name
        
        # Timer-Einstellungen
        use_timer = self.timer_checkbox.active
        time_per_player = None
        if use_timer:
            try:
                time_per_player = int(self.time_input.text)
                if time_per_player <= 0:
                    self._show_popup('Fehler', 'Bitte positive Zeit eingeben!')
                    return
            except ValueError:
                self._show_popup('Fehler', 'Bitte gültige Zahl für Zeit eingeben!')
                return
        
        # Spieler-Infos an Controller übergeben und Spiel starten
        if self.controller:
            self.controller.set_players(white_player, black_player, use_timer, time_per_player)
            # WICHTIG: start_new_game() VOR go_to_game() aufrufen!
            self.controller.start_new_game()
            self.controller.go_to_game()
        else:
            self.manager.current = 'game'
        
        # Eingabefelder leeren
        self.white_input.text = ''
        self.black_input.text = ''
        self.timer_checkbox.active = False
        self.time_input.text = '10'
    
    def go_back(self, instance):
        """Zurück zum Hauptmenü."""
        if self.controller:
            self.controller.go_to_menu()
        else:
            self.manager.current = 'menu'
    
    def _show_popup(self, title, message):
        """Zeigt ein Popup-Fenster an."""
        popup_layout = BoxLayout(orientation='vertical', padding=10)
        popup_layout.add_widget(Label(text=message))
        close_btn = Button(text='OK', size_hint=(1, 0.3))
        popup_layout.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=popup_layout,
            size_hint=(0.6, 0.4)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class GameScreen(Screen):
    """Spiel-Screen mit Schachbrett und Pause-Button."""
    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller  # Referenz zum GameController
        
        # Dunkler Hintergrundton wie die Menüs
        with self.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        main_layout = BoxLayout(orientation='vertical')
        
        # Top Bar mit Pause Button und Info
        top_bar = BoxLayout(size_hint=(1, 0.08), padding=10, spacing=10)
        
        pause_btn = Button(
            text='Pause',
            size_hint=(0.1, 1),
            background_color=(0.8, 0.6, 0.2, 1),
            font_size='16sp'
        )
        pause_btn.bind(on_press=self.show_pause_menu)
        top_bar.add_widget(pause_btn)
        
        # Info Label (für Spielernamen) - mit Hintergrund und Rahmen
        info_container = BoxLayout(size_hint=(0.9, 1), padding=[15, 8])
        with info_container.canvas.before:
            # Rahmen (blau-grauer Akzent passend zum Theme)
            Color(0.4, 0.5, 0.7, 0.9)
            self.info_border_rect = Rectangle()
            # Hintergrund
            Color(0.15, 0.17, 0.22, 0.95)
            self.info_bg_rect = Rectangle()
        info_container.bind(pos=self._update_info_bg, size=self._update_info_bg)
        
        self.info_label = Label(
            text='[b]WEISS AM ZUG[/b]',
            size_hint=(1, 1),
            font_size='24sp',
            markup=True,
            color=(1, 1, 1, 1)
        )
        info_container.add_widget(self.info_label)
        top_bar.add_widget(info_container)
        
        main_layout.add_widget(top_bar)
        
        # Hauptbereich: Brett + Seitenpanel
        game_layout = BoxLayout(orientation="horizontal", padding=[20, 10, 20, 10], spacing=15)
        
        # Schachbrett (links) - Container mit fester Breite
        self.board_container = BoxLayout(size_hint_x=0.65, orientation='vertical')
        
        self.board_container.add_widget(Widget(size_hint_y=0.05))  # Spacer oben
        
        # Horizontaler Container für Zentrierung
        h_container = BoxLayout(orientation='horizontal', size_hint_y=0.9)
        h_container.add_widget(Widget())  # Spacer links
        
        # Board mit fester Größe
        self.board = ChessBoard(size_hint=(None, None))
        h_container.add_widget(self.board)
        
        h_container.add_widget(Widget())  # Spacer rechts
        
        self.board_container.add_widget(h_container)
        self.board_container.add_widget(Widget(size_hint_y=0.05))  # Spacer unten
        
        # Binde Board-Größe an Container
        self.board_container.bind(size=self._update_board_size)
        
        game_layout.add_widget(self.board_container)
        
        # Rechtes Panel: Timer + Zughistorie
        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.35, spacing=10)
        
        # Timer-Bereich
        timer_box = BoxLayout(orientation='vertical', size_hint=(1, 0.35), spacing=5)
        
        timer_title = Label(
            text='Timer',
            font_size='20sp',
            size_hint=(1, 0.2),
            bold=True
        )
        timer_box.add_widget(timer_title)
        
        # Weißer Spieler Timer
        white_timer_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.35), padding=[10, 5])
        self.white_timer_label = Label(
            text='Weiß: --:--',
            font_size='24sp',
            size_hint=(0.7, 1),
            halign='left'
        )
        self.white_timer_label.bind(size=self.white_timer_label.setter('text_size'))
        white_timer_box.add_widget(self.white_timer_label)
        
        with white_timer_box.canvas.before:
            Color(0.2, 0.3, 0.2, 1)
            self.white_timer_bg = Rectangle()
        white_timer_box.bind(pos=self._update_white_timer_bg, size=self._update_white_timer_bg)
        
        timer_box.add_widget(white_timer_box)
        
        # Schwarzer Spieler Timer
        black_timer_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.35), padding=[10, 5])
        self.black_timer_label = Label(
            text='Schwarz: --:--',
            font_size='24sp',
            size_hint=(0.7, 1),
            halign='left'
        )
        self.black_timer_label.bind(size=self.black_timer_label.setter('text_size'))
        black_timer_box.add_widget(self.black_timer_label)
        
        with black_timer_box.canvas.before:
            Color(0.2, 0.2, 0.3, 1)
            self.black_timer_bg = Rectangle()
        black_timer_box.bind(pos=self._update_black_timer_bg, size=self._update_black_timer_bg)
        
        timer_box.add_widget(black_timer_box)
        
        right_panel.add_widget(timer_box)
        
        # Trennlinie
        from kivy.uix.widget import Widget as Sep
        separator = Sep(size_hint=(1, 0.02))
        right_panel.add_widget(separator)
        
        # Zughistorie mit Rahmen (verkürzt für zukünftiges Menü)
        history_box = BoxLayout(orientation='vertical', size_hint=(1, 0.48), spacing=8, padding=[10, 10])
        
        # Rahmen und Hintergrund
        with history_box.canvas.before:
            # Rahmen (blauer Akzent)
            Color(0.3, 0.4, 0.6, 0.8)
            self.history_border_rect = Rectangle()
            # Hintergrund
            Color(0.15, 0.18, 0.22, 0.9)
            self.history_bg_rect = Rectangle()
        history_box.bind(pos=self._update_history_box, size=self._update_history_box)
        
        history_title = Label(
            text='ZUGHISTORIE',
            font_size='20sp',
            size_hint=(1, None),
            height=30,
            bold=True,
            color=(0.9, 0.92, 1, 1)
        )
        history_box.add_widget(history_title)
        
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        
        self.history_label = Label(
            text='Noch keine Züge',
            font_size='22sp',
            size_hint_y=None,
            halign='left',
            valign='top',
            color=(0.85, 0.87, 0.95, 1),
            padding=[5, 5],
            markup=True
        )
        self.history_label.bind(texture_size=self.history_label.setter('size'))
        self.history_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        
        scroll.add_widget(self.history_label)
        history_box.add_widget(scroll)
        
        right_panel.add_widget(history_box)
        
        # Platzhalter für zukünftiges Menü (ca. 15% Höhe)
        # menu_placeholder = BoxLayout(size_hint=(1, 0.15))
        # right_panel.add_widget(menu_placeholder)
        
        game_layout.add_widget(right_panel)
        
        main_layout.add_widget(game_layout)
        
        self.add_widget(main_layout)
        
        # Spieler-Informationen
        self.white_player = None
        self.black_player = None
        self.use_timer = False
        self.time_per_player = None
        
        # Controller-Integration (wenn übergeben)
        if self.controller:
            self.controller.set_board_widget(self.board)
            self.controller.set_game_screen(self)
            self.board.set_controller(self.controller)
    
    def _update_info_bg(self, instance, value):
        # Rahmen (3px breit)
        border_width = 3
        self.info_border_rect.pos = instance.pos
        self.info_border_rect.size = instance.size
        # Hintergrund (innerhalb des Rahmens)
        self.info_bg_rect.pos = (instance.x + border_width, instance.y + border_width)
        self.info_bg_rect.size = (instance.width - 2 * border_width, instance.height - 2 * border_width)
    
    def _update_history_box(self, instance, value):
        """Aktualisiert Rahmen und Hintergrund der Zughistorie."""
        border_width = 2
        self.history_border_rect.pos = instance.pos
        self.history_border_rect.size = instance.size
        # Hintergrund (innerhalb des Rahmens)
        self.history_bg_rect.pos = (instance.x + border_width, instance.y + border_width)
        self.history_bg_rect.size = (instance.width - 2 * border_width, instance.height - 2 * border_width)
    
    def _update_white_timer_bg(self, instance, value):
        self.white_timer_bg.pos = instance.pos
        self.white_timer_bg.size = instance.size
    
    def _update_black_timer_bg(self, instance, value):
        self.black_timer_bg.pos = instance.pos
        self.black_timer_bg.size = instance.size
    
    def _update_bg(self, *args):
        """Hintergrund an Screen-Größe anpassen."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _update_board_size(self, instance, value):
        """Hält das Board quadratisch und auf dem Bildschirm."""
        # Nimm 90% der kleineren Dimension (Breite oder Höhe des Containers)
        size = min(self.board_container.width * 0.9, self.board_container.height * 0.9)
        self.board.width = size
        self.board.height = size
    
    def set_players(self, white_player, black_player, use_timer=False, time_per_player=None):
        """Setzt die Spieler-Informationen und Timer für das Spiel."""
        self.white_player = white_player
        self.black_player = black_player
        self.use_timer = use_timer
        self.time_per_player = time_per_player
        
        # Controller informieren
        if self.controller:
            self.controller.set_players(white_player, black_player, use_timer, time_per_player)
        
        self.info_label.text = f"{white_player[1]} (Weiß) vs {black_player[1]} (Schwarz)"
        
        # Timer aktualisieren
        if use_timer and time_per_player:
            minutes = time_per_player
            self.white_timer_label.text = f"Weiß: {minutes:02d}:00"
            self.black_timer_label.text = f"Schwarz: {minutes:02d}:00"
        else:
            self.white_timer_label.text = "Weiß: --:--"
            self.black_timer_label.text = "Schwarz: --:--"
    
    def update_turn_info(self, current_turn):
        """
        Aktualisiert die Info-Anzeige, wer am Zug ist.
        
        Diese Methode wird vom Controller aufgerufen, wenn sich
        der aktuelle Spieler ändert.
        
        Args:
            current_turn: 'white' oder 'black'
        """
        if current_turn == 'white':
            if self.white_player:
                # white_player ist ein Tuple: (player_dict, username)
                username = self.white_player[1] if isinstance(self.white_player, tuple) else self.white_player.get('username', 'Weiß')
                self.info_label.text = f"[b][color=FFFFFF]{username}[/color] (WEISS) AM ZUG[/b]"
            else:
                self.info_label.text = "[b][color=FFFFFF]WEISS[/color] AM ZUG[/b]"
        else:
            if self.black_player:
                # black_player ist ein Tuple: (player_dict, username)
                username = self.black_player[1] if isinstance(self.black_player, tuple) else self.black_player.get('username', 'Schwarz')
                self.info_label.text = f"[b][color=FFFFFF]{username}[/color] (SCHWARZ) AM ZUG[/b]"
            else:
                self.info_label.text = "[b][color=FFFFFF]SCHWARZ[/color] AM ZUG[/b]"
    
    def update_move_history(self, move_history):
        """
        Aktualisiert die Zughistorie-Anzeige.
        
        Diese Methode wird vom Controller aufgerufen, wenn ein Zug
        gemacht wurde.
        
        Args:
            move_history: Liste von Zug-Dictionaries
        """
        if not move_history:
            self.history_label.text = 'Noch keine Züge'
            return
        
        # Formatiere Züge mit Farben für weiß und schwarz
        text = ""
        for i, move in enumerate(move_history, 1):
            notation = self.controller.get_move_notation(move)
            
            # Farbe basierend auf Spieler (ungerade = weiß, gerade = schwarz)
            if i % 2 == 1:
                # Weißer Zug - hellere Farbe
                move_number = (i + 1) // 2
                text += f"[b][color=D0D0E0]{move_number}.[/color][/b] [color=FFFFFF]{notation}[/color]"
            else:
                # Schwarzer Zug - leicht gedämpfte Farbe
                text += f"  [color=C0C0D0]{notation}[/color]\n"
        
        # Füge Newline am Ende hinzu wenn ungerade Anzahl
        if len(move_history) % 2 == 1:
            text += "\n"
        
        self.history_label.text = text
        # Erzwinge Update der Größe für Scrolling
        self.history_label.texture_update()
    
    def show_pause_menu(self, instance):
        if self.controller:
            self.controller.go_to_pause_menu()
        else:
            self.manager.current = 'pause'
    
    def show_promotion_popup(self, color, callback):
        """
        Zeigt das Promotion-Popup und ruft callback mit gewählter Figur auf.
        
        Args:
            color: 'white' oder 'black'
            callback: Funktion die mit Figuren-Typ ('Q', 'R', 'B', 'N') aufgerufen wird
        """
        popup = PromotionPopup(color, callback)
        popup.open()
    
    def show_game_over_popup(self, result_type, winner, controller):
        """
        Zeigt Game-Over Popup an.
        
        Args:
            result_type: 'checkmate' oder 'stalemate'
            winner: 'white' oder 'black' (nur bei checkmate)
            controller: GameController für Navigation
        """
        popup = GameOverPopup(result_type, winner, controller)
        popup.open()


class StatsMenuScreen(Screen):
    """Menü für Statistiken und Historie."""
    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        
        # Dunkler Hintergrund wie im Hauptmenü
        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=[150, 100, 150, 100], spacing=30)

        # Centered panel
        panel = BoxLayout(orientation='vertical', spacing=20)
        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        panel.bind(pos=self._update_panel, size=self._update_panel)

        # Title
        title_box = BoxLayout(orientation='vertical', size_hint=(1, 0.2), padding=[0, 20, 0, 10])
        title = Label(
            text='STATISTIKEN',
            font_size='48sp',
            size_hint=(1, 1),
            bold=True,
            color=(0.95, 0.95, 1, 1)
        )
        title_box.add_widget(title)
        panel.add_widget(title_box)

        # Separator
        separator = Widget(size_hint=(1, 0.02))
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect_stats = Rectangle()
        separator.bind(pos=self._update_separator_stats, size=self._update_separator_stats)
        panel.add_widget(separator)

        # Button container
        button_container = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint=(1, 0.68),
            padding=[80, 20, 80, 20]
        )

        # Leaderboard - Blue
        leaderboard_btn = Button(
            text='Rangliste',
            font_size='26sp',
            size_hint=(1, 0.33),
            background_color=(0.3, 0.4, 0.7, 1),
            bold=True
        )
        leaderboard_btn.bind(on_press=self.show_leaderboard)
        button_container.add_widget(leaderboard_btn)

        # Game history - Blue (slightly different hue)
        history_btn = Button(
            text='Spielhistorie',
            font_size='26sp',
            size_hint=(1, 0.33),
            background_color=(0.3, 0.5, 0.7, 1),
            bold=True
        )
        history_btn.bind(on_press=self.show_game_history)
        button_container.add_widget(history_btn)

        # Back - Red
        back_btn = Button(
            text='Zurück',
            font_size='26sp',
            size_hint=(1, 0.33),
            background_color=(0.7, 0.2, 0.2, 1),
            bold=True
        )
        back_btn.bind(on_press=self.go_back)
        button_container.add_widget(back_btn)

        panel.add_widget(button_container)
        main_layout.add_widget(panel)
        self.add_widget(main_layout)
    
    def show_leaderboard(self, instance):
        if self.controller:
            self.controller.go_to_leaderboard()
        else:
            self.manager.current = 'leaderboard'
    
    def show_game_history(self, instance):
        if self.controller:
            self.controller.go_to_game_history()
        else:
            self.manager.current = 'game_history'
    
    def go_back(self, instance):
        if self.controller:
            self.controller.go_to_menu()
        else:
            self.manager.current = 'menu'
    
    def _update_panel(self, instance, value):
        """Update panel rectangle."""
        self.panel_rect.pos = instance.pos
        self.panel_rect.size = instance.size
    
    def _update_separator_stats(self, instance, value):
        """Aktualisiert Separator Position und Größe - zentriert."""
        margin = instance.width * 0.2
        self.sep_rect_stats.pos = (instance.x + margin, instance.y + instance.height / 2 - 1)
        self.sep_rect_stats.size = (instance.width - 2 * margin, 2)
    
    def update_bg(self, *args):
        """Update background rectangle."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class LeaderboardScreen(Screen):
    """Ranglisten-Anzeige."""
    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.db = DatabaseManager()
        
        # Dunkler Hintergrund wie im Hauptmenü
        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Hauptlayout mit Padding
        main_layout = BoxLayout(orientation='vertical', padding=[100, 50, 100, 50], spacing=20)
        
        # Panel
        panel = BoxLayout(orientation='vertical', spacing=15, padding=20)
        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        panel.bind(pos=self._update_panel, size=self._update_panel)
        
        # Titel
        title = Label(
            text='RANGLISTE',
            font_size='42sp',
            size_hint=(1, 0.12),
            bold=True,
            color=(0.95, 0.95, 1, 1)
        )
        panel.add_widget(title)
        
        # Trennlinie
        separator = Widget(size_hint=(1, None), height=2)
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        panel.add_widget(separator)
        
        # Tabellenkopf
        header = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), padding=[10, 5])
        header.add_widget(Label(text='Rang', font_size='18sp', bold=True, size_hint=(0.15, 1), color=(0.9, 0.9, 1, 1)))
        header.add_widget(Label(text='Spieler', font_size='18sp', bold=True, size_hint=(0.35, 1), halign='left', color=(0.9, 0.9, 1, 1)))
        header.add_widget(Label(text='Punkte', font_size='18sp', bold=True, size_hint=(0.2, 1), color=(0.9, 0.9, 1, 1)))
        header.add_widget(Label(text='Spiele', font_size='18sp', bold=True, size_hint=(0.15, 1), color=(0.9, 0.9, 1, 1)))
        header.add_widget(Label(text='Siege', font_size='18sp', bold=True, size_hint=(0.15, 1), color=(0.9, 0.9, 1, 1)))
        
        # Header Hintergrund
        with header.canvas.before:
            Color(0.2, 0.25, 0.3, 1)
            self.header_rect = Rectangle()
        header.bind(pos=self._update_header_rect, size=self._update_header_rect)
        
        panel.add_widget(header)
        
        # Scrollbare Liste
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint=(1, 0.65))
        
        self.leaderboard_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=2
        )
        self.leaderboard_container.bind(minimum_height=self.leaderboard_container.setter('height'))
        
        scroll.add_widget(self.leaderboard_container)
        panel.add_widget(scroll)
        
        # Zurück Button
        back_btn = Button(
            text='Zurück',
            font_size='22sp',
            size_hint=(1, 0.1),
            background_color=(0.6, 0.3, 0.3, 1),
            bold=True
        )
        back_btn.bind(on_press=self.go_back)
        panel.add_widget(back_btn)
        
        main_layout.add_widget(panel)
        self.add_widget(main_layout)
    
    def _update_panel(self, instance, value):
        self.panel_rect.pos = instance.pos
        self.panel_rect.size = instance.size
    
    def _update_separator(self, instance, value):
        """Zentriert die horizontale Trennlinie."""
        margin = instance.width * 0.2
        self.sep_rect.pos = (instance.x + margin, instance.y)
        self.sep_rect.size = (instance.width * 0.6, 2)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
    
    def on_pre_enter(self):
        """Lädt die Rangliste, wenn der Screen geöffnet wird."""
        self.load_leaderboard()
    
    def load_leaderboard(self):
        """Lädt und zeigt die Rangliste an."""
        self.leaderboard_container.clear_widgets()
        players = self.db.get_leaderboard(50)
        
        if not players:
            empty_label = Label(
                text='Noch keine Spieler registriert.',
                font_size='20sp',
                size_hint_y=None,
                height=100
            )
            self.leaderboard_container.add_widget(empty_label)
            return
        
        for i, player in enumerate(players, 1):
            # Zeilen-Container
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=50,
                padding=[10, 5]
            )
            
            # Farbliche Hervorhebung für Top 3
            if i == 1:
                rank_text = '1.'
                rank_color = (1, 0.84, 0, 1)  # Gold
            elif i == 2:
                rank_text = '2.'
                rank_color = (0.75, 0.75, 0.75, 1)  # Silber
            elif i == 3:
                rank_text = '3.'
                rank_color = (0.8, 0.5, 0.2, 1)  # Bronze
            else:
                rank_text = f'{i}.'
                rank_color = (1, 1, 1, 1)
            
            # Spalten
            rank_label = Label(
                text=rank_text,
                font_size='18sp',
                bold=i <= 3,
                size_hint=(0.15, 1),
                color=rank_color
            )
            row.add_widget(rank_label)
            
            name_label = Label(
                text=player['username'],
                font_size='18sp',
                bold=i <= 3,
                size_hint=(0.35, 1),
                halign='left',
                text_size=(None, None)
            )
            name_label.bind(size=lambda l, s: setattr(l, 'text_size', (s[0], None)))
            row.add_widget(name_label)
            
            points_label = Label(
                text=str(player['points']),
                font_size='18sp',
                size_hint=(0.2, 1),
                color=(0.3, 1, 0.3, 1) if player['points'] > 0 else (1, 1, 1, 1)
            )
            row.add_widget(points_label)
            
            games_label = Label(
                text=str(player['games_played']),
                font_size='18sp',
                size_hint=(0.15, 1)
            )
            row.add_widget(games_label)
            
            wins_label = Label(
                text=str(player['games_won']),
                font_size='18sp',
                size_hint=(0.15, 1)
            )
            row.add_widget(wins_label)
            
            # Hintergrundfarbe für Zeilen (abwechselnd)
            with row.canvas.before:
                if i % 2 == 0:
                    Color(0.15, 0.15, 0.2, 1)
                else:
                    Color(0.1, 0.1, 0.15, 1)
                row_rect = Rectangle()
            row.bind(pos=lambda r, v, rect=row_rect: setattr(rect, 'pos', r.pos),
                    size=lambda r, v, rect=row_rect: setattr(rect, 'size', r.size))
            
            self.leaderboard_container.add_widget(row)
    
    def go_back(self, instance):
        if self.controller:
            self.controller.go_to_stats_menu()
        else:
            self.manager.current = 'stats_menu'


class GameHistoryScreen(Screen):
    """Spielhistorie-Anzeige."""
    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.db = DatabaseManager()
        
        # Dunkler Hintergrund wie im Hauptmenü
        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Hauptlayout mit Padding
        main_layout = BoxLayout(orientation='vertical', padding=[100, 50, 100, 50], spacing=20)
        
        # Panel
        panel = BoxLayout(orientation='vertical', spacing=15, padding=20)
        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        panel.bind(pos=self._update_panel, size=self._update_panel)
        
        # Titel
        title = Label(
            text='SPIELHISTORIE',
            font_size='42sp',
            size_hint=(1, 0.1),
            bold=True,
            color=(0.95, 0.95, 1, 1)
        )
        panel.add_widget(title)
        
        # Trennlinie
        separator = Widget(size_hint=(1, None), height=2)
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        panel.add_widget(separator)
        
        # Scrollbare Liste
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint=(1, 0.75))
        
        self.history_label = Label(
            text='Lade Spielhistorie...',
            font_size='16sp',
            size_hint_y=None,
            halign='left',
            valign='top',
            markup=True,
            color=(0.9, 0.9, 1, 1)
        )
        self.history_label.bind(texture_size=self.history_label.setter('size'))
        self.history_label.bind(size=self.history_label.setter('text_size'))
        
        scroll.add_widget(self.history_label)
        panel.add_widget(scroll)
        
        # Zurück Button
        back_btn = Button(
            text='Zurück',
            font_size='22sp',
            size_hint=(1, 0.1),
            background_color=(0.6, 0.3, 0.3, 1),
            bold=True
        )
        back_btn.bind(on_press=self.go_back)
        panel.add_widget(back_btn)
        
        main_layout.add_widget(panel)
        self.add_widget(main_layout)
    
    def _update_panel(self, instance, value):
        self.panel_rect.pos = instance.pos
        self.panel_rect.size = instance.size
    
    def _update_separator(self, instance, value):
        """Zentriert die horizontale Trennlinie."""
        margin = instance.width * 0.2
        self.sep_rect.pos = (instance.x + margin, instance.y)
        self.sep_rect.size = (instance.width * 0.6, 2)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_pre_enter(self):
        """Lädt die Spielhistorie, wenn der Screen geöffnet wird."""
        self.load_game_history()
    
    def load_game_history(self):
        games = self.db.list_games(limit=50)
        
        if not games:
            self.history_label.text = 'Noch keine Spiele gespielt.'
            return
        
        text = '[b]Spiele[/b]\n' + '─' * 60 + '\n\n'
        
        for game in games:
            white = self.db.get_player(game['white_player_id'])
            black = self.db.get_player(game['black_player_id'])
            
            result_text = {
                'white_win': f"[color=00ff00]{white['username']} gewonnen[/color]",
                'black_win': f"[color=00ff00]{black['username']} gewonnen[/color]",
                'draw': '[color=ffff00]Remis[/color]'
            }.get(game['result'], 'Laufend')
            
            game_type = 'Mit Timer' if game['game_type'] == 'timed' else 'Ohne Timer'
            start_time = game['start_time'][:16].replace('T', ' ')  # Format: YYYY-MM-DD HH:MM
            
            text += f"[b]{white['username']}[/b] vs [b]{black['username']}[/b]\n"
            text += f"  Ergebnis: {result_text}\n"
            text += f"  Typ: {game_type} | Start: {start_time}\n\n"
        
        self.history_label.text = text
    
    def go_back(self, instance):
        if self.controller:
            self.controller.go_to_stats_menu()
        else:
            self.manager.current = 'stats_menu'


class PauseMenuScreen(Screen):
    """Pause-Menü mit Resume, Restart, Main Menu."""
    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        
        # Dunkler Hintergrund wie im Hauptmenü
        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Hauptlayout
        main_layout = BoxLayout(orientation='vertical', padding=[150, 100, 150, 100], spacing=30)
        
        # Zentriertes Panel
        panel = BoxLayout(orientation='vertical', spacing=20)
        
        # Panel-Hintergrund (dunkel mit Rahmen)
        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        panel.bind(pos=self._update_panel, size=self._update_panel)
        
        # Title mit Abstand
        title_box = BoxLayout(orientation='vertical', size_hint=(1, 0.2), padding=[0, 20, 0, 10])
        title = Label(
            text='PAUSE',
            font_size='48sp',
            size_hint=(1, 1),
            bold=True,
            color=(0.95, 0.95, 1, 1)
        )
        title_box.add_widget(title)
        panel.add_widget(title_box)
        
        # Trennlinie
        separator = Widget(size_hint=(1, 0.02))
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        panel.add_widget(separator)
        
        # Button container mit mehr Platz
        button_container = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint=(1, 0.68),
            padding=[80, 20, 80, 20]
        )
        
        # Resume Button - Grün
        resume_btn = Button(
            text='Weiterspielen',
            font_size='26sp',
            size_hint=(1, 0.25),
            background_color=(0.2, 0.7, 0.3, 1),
            bold=True
        )
        resume_btn.bind(on_press=self.resume_game)
        button_container.add_widget(resume_btn)
        
        # Restart Button - Orange
        restart_btn = Button(
            text='Neu starten',
            font_size='26sp',
            size_hint=(1, 0.25),
            background_color=(0.8, 0.5, 0.1, 1),
            bold=True
        )
        restart_btn.bind(on_press=self.restart_game)
        button_container.add_widget(restart_btn)
        
        # Main Menu Button - Blau
        menu_btn = Button(
            text='Hauptmenü',
            font_size='26sp',
            size_hint=(1, 0.25),
            background_color=(0.3, 0.4, 0.7, 1),
            bold=True
        )
        menu_btn.bind(on_press=self.go_to_menu)
        button_container.add_widget(menu_btn)
        
        # Quit Button - Rot
        quit_btn = Button(
            text='Beenden',
            font_size='26sp',
            size_hint=(1, 0.25),
            background_color=(0.7, 0.2, 0.2, 1),
            bold=True
        )
        quit_btn.bind(on_press=self.quit_app)
        button_container.add_widget(quit_btn)
        
        panel.add_widget(button_container)
        
        main_layout.add_widget(panel)
        self.add_widget(main_layout)
    
    def _update_panel(self, instance, value):
        self.panel_rect.pos = instance.pos
        self.panel_rect.size = instance.size
    
    def _update_separator(self, instance, value):
        """Zentriert die horizontale Trennlinie."""
        margin = instance.width * 0.2
        self.sep_rect.pos = (instance.x + margin, instance.y)
        self.sep_rect.size = (instance.width * 0.6, 2)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def resume_game(self, instance):
        if self.controller:
            self.controller.go_to_game()
        else:
            self.manager.current = 'game'
    
    def restart_game(self, instance):
        # Spiel über Controller neu starten
        if self.controller:
            self.controller.start_new_game()
            self.controller.go_to_game()
        else:
            self.manager.current = 'game'
    
    def go_to_menu(self, instance):
        if self.controller:
            self.controller.go_to_menu()
        else:
            self.manager.current = 'menu'
    
    def quit_app(self, instance):
        if self.controller:
            self.controller.quit_app()
        else:
            App.get_running_app().stop()


class ChessApp(App):
    def build(self):
        Window.size = (900, 700)
        
        # Screen Manager
        sm = ScreenManager()
        
        # GameController erstellen (verwaltet Navigation und Spiellogik)
        self.game_controller = GameController(sm, app=self)
        
        # Screens hinzufügen und Controller übergeben
        sm.add_widget(StartMenuScreen(name='menu', controller=self.game_controller))
        sm.add_widget(PlayerSelectionScreen(name='player_selection', controller=self.game_controller))
        sm.add_widget(GameScreen(name='game', controller=self.game_controller))
        sm.add_widget(PauseMenuScreen(name='pause', controller=self.game_controller))
        sm.add_widget(StatsMenuScreen(name='stats_menu', controller=self.game_controller))
        sm.add_widget(LeaderboardScreen(name='leaderboard', controller=self.game_controller))
        sm.add_widget(GameHistoryScreen(name='game_history', controller=self.game_controller))
        
        return sm


if __name__ == "__main__":
    ChessApp().run()

