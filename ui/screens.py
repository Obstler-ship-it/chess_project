"""Kivy Screens für Menüs, Spiel und Replays."""

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from ui.board_widgets import ChessBoard
from ui.popups import GameOverPopup, PromotionPopup, RemisConfirmPopup


# ==================== GEMEINSAME HILFSMETHODEN ====================

class ScreenBackgroundMixin:
    """Mixin für gemeinsame Background-Update Methode."""
    
    def update_bg(self, *args):
        """Aktualisiert das Background-Rectangle."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class PanelMixin:
    """Mixin für Panel und Separator Updates."""
    
    def _update_panel(self, instance, value):
        """Aktualisiert das Panel-Rectangle."""
        self.panel_rect.pos = instance.pos
        self.panel_rect.size = instance.size
    
    def _update_separator(self, instance, value):
        """Aktualisiert den Separator mit 20% Margin."""
        margin = instance.width * 0.2
        self.sep_rect.pos = (instance.x + margin, instance.y)
        self.sep_rect.size = (instance.width * 0.6, 2)


def create_move_history_display(container, moves_list):
    """
    Gemeinsame Hilfsfunktion zum Erstellen der Zughistorie-Anzeige.
    
    Args:
        container: BoxLayout Container für die Züge
        moves_list: Liste von Zugnotationen (Strings)
    """
    container.clear_widgets()
    
    if not moves_list:
        empty_label = Label(
            text="Keine Züge",
            font_size=dp(18),
            size_hint_y=None,
            height=40,
            color=(0.6, 0.6, 0.7, 1),
            italic=True
        )
        container.add_widget(empty_label)
        return

    # Gruppiere Züge paarweise (Weiß und Schwarz)
    move_pairs = []
    for i in range(0, len(moves_list), 2):
        white_move = moves_list[i]
        black_move = moves_list[i + 1] if i + 1 < len(moves_list) else None
        move_pairs.append((white_move, black_move))

    for move_num, (white_move, black_move) in enumerate(move_pairs, 1):
        # Container für ein Zugpaar (eine Zeile)
        move_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=35,
            spacing=4,
            padding=[2, 2]
        )

        # Zugnummer Box
        num_box = BoxLayout(size_hint_x=0.18, padding=[4, 2])
        with num_box.canvas.before:
            Color(0.25, 0.3, 0.4, 0.9)
            num_rect = Rectangle()
        num_box.bind(
            pos=lambda instance, value, r=num_rect: setattr(r, "pos", instance.pos),
            size=lambda instance, value, r=num_rect: setattr(r, "size", instance.size)
        )
        
        num_label = Label(
            text=f"{move_num}.",
            font_size=dp(16),
            bold=True,
            color=(0.7, 0.8, 0.95, 1)
        )
        num_box.add_widget(num_label)
        move_row.add_widget(num_box)

        # Weißer Zug Box
        white_box = BoxLayout(size_hint_x=0.41, padding=[6, 2])
        with white_box.canvas.before:
            Color(0.2, 0.25, 0.35, 0.95)
            white_rect = Rectangle()
        white_box.bind(
            pos=lambda instance, value, r=white_rect: setattr(r, "pos", instance.pos),
            size=lambda instance, value, r=white_rect: setattr(r, "size", instance.size)
        )
        
        white_label = Label(
            text=white_move,
            font_size=dp(16),
            color=(0.95, 0.95, 1, 1),
            bold=True
        )
        white_box.add_widget(white_label)
        move_row.add_widget(white_box)

        # Schwarzer Zug Box (falls vorhanden)
        if black_move:
            black_box = BoxLayout(size_hint_x=0.41, padding=[6, 2])
            with black_box.canvas.before:
                Color(0.15, 0.18, 0.25, 0.95)
                black_rect = Rectangle()
            black_box.bind(
                pos=lambda instance, value, r=black_rect: setattr(r, "pos", instance.pos),
                size=lambda instance, value, r=black_rect: setattr(r, "size", instance.size)
            )
            
            black_label = Label(
                text=black_move,
                font_size=dp(16),
                color=(0.85, 0.85, 0.9, 1)
            )
            black_box.add_widget(black_label)
            move_row.add_widget(black_box)
        else:
            # Leere Box wenn nur weißer Zug vorhanden
            move_row.add_widget(Widget(size_hint_x=0.41))

        container.add_widget(move_row)


class StartMenuScreen(ScreenBackgroundMixin, PanelMixin, Screen):
    """Start-Menü mit New Game, Settings, Quit Buttons."""

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)

        main_layout = BoxLayout(orientation="vertical", padding=[150, 100, 150, 100], spacing=30)
        panel = BoxLayout(orientation="vertical", spacing=20)

        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()

        panel.bind(pos=self._update_panel, size=self._update_panel)

        title_box = BoxLayout(orientation="vertical", size_hint=(1, 0.2), padding=[0, 20, 0, 10])
        title = Label(text="SCHACH", font_size="48sp", size_hint=(1, 1), bold=True, color=(0.95, 0.95, 1, 1))
        title_box.add_widget(title)
        panel.add_widget(title_box)

        separator = Widget(size_hint=(1, 0.02))
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        panel.add_widget(separator)

        button_container = BoxLayout(orientation="vertical", spacing=20, size_hint=(1, 0.68), padding=[80, 20, 80, 20])

        new_game_btn = Button(text="Neues Spiel", font_size="26sp", size_hint=(1, 0.33), background_color=(0.2, 0.7, 0.3, 1), bold=True)
        new_game_btn.bind(on_press=self.start_game)
        button_container.add_widget(new_game_btn)

        stats_btn = Button(text="Statistiken", font_size="26sp", size_hint=(1, 0.33), background_color=(0.3, 0.4, 0.7, 1), bold=True)
        stats_btn.bind(on_press=self.open_stats)
        button_container.add_widget(stats_btn)

        quit_btn = Button(text="Beenden", font_size="26sp", size_hint=(1, 0.33), background_color=(0.7, 0.2, 0.2, 1), bold=True)
        quit_btn.bind(on_press=self.quit_app)
        button_container.add_widget(quit_btn)

        panel.add_widget(button_container)
        main_layout.add_widget(panel)
        self.add_widget(main_layout)

    def start_game(self, instance):
        if self.controller:
            self.controller.go_to_player_selection()
        else:
            self.manager.current = "player_selection"

    def open_stats(self, instance):
        if self.controller:
            self.controller.go_to_stats_menu()
        else:
            self.manager.current = "stats_menu"

    def quit_app(self, instance):
        if self.controller:
            self.controller.quit_app()
        else:
            App.get_running_app().stop()


class PlayerSelectionScreen(ScreenBackgroundMixin, PanelMixin, Screen):
    """Screen zur Auswahl/Registrierung beider Spieler."""

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        main_layout = BoxLayout(orientation="vertical", padding=[120, 60, 120, 60], spacing=20)
        panel = BoxLayout(orientation="vertical", spacing=20)
        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        panel.bind(pos=self._update_panel, size=self._update_panel)

        title_box = BoxLayout(orientation="vertical", size_hint=(1, 0.15), padding=[0, 15, 0, 5])
        title = Label(text="SPIELER-ANMELDUNG", font_size="38sp", size_hint=(1, 0.6), bold=True, color=(0.95, 0.95, 1, 1))
        title_box.add_widget(title)

        info_label = Label(text="Benutzernamen eingeben oder neuen Account erstellen", font_size="14sp", size_hint=(1, 0.4), color=(0.7, 0.75, 0.85, 1))
        title_box.add_widget(info_label)
        panel.add_widget(title_box)

        separator = Widget(size_hint=(1, 0.02))
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        panel.add_widget(separator)

        players_container = BoxLayout(orientation="horizontal", spacing=25, size_hint=(1, 0.38), padding=[50, 20, 50, 20])

        white_box = BoxLayout(orientation="vertical", spacing=15)
        white_label = Label(text="WEISS", font_size="22sp", size_hint=(1, None), height=35, bold=True, color=(1, 1, 1, 1))
        white_box.add_widget(white_label)

        self.white_input = TextInput(hint_text="Benutzername", multiline=False, size_hint=(1, None), height=50, font_size="20sp", write_tab=False, text_validate_unfocus=False, background_color=(0.22, 0.24, 0.28, 1), foreground_color=(1, 1, 1, 1), padding=[15, 12])
        self.white_input.bind(text=lambda instance, value: self.limit_name_length(instance, value, 20))  # type: ignore
        white_box.add_widget(self.white_input)
        white_box.add_widget(Widget(size_hint=(1, 1)))
        players_container.add_widget(white_box)

        vsep = Widget(size_hint=(None, 1), width=1)
        with vsep.canvas:
            Color(0.35, 0.37, 0.42, 1)
            self.vsep_rect = Rectangle()
        vsep.bind(pos=self._update_vsep, size=self._update_vsep)
        players_container.add_widget(vsep)

        black_box = BoxLayout(orientation="vertical", spacing=15)
        black_label = Label(text="SCHWARZ", font_size="22sp", size_hint=(1, None), height=35, bold=True, color=(0.85, 0.85, 0.85, 1))
        black_box.add_widget(black_label)

        self.black_input = TextInput(hint_text="Benutzername", multiline=False, size_hint=(1, None), height=50, font_size="20sp", write_tab=False, text_validate_unfocus=False, background_color=(0.22, 0.24, 0.28, 1), foreground_color=(1, 1, 1, 1), padding=[15, 12])
        self.black_input.bind(text=lambda instance, value: self.limit_name_length(instance, value, 20))  # type: ignore
        black_box.add_widget(self.black_input)
        black_box.add_widget(Widget(size_hint=(1, 1)))
        players_container.add_widget(black_box)

        panel.add_widget(players_container)

        timer_sep = Widget(size_hint=(1, None), height=1)
        with timer_sep.canvas:
            Color(0.3, 0.32, 0.37, 1)
            self.timer_sep_rect = Rectangle()
        timer_sep.bind(pos=self._update_timer_sep, size=self._update_timer_sep)
        panel.add_widget(timer_sep)

        timer_box = BoxLayout(orientation="vertical", spacing=0, size_hint=(1, 0.22), padding=[50, 15, 50, 10])

        timer_title = Label(text="TIMER-EINSTELLUNGEN", font_size="16sp", size_hint=(1, None), height=25, bold=True, color=(0.75, 0.8, 0.9, 1))
        timer_box.add_widget(timer_title)

        timer_box.add_widget(Widget(size_hint=(1, None), height=10))

        timer_container = BoxLayout(orientation="horizontal", spacing=20, size_hint=(1, None), height=45)
        timer_container.add_widget(Widget(size_hint=(0.05, 1)))

        from kivy.uix.checkbox import CheckBox

        self.timer_checkbox = CheckBox(size_hint=(None, None), size=(28, 28), active=False)
        self.timer_checkbox.bind(active=self.toggle_timer_input)
        timer_container.add_widget(self.timer_checkbox)

        timer_label = Label(text="Timer aktivieren", size_hint=(None, 1), width=140, font_size="17sp", bold=True, color=(0.9, 0.92, 1, 1), halign="left")
        timer_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        timer_container.add_widget(timer_label)

        timer_container.add_widget(Widget(size_hint=(1, 1)))

        self.time_input = TextInput(text="10", multiline=False, size_hint=(None, None), size=(70, 38), font_size="18sp", input_filter="int", disabled=True, background_color=(0.22, 0.24, 0.28, 1), foreground_color=(1, 1, 1, 1), padding=[12, 8], halign="center")
        timer_container.add_widget(self.time_input)

        time_info = Label(text="Minuten", size_hint=(None, 1), width=80, font_size="16sp", color=(0.75, 0.78, 0.88, 1))
        timer_container.add_widget(time_info)

        timer_container.add_widget(Widget(size_hint=(0.05, 1)))

        timer_box.add_widget(timer_container)
        panel.add_widget(timer_box)

        button_bar = BoxLayout(orientation="horizontal", spacing=25, size_hint=(1, 0.13), padding=[50, 15, 50, 15])
        back_btn = Button(text="Zurück", font_size="22sp", bold=True, background_color=(0.55, 0.3, 0.3, 1), size_hint=(0.4, 1))
        back_btn.bind(on_press=self.go_back)
        button_bar.add_widget(back_btn)
        start_btn = Button(text="Spiel starten", font_size="22sp", bold=True, background_color=(0.2, 0.65, 0.3, 1), size_hint=(0.6, 1))
        start_btn.bind(on_press=self.start_game)
        button_bar.add_widget(start_btn)
        panel.add_widget(button_bar)

        main_layout.add_widget(panel)
        self.add_widget(main_layout)

    def limit_name_length(self, instance, value, max_length):
        if len(value) > max_length:
            instance.text = value[:max_length]

    def toggle_timer_input(self, checkbox, value):
        self.time_input.disabled = not value

    def _update_vsep(self, instance, value):
        margin = instance.height * 0.1
        self.vsep_rect.pos = (instance.x, instance.y + margin)
        self.vsep_rect.size = (instance.width, instance.height * 0.8)

    def _update_timer_sep(self, instance, value):
        margin = instance.width * 0.1
        self.timer_sep_rect.pos = (instance.x + margin, instance.y)
        self.timer_sep_rect.size = (instance.width * 0.8, instance.height)

    def _get_or_create_player(self, username: str):
        if self.controller:
            return self.controller.get_or_create_player(username)
        return None

    def start_game(self, instance):
        white_name = self.white_input.text.strip()
        black_name = self.black_input.text.strip()

        if not white_name and not black_name:
            self._show_popup("Fehler", "Bitte Benutzername für beide Spieler eingeben!")
            return

        if not white_name:
            self._show_popup("Fehler", "Bitte Benutzername für weißen Spieler eingeben!")
            return

        if not black_name:
            self._show_popup("Fehler", "Bitte Benutzername für schwarzen Spieler eingeben!")
            return

        if white_name.lower() == black_name.lower():
            self._show_popup("Fehler", "Bitte zwei verschiedene Spieler eingeben!")
            return

        if len(white_name) < 3 or len(black_name) < 3:
            self._show_popup("Fehler", "Der Benutzername muss mindestens drei Zeichen enthalten!")
            return

        white_player = self._get_or_create_player(white_name), white_name
        black_player = self._get_or_create_player(black_name), black_name

        use_timer = self.timer_checkbox.active
        time_per_player = None
        if use_timer:
            try:
                time_per_player = int(self.time_input.text)
                if time_per_player <= 0:
                    self._show_popup("Fehler", "Bitte positive Zeit eingeben!")
                    return
            except ValueError:
                self._show_popup("Fehler", "Bitte gültige Zahl für Zeit eingeben!")
                return

        if self.controller:
            self.controller.set_players(white_player, black_player, use_timer, time_per_player)
            self.controller.start_new_game()
            self.controller.go_to_game()
        else:
            self.manager.current = "game"

        self.white_input.text = ""
        self.black_input.text = ""
        self.timer_checkbox.active = False
        self.time_input.text = "10"

    def go_back(self, instance):
        if self.controller:
            self.controller.go_to_menu()
        else:
            self.manager.current = "menu"

    def _show_popup(self, title, message):
        popup_layout = BoxLayout(orientation="vertical", padding=10)
        popup_layout.add_widget(Label(text=message))
        close_btn = Button(text="OK", size_hint=(1, 0.3))
        popup_layout.add_widget(close_btn)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.6, 0.4), auto_dismiss=True)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class GameScreen(Screen):
    """Spiel-Screen mit Schachbrett und Pause-Button."""

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        with self.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        main_layout = BoxLayout(orientation="vertical")
        top_bar = BoxLayout(size_hint=(1, 0.08), padding=10, spacing=10)

        pause_btn = Button(text="Pause", size_hint=(0.1, 1), background_color=(0.9, 0.3, 0.3, 1), font_size="16sp")
        pause_btn.bind(on_press=self.show_pause_menu)
        top_bar.add_widget(pause_btn)

        info_container = BoxLayout(size_hint=(0.9, 1), padding=[15, 8])
        with info_container.canvas.before:
            Color(0.4, 0.5, 0.7, 0.9)
            self.info_border_rect = Rectangle()
            Color(0.15, 0.17, 0.22, 0.95)
            self.info_bg_rect = Rectangle()
        info_container.bind(pos=self._update_info_bg, size=self._update_info_bg)

        self.info_label = Label(text="[b]WEISS  IST AM ZUG[/b]", size_hint=(1, 1), font_size="24sp", markup=True, color=(1, 1, 1, 1))
        info_container.add_widget(self.info_label)
        top_bar.add_widget(info_container)

        main_layout.add_widget(top_bar)

        game_layout = BoxLayout(orientation="horizontal", padding=[20, 10, 20, 10], spacing=15)

        self.board_container = BoxLayout(size_hint_x=0.65, orientation="vertical")
        self.board_container.add_widget(Widget(size_hint_y=0.05))

        h_container = BoxLayout(orientation="horizontal", size_hint_y=0.9)
        h_container.add_widget(Widget())

        self.board = ChessBoard(size_hint=(None, None))
        h_container.add_widget(self.board)

        h_container.add_widget(Widget())

        self.board_container.add_widget(h_container)
        self.board_container.add_widget(Widget(size_hint_y=0.05))
        self.board_container.bind(size=self._update_board_size)

        game_layout.add_widget(self.board_container)

        right_panel = BoxLayout(orientation="vertical", size_hint_x=0.35, spacing=10)

        timer_box = BoxLayout(orientation="vertical", size_hint=(1, 0.35), spacing=5)

        timer_title = Label(text="Timer", font_size="20sp", size_hint=(1, 0.2), bold=True)
        timer_box.add_widget(timer_title)

        white_timer_box = BoxLayout(orientation="horizontal", size_hint=(1, 0.35), padding=[10, 5])
        self.white_timer_label = Label(text="Weiß: --:--", font_size=dp(22), size_hint=(0.7, 1), halign="left")
        Window.bind(size=self._update_font_sizes)
        self.white_timer_label.bind(size=self.white_timer_label.setter("text_size"))
        white_timer_box.add_widget(self.white_timer_label)

        with white_timer_box.canvas.before:
            Color(0.2, 0.3, 0.2, 1)
            self.white_timer_bg = Rectangle()
        white_timer_box.bind(pos=self._update_white_timer_bg, size=self._update_white_timer_bg)

        timer_box.add_widget(white_timer_box)

        black_timer_box = BoxLayout(orientation="horizontal", size_hint=(1, 0.35), padding=[10, 5])
        self.black_timer_label = Label(text="Schwarz: --:--", font_size=dp(22), size_hint=(0.7, 1), halign="left")
        self.black_timer_label.bind(size=self.black_timer_label.setter("text_size"))
        black_timer_box.add_widget(self.black_timer_label)

        with black_timer_box.canvas.before:
            Color(0.2, 0.2, 0.3, 1)
            self.black_timer_bg = Rectangle()
        black_timer_box.bind(pos=self._update_black_timer_bg, size=self._update_black_timer_bg)

        timer_box.add_widget(black_timer_box)
        right_panel.add_widget(timer_box)

        separator = Widget(size_hint=(1, 0.02))
        right_panel.add_widget(separator)

        history_box = BoxLayout(orientation="vertical", size_hint=(1, 0.48), spacing=8, padding=[10, 10])
        with history_box.canvas.before:
            Color(0.3, 0.4, 0.6, 0.8)
            self.history_border_rect = Rectangle()
            Color(0.15, 0.18, 0.22, 0.9)
            self.history_bg_rect = Rectangle()
        history_box.bind(pos=self._update_history_box, size=self._update_history_box)

        history_title = Label(text="ZUGHISTORIE", font_size="20sp", size_hint=(1, None), height=30, bold=True, color=(0.9, 0.92, 1, 1))
        history_box.add_widget(history_title)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)

        self.history_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=3, padding=[5, 5])
        self.history_container.bind(minimum_height=self.history_container.setter("height"))

        scroll.add_widget(self.history_container)
        history_box.add_widget(scroll)

        right_panel.add_widget(history_box)
        
        # Remis-Button unter der Zughistorie
        draw_button = Button(
            text="Remis anbieten",
            size_hint=(1, 0.08),
            background_color=(0.9, 0.3, 0.3, 1),
            font_size="18sp",
            bold=True
        )
        draw_button.bind(on_press=self.request_draw)
        right_panel.add_widget(draw_button)
        
        game_layout.add_widget(right_panel)
        main_layout.add_widget(game_layout)

        self.add_widget(main_layout)

        self.white_player = None
        self.black_player = None
        self.use_timer = False
        self.time_per_player = None

        if self.controller:
            self.controller.set_board_widget(self.board)
            self.controller.set_game_screen(self)
            self.board.set_controller(self.controller)

    def _update_info_bg(self, instance, value):
        border_width = 3
        self.info_border_rect.pos = instance.pos
        self.info_border_rect.size = instance.size
        self.info_bg_rect.pos = (instance.x + border_width, instance.y + border_width)
        self.info_bg_rect.size = (instance.width - 2 * border_width, instance.height - 2 * border_width)

    def _update_history_box(self, instance, value):
        border_width = 2
        self.history_border_rect.pos = instance.pos
        self.history_border_rect.size = instance.size
        self.history_bg_rect.pos = (instance.x + border_width, instance.y + border_width)
        self.history_bg_rect.size = (instance.width - 2 * border_width, instance.height - 2 * border_width)

    def _update_white_timer_bg(self, instance, value):
        self.white_timer_bg.pos = instance.pos
        self.white_timer_bg.size = instance.size

    def _update_black_timer_bg(self, instance, value):
        self.black_timer_bg.pos = instance.pos
        self.black_timer_bg.size = instance.size

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_board_size(self, instance, value):
        size = min(self.board_container.width * 0.9, self.board_container.height * 0.9)
        self.board.width = size
        self.board.height = size

    def set_players(self, white_player, black_player, use_timer=False, time_per_player=None):
        self.white_player = white_player
        self.black_player = black_player
        self.use_timer = use_timer
        self.time_per_player = time_per_player

        self.info_label.text = f"{white_player[1]} (Weiß) vs {black_player[1]} (Schwarz)"

        white_name = white_player[1] if isinstance(white_player, tuple) else white_player.get("username", "Weiß")
        black_name = black_player[1] if isinstance(black_player, tuple) else black_player.get("username", "Schwarz")

        if use_timer and time_per_player:
            # Countdown-Modus
            minutes = time_per_player
            self.white_timer_label.text = f"{white_name}: {minutes:02d}:00"
            self.black_timer_label.text = f"{black_name}: {minutes:02d}:00"
        else:
            # Stopwatch-Modus (beginnt bei 00:00)
            self.white_timer_label.text = f"{white_name}: 00:00"
            self.black_timer_label.text = f"{black_name}: 00:00"

    def _update_font_sizes(self, instance, size):
        base_size = min(size[0], size[1])
        multiplier = base_size / 800

        timer_size = max(18, min(32, int(22 * multiplier)))
        self.white_timer_label.font_size = dp(timer_size)
        self.black_timer_label.font_size = dp(timer_size)

    def update_turn_info(self, current_turn):
        if current_turn == "white":
            self.info_label.text = "[b][color=FFFFFF]WEISS IST AM ZUG[/color][/b]"
        else:
            self.info_label.text = "[b][color=FFFFFF]SCHWARZ IST AM ZUG[/color][/b]"

    def update_move_history(self, move_history):
        # Konvertiere Move-Objekte zu Notationen
        move_notations = [self.controller.get_move_notation(move) for move in move_history]
        # Verwende gemeinsame Hilfsfunktion
        create_move_history_display(self.history_container, move_notations)

    def show_pause_menu(self, instance):
        if self.controller:
            self.controller.go_to_pause_menu()
        else:
            self.manager.current = "pause"

    def show_promotion_popup(self, color, callback):
        popup = PromotionPopup(color, callback)
        popup.open()

    def show_game_over_popup(self, result_type, winner, controller):
        popup = GameOverPopup(result_type, winner, controller, self.white_player, self.black_player)
        popup.open()

    def request_draw(self, instance):
        """Öffnet Remis-Bestätigungs-Popup."""
        if self.controller:
            self.controller.request_draw()
    
    def show_draw_confirm_popup(self):
        """Zeigt das Remis-Bestätigungs-Popup an."""
        popup = RemisConfirmPopup(controller=self.controller)
        popup.open()

    def request_draw(self, instance):
        """Öffnet Remis-Bestätigungs-Popup."""
        if self.controller:
            self.controller.request_draw()
    
    def show_draw_confirm_popup(self):
        """Zeigt das Remis-Bestätigungs-Popup an."""
        popup = RemisConfirmPopup(controller=self.controller)
        popup.open()

    def show_time_up_popup(self, winner_color, controller):
        from kivy.uix.popup import Popup

        if winner_color == "white":
            if self.white_player:
                winner_name = self.white_player[1] if isinstance(self.white_player, tuple) else self.white_player.get("username", "Weiß")
            else:
                winner_name = "Weiß"
            if self.black_player:
                loser_name = self.black_player[1] if isinstance(self.black_player, tuple) else self.black_player.get("username", "Schwarz")
            else:
                loser_name = "Schwarz"
        else:
            if self.black_player:
                winner_name = self.black_player[1] if isinstance(self.black_player, tuple) else self.black_player.get("username", "Schwarz")
            else:
                winner_name = "Schwarz"
            if self.white_player:
                loser_name = self.white_player[1] if isinstance(self.white_player, tuple) else self.white_player.get("username", "Weiß")
            else:
                loser_name = "Weiß"

        content = BoxLayout(orientation="vertical", padding=20, spacing=15)

        title_label = Label(text="ZEIT ABGELAUFEN!", font_size="32sp", bold=True, size_hint=(1, 0.25), color=(1, 0.3, 0.3, 1))
        content.add_widget(title_label)

        message_label = Label(text=f"{loser_name} hat keine Zeit mehr!\n\n{winner_name} gewinnt!", font_size="24sp", size_hint=(1, 0.4), halign="center")
        message_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        content.add_widget(message_label)

        button_box = BoxLayout(orientation="horizontal", spacing=15, size_hint=(1, 0.35))

        menu_btn = Button(text="Hauptmenü", font_size="22sp", background_color=(0.3, 0.4, 0.7, 1), bold=True)
        button_box.add_widget(menu_btn)

        restart_btn = Button(text="Neu starten", font_size="22sp", background_color=(0.2, 0.7, 0.3, 1), bold=True)
        button_box.add_widget(restart_btn)

        content.add_widget(button_box)

        popup = Popup(title="", content=content, size_hint=(0.5, 0.5), separator_height=0, auto_dismiss=True)

        menu_btn.bind(on_press=lambda x: (popup.dismiss(), controller.go_to_menu()))
        restart_btn.bind(on_press=lambda x: (popup.dismiss(), controller.restart_game()))

        popup.open()

    def update_timer_display(self, white_time_seconds, black_time_seconds, active_player):
        white_minutes = int(white_time_seconds // 60)
        white_seconds = int(white_time_seconds % 60)
        black_minutes = int(black_time_seconds // 60)
        black_seconds = int(black_time_seconds % 60)

        if self.white_player:
            white_name = self.white_player[1] if isinstance(self.white_player, tuple) else self.white_player.get("username", "Weiß")
        else:
            white_name = "Weiß"

        if self.black_player:
            black_name = self.black_player[1] if isinstance(self.black_player, tuple) else self.black_player.get("username", "Schwarz")
        else:
            black_name = "Schwarz"

        self.white_timer_label.text = f"{white_name}: {white_minutes:02d}:{white_seconds:02d}"
        self.black_timer_label.text = f"{black_name}: {black_minutes:02d}:{black_seconds:02d}"

        # Aktiver Spieler hervorheben
        if active_player == "white":
            with self.white_timer_label.parent.canvas.before:
                self.white_timer_label.parent.canvas.before.clear()
                Color(0.2, 0.5, 0.2, 1)
                self.white_timer_bg = Rectangle(pos=self.white_timer_label.parent.pos, size=self.white_timer_label.parent.size)
            with self.black_timer_label.parent.canvas.before:
                self.black_timer_label.parent.canvas.before.clear()
                Color(0.2, 0.2, 0.3, 1)
                self.black_timer_bg = Rectangle(pos=self.black_timer_label.parent.pos, size=self.black_timer_label.parent.size)
        else:
            with self.black_timer_label.parent.canvas.before:
                self.black_timer_label.parent.canvas.before.clear()
                Color(0.2, 0.5, 0.2, 1)
                self.black_timer_bg = Rectangle(pos=self.black_timer_label.parent.pos, size=self.black_timer_label.parent.size)
            with self.white_timer_label.parent.canvas.before:
                self.white_timer_label.parent.canvas.before.clear()
                Color(0.2, 0.3, 0.2, 1)
                self.white_timer_bg = Rectangle(pos=self.white_timer_label.parent.pos, size=self.white_timer_label.parent.size)

        # Nur im Countdown-Modus (use_timer=True) rot färben bei weniger als 60 Sekunden
        if self.use_timer:
            if white_time_seconds < 60 and active_player == "white":
                with self.white_timer_label.parent.canvas.before:
                    self.white_timer_label.parent.canvas.before.clear()
                    Color(0.7, 0.2, 0.2, 1)
                    self.white_timer_bg = Rectangle(pos=self.white_timer_label.parent.pos, size=self.white_timer_label.parent.size)

            if black_time_seconds < 60 and active_player == "black":
                with self.black_timer_label.parent.canvas.before:
                    self.black_timer_label.parent.canvas.before.clear()
                    Color(0.7, 0.2, 0.2, 1)
                    self.black_timer_bg = Rectangle(pos=self.black_timer_label.parent.pos, size=self.black_timer_label.parent.size)


class StatsMenuScreen(ScreenBackgroundMixin, PanelMixin, Screen):
    """Menü für Statistiken und Historie."""

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        main_layout = BoxLayout(orientation="vertical", padding=[150, 100, 150, 100], spacing=30)
        panel = BoxLayout(orientation="vertical", spacing=20)
        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        panel.bind(pos=self._update_panel, size=self._update_panel)

        title_box = BoxLayout(orientation="vertical", size_hint=(1, 0.2), padding=[0, 20, 0, 10])
        title = Label(text="STATISTIKEN", font_size="48sp", size_hint=(1, 1), bold=True, color=(0.95, 0.95, 1, 1))
        title_box.add_widget(title)
        panel.add_widget(title_box)

        separator = Widget(size_hint=(1, 0.02))
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        panel.add_widget(separator)

        button_container = BoxLayout(orientation="vertical", spacing=20, size_hint=(1, 0.68), padding=[80, 20, 80, 20])

        leaderboard_btn = Button(text="Rangliste", font_size="26sp", size_hint=(1, 0.33), background_color=(0.3, 0.4, 0.7, 1), bold=True)
        leaderboard_btn.bind(on_press=self.show_leaderboard)
        button_container.add_widget(leaderboard_btn)

        history_btn = Button(text="Spielhistorie", font_size="26sp", size_hint=(1, 0.33), background_color=(0.3, 0.5, 0.7, 1), bold=True)
        history_btn.bind(on_press=self.show_game_history)
        button_container.add_widget(history_btn)

        back_btn = Button(text="Zurück", font_size="26sp", size_hint=(1, 0.33), background_color=(0.7, 0.2, 0.2, 1), bold=True)
        back_btn.bind(on_press=self.go_back)
        button_container.add_widget(back_btn)

        panel.add_widget(button_container)
        main_layout.add_widget(panel)
        self.add_widget(main_layout)

    def show_leaderboard(self, instance):
        if self.controller:
            self.controller.go_to_leaderboard()
        else:
            self.manager.current = "leaderboard"

    def show_game_history(self, instance):
        if self.controller:
            self.controller.go_to_game_history()
        else:
            self.manager.current = "game_history"

    def go_back(self, instance):
        if self.controller:
            self.controller.go_to_menu()
        else:
            self.manager.current = "menu"


class LeaderboardScreen(ScreenBackgroundMixin, PanelMixin, Screen):
    """Ranglisten-Anzeige."""

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        main_layout = BoxLayout(orientation="vertical", padding=[100, 50, 100, 50], spacing=20)
        panel = BoxLayout(orientation="vertical", spacing=15, padding=20)
        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        panel.bind(pos=self._update_panel, size=self._update_panel)

        title = Label(text="RANGLISTE", font_size="42sp", size_hint=(1, 0.12), bold=True, color=(0.95, 0.95, 1, 1))
        panel.add_widget(title)

        separator = Widget(size_hint=(1, None), height=2)
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        panel.add_widget(separator)

        header = BoxLayout(orientation="horizontal", size_hint=(1, 0.08), padding=[10, 5])
        header.add_widget(Label(text="Rang", font_size="18sp", bold=True, size_hint=(0.15, 1), color=(0.9, 0.9, 1, 1)))
        header.add_widget(Label(text="Spieler", font_size="18sp", bold=True, size_hint=(0.35, 1), halign="left", color=(0.9, 0.9, 1, 1)))
        header.add_widget(Label(text="Punkte", font_size="18sp", bold=True, size_hint=(0.2, 1), color=(0.9, 0.9, 1, 1)))
        header.add_widget(Label(text="Spiele", font_size="18sp", bold=True, size_hint=(0.15, 1), color=(0.9, 0.9, 1, 1)))
        header.add_widget(Label(text="Siege", font_size="18sp", bold=True, size_hint=(0.15, 1), color=(0.9, 0.9, 1, 1)))

        with header.canvas.before:
            Color(0.2, 0.25, 0.3, 1)
            self.header_rect = Rectangle()
        header.bind(pos=self._update_header_rect, size=self._update_header_rect)

        panel.add_widget(header)

        scroll = ScrollView(size_hint=(1, 0.65))

        self.leaderboard_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=2)
        self.leaderboard_container.bind(minimum_height=self.leaderboard_container.setter("height"))

        scroll.add_widget(self.leaderboard_container)
        panel.add_widget(scroll)

        back_btn = Button(text="Zurück", font_size="22sp", size_hint=(1, 0.1), background_color=(0.6, 0.3, 0.3, 1), bold=True)
        back_btn.bind(on_press=self.go_back)
        panel.add_widget(back_btn)

        main_layout.add_widget(panel)
        self.add_widget(main_layout)

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def on_pre_enter(self):
        self.load_leaderboard()

    def load_leaderboard(self):
        self.leaderboard_container.clear_widgets()

        if not self.controller:
            return

        players = self.controller.get_leaderboard(50)

        if not players:
            empty_label = Label(text="Noch keine Spieler registriert.", font_size="20sp", size_hint_y=None, height=100)
            self.leaderboard_container.add_widget(empty_label)
            return

        for i, player in enumerate(players, 1):
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, padding=[10, 5])

            if i == 1:
                rank_text = "1."
                rank_color = (1, 0.84, 0, 1)
            elif i == 2:
                rank_text = "2."
                rank_color = (0.75, 0.75, 0.75, 1)
            elif i == 3:
                rank_text = "3."
                rank_color = (0.8, 0.5, 0.2, 1)
            else:
                rank_text = f"{i}."
                rank_color = (1, 1, 1, 1)

            rank_label = Label(text=rank_text, font_size="18sp", bold=i <= 3, size_hint=(0.15, 1), color=rank_color)
            row.add_widget(rank_label)

            name_label = Label(text=player["username"], font_size="18sp", bold=i <= 3, size_hint=(0.35, 1), halign="left", text_size=(None, None))
            name_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
            row.add_widget(name_label)

            points_label = Label(text=str(player["points"]), font_size="18sp", size_hint=(0.2, 1), color=(0.3, 1, 0.3, 1) if player["points"] > 0 else (1, 1, 1, 1))
            row.add_widget(points_label)

            games_label = Label(text=str(player["games_played"]), font_size="18sp", size_hint=(0.15, 1))
            row.add_widget(games_label)

            wins_label = Label(text=str(player["games_won"]), font_size="18sp", size_hint=(0.15, 1))
            row.add_widget(wins_label)

            with row.canvas.before:
                if i % 2 == 0:
                    Color(0.15, 0.15, 0.2, 1)
                else:
                    Color(0.1, 0.1, 0.15, 1)
                row_rect = Rectangle()
            row.bind(pos=lambda r, v, rect=row_rect: setattr(rect, "pos", r.pos), size=lambda r, v, rect=row_rect: setattr(rect, "size", r.size))

            self.leaderboard_container.add_widget(row)

    def go_back(self, instance):
        if self.controller:
            self.controller.go_to_stats_menu()
        else:
            self.manager.current = "stats_menu"


class GameHistoryScreen(ScreenBackgroundMixin, PanelMixin, Screen):
    """Spielhistorie-Anzeige."""

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        main_layout = BoxLayout(orientation="vertical", padding=[100, 50, 100, 50], spacing=20)
        panel = BoxLayout(orientation="vertical", spacing=15, padding=20)
        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        panel.bind(pos=self._update_panel, size=self._update_panel)

        title = Label(text="SPIELHISTORIE", font_size="42sp", size_hint=(1, 0.1), bold=True, color=(0.95, 0.95, 1, 1))
        panel.add_widget(title)

        separator = Widget(size_hint=(1, None), height=2)
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        panel.add_widget(separator)

        scroll = ScrollView(size_hint=(1, 0.75))

        self.games_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=5, padding=[5, 5])
        self.games_container.bind(minimum_height=self.games_container.setter("height"))

        scroll.add_widget(self.games_container)
        panel.add_widget(scroll)

        back_btn = Button(text="Zurück", font_size="22sp", size_hint=(1, 0.1), background_color=(0.6, 0.3, 0.3, 1), bold=True)
        back_btn.bind(on_press=self.go_back)
        panel.add_widget(back_btn)

        main_layout.add_widget(panel)
        self.add_widget(main_layout)

    def on_pre_enter(self):
        self.load_game_history()

    def load_game_history(self):
        self.games_container.clear_widgets()

        if not self.controller:
            return

        games = self.controller.get_games_list(limit=50)

        if not games:
            empty_label = Label(text="Noch keine Spiele gespielt.", font_size="20sp", size_hint_y=None, height=100, color=(0.7, 0.7, 0.8, 1))
            self.games_container.add_widget(empty_label)
            return

        for game in games:
            white = self.controller.get_player_by_id(game["white_player_id"])
            black = self.controller.get_player_by_id(game["black_player_id"])

            if not white or not black:
                continue

            if game["result"] == "white_win":
                result_text = f"{white['username']} gewonnen"
                result_color = (0.3, 0.8, 0.3, 1)
            elif game["result"] == "black_win":
                result_text = f"{black['username']} gewonnen"
                result_color = (0.3, 0.8, 0.3, 1)
            elif game["result"] == "draw":
                result_text = "Remis"
                result_color = (0.8, 0.8, 0.3, 1)
            else:
                result_text = "Laufend"
                result_color = (0.6, 0.6, 0.7, 1)

            game_type = "Timer" if game["game_type"] == "timed" else "Ohne Timer"
            start_time = game["start_time"][:16].replace("T", " ")

            game_btn = Button(size_hint_y=None, height=80, background_normal="", background_color=(0.2, 0.22, 0.28, 1))

            btn_layout = BoxLayout(orientation="vertical", padding=[10, 5])

            players_label = Label(text=f"[b]{white['username']}[/b]  vs  [b]{black['username']}[/b]", font_size="18sp", markup=True, size_hint=(1, 0.4), halign="center", valign="middle")
            players_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], s[1])))
            btn_layout.add_widget(players_label)

            info_box = BoxLayout(orientation="horizontal", size_hint=(1, 0.3))
            result_label = Label(text=result_text, font_size="14sp", color=result_color, size_hint=(0.4, 1))
            type_label = Label(text=game_type, font_size="14sp", size_hint=(0.3, 1), color=(0.7, 0.75, 0.8, 1))
            time_label = Label(text=start_time, font_size="12sp", size_hint=(0.3, 1), color=(0.6, 0.65, 0.7, 1))
            info_box.add_widget(result_label)
            info_box.add_widget(type_label)
            info_box.add_widget(time_label)
            btn_layout.add_widget(info_box)

            game_btn.add_widget(btn_layout)

            game_btn.bind(on_press=lambda btn, g=game: self.view_game(g))

            def on_btn_press(instance):
                instance.background_color = (0.25, 0.27, 0.35, 1)

            def on_btn_release(instance):
                instance.background_color = (0.2, 0.22, 0.28, 1)

            game_btn.bind(on_press=on_btn_press)
            game_btn.bind(on_release=lambda btn, g=game: (on_btn_release(btn), self.view_game(g)))

            self.games_container.add_widget(game_btn)

    def view_game(self, game):
        if self.controller:
            self.controller.view_game_replay(game["id"])

    def go_back(self, instance):
        if self.controller:
            self.controller.go_to_stats_menu()
        else:
            self.manager.current = "stats_menu"


class GameReplayScreen(ScreenBackgroundMixin, Screen):
    """Screen zum Durchspielen aufgezeichneter Spiele."""

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.current_move_index = 0
        self.moves = []
        self.game_data = None

        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        main_layout = BoxLayout(orientation="vertical", padding=[20, 20], spacing=15)

        info_box = BoxLayout(orientation="horizontal", size_hint=(1, 0.08), spacing=10)

        self.game_info_label = Label(text="Lade Spiel...", font_size="20sp", size_hint=(0.7, 1), halign="left", valign="middle", markup=True)
        self.game_info_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], s[1])))
        info_box.add_widget(self.game_info_label)

        back_btn = Button(text="Zurück", font_size="18sp", size_hint=(0.3, 1), background_color=(0.6, 0.3, 0.3, 1), bold=True)
        back_btn.bind(on_press=self.go_back)
        info_box.add_widget(back_btn)

        main_layout.add_widget(info_box)

        game_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.82), spacing=15)

        board_container = BoxLayout(orientation="vertical", size_hint=(0.7, 1))
        self.board = ChessBoard(board_array=None)
        self.board.size_hint = (None, None)
        self.board.bind(size=self._update_board_size)
        board_container.bind(size=self._update_board_size)
        board_container.add_widget(Widget())
        board_container.add_widget(self.board)
        board_container.add_widget(Widget())
        game_layout.add_widget(board_container)

        right_panel = BoxLayout(orientation="vertical", size_hint=(0.3, 1), spacing=10)

        move_info_box = BoxLayout(orientation="vertical", size_hint=(1, 0.3), padding=[10, 10])
        with move_info_box.canvas.before:
            Color(0.15, 0.18, 0.22, 0.9)
            self.move_info_bg = Rectangle()
        move_info_box.bind(pos=self._update_move_info_bg, size=self._update_move_info_bg)

        self.move_info_label = Label(text="Zug 0 / 0", font_size="24sp", bold=True, size_hint=(1, 1), color=(0.9, 0.92, 1, 1))
        move_info_box.add_widget(self.move_info_label)
        right_panel.add_widget(move_info_box)

        right_panel.add_widget(Widget(size_hint=(1, 0.1)))

        history_box = BoxLayout(orientation="vertical", size_hint=(1, 0.6), padding=[10, 10])
        with history_box.canvas.before:
            Color(0.15, 0.18, 0.22, 0.9)
            self.history_bg = Rectangle()
        history_box.bind(pos=self._update_history_bg, size=self._update_history_bg)

        history_title = Label(text="ZÜGE", font_size="18sp", size_hint=(1, None), height=30, bold=True, color=(0.9, 0.92, 1, 1))
        history_box.add_widget(history_title)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)

        self.history_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=3, padding=[5, 5])
        self.history_container.bind(minimum_height=self.history_container.setter("height"))

        scroll.add_widget(self.history_container)
        history_box.add_widget(scroll)
        right_panel.add_widget(history_box)

        game_layout.add_widget(right_panel)
        main_layout.add_widget(game_layout)

        control_box = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=10, padding=[100, 0])

        first_btn = Button(text="Anfang", font_size="18sp", background_color=(0.3, 0.4, 0.7, 1), bold=True)
        first_btn.bind(on_press=self.go_to_first)
        control_box.add_widget(first_btn)

        prev_btn = Button(text="Zurueck", font_size="18sp", background_color=(0.3, 0.4, 0.7, 1), bold=True)
        prev_btn.bind(on_press=self.prev_move)
        control_box.add_widget(prev_btn)

        next_btn = Button(text="Vor", font_size="18sp", background_color=(0.3, 0.4, 0.7, 1), bold=True)
        next_btn.bind(on_press=self.next_move)
        control_box.add_widget(next_btn)

        last_btn = Button(text="Ende", font_size="18sp", background_color=(0.3, 0.4, 0.7, 1), bold=True)
        last_btn.bind(on_press=self.go_to_last)
        control_box.add_widget(last_btn)

        main_layout.add_widget(control_box)
        self.add_widget(main_layout)

    def load_game(self, game_id):
        if not self.controller:
            return

        self.game_data, self.moves = self.controller.load_game_for_replay(game_id)

        if not self.game_data:
            self.game_info_label.text = "Fehler beim Laden des Spiels"
            return

        white_player = self.controller.get_player_by_id(self.game_data["white_player_id"])
        black_player = self.controller.get_player_by_id(self.game_data["black_player_id"])

        # Spielergebnis formatieren
        result = self.game_data.get("result", "")
        if result == "white_win":
            result_text = f"[color=4dcc4d]{white_player['username']} gewonnen[/color]"
        elif result == "black_win":
            result_text = f"[color=4dcc4d]{black_player['username']} gewonnen[/color]"
        elif result == "draw":
            result_text = "[color=cccc4d]Remis[/color]"
        else:
            result_text = "[color=9999aa]Laufend[/color]"

        self.game_info_label.text = f"[b]{white_player['username']}[/b] vs [b]{black_player['username']}[/b]\n{result_text}"

        self.current_move_index = 0
        self.show_position()

    def show_position(self):
        if not self.controller:
            return

        board_array = self.controller.get_replay_position(self.current_move_index)

        if board_array is not None:
            self.board.update_board(board_array)

        total_moves = len(self.moves)
        self.move_info_label.text = f"Zug {self.current_move_index} / {total_moves}"

        self.update_history_display()

    def update_history_display(self):
        # Verwende gemeinsame Hilfsfunktion (self.moves sind bereits Strings)
        create_move_history_display(self.history_container, self.moves)

    def go_to_first(self, instance):
        self.current_move_index = 0
        self.show_position()

    def prev_move(self, instance):
        if self.current_move_index > 0:
            self.current_move_index -= 1
            self.show_position()

    def next_move(self, instance):
        if self.current_move_index < len(self.moves):
            self.current_move_index += 1
            self.show_position()

    def go_to_last(self, instance):
        self.current_move_index = len(self.moves)
        self.show_position()

    def go_back(self, instance):
        if self.controller:
            self.controller.go_to_game_history()
        else:
            self.manager.current = "game_history"

    def _update_board_size(self, instance, value):
        if not hasattr(self, "board"):
            return

        if instance == self.board:
            return

        size = min(instance.width * 0.9, instance.height * 0.9) if hasattr(instance, "width") else 400

        if abs(self.board.width - size) > 1:
            self.board.width = size
            self.board.height = size

    def _update_move_info_bg(self, instance, value):
        self.move_info_bg.pos = instance.pos
        self.move_info_bg.size = instance.size

    def _update_history_bg(self, instance, value):
        self.history_bg.pos = instance.pos
        self.history_bg.size = instance.size


class PauseMenuScreen(ScreenBackgroundMixin, PanelMixin, Screen):
    """Pause-Menü mit Resume, Restart, Main Menu."""

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        main_layout = BoxLayout(orientation="vertical", padding=[150, 100, 150, 100], spacing=30)
        panel = BoxLayout(orientation="vertical", spacing=20)

        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        panel.bind(pos=self._update_panel, size=self._update_panel)

        title_box = BoxLayout(orientation="vertical", size_hint=(1, 0.2), padding=[0, 20, 0, 10])
        title = Label(text="PAUSE", font_size="48sp", size_hint=(1, 1), bold=True, color=(0.95, 0.95, 1, 1))
        title_box.add_widget(title)
        panel.add_widget(title_box)

        separator = Widget(size_hint=(1, 0.02))
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        panel.add_widget(separator)

        button_container = BoxLayout(orientation="vertical", spacing=20, size_hint=(1, 0.68), padding=[80, 20, 80, 20])

        resume_btn = Button(text="Weiterspielen", font_size="26sp", size_hint=(1, 0.25), background_color=(0.2, 0.7, 0.3, 1), bold=True)
        resume_btn.bind(on_press=self.resume_game)
        button_container.add_widget(resume_btn)

        restart_btn = Button(text="Neu starten", font_size="26sp", size_hint=(1, 0.25), background_color=(0.8, 0.5, 0.1, 1), bold=True)
        restart_btn.bind(on_press=self.restart_game)
        button_container.add_widget(restart_btn)

        menu_btn = Button(text="Hauptmenü", font_size="26sp", size_hint=(1, 0.25), background_color=(0.3, 0.4, 0.7, 1), bold=True)
        menu_btn.bind(on_press=self.go_to_menu)
        button_container.add_widget(menu_btn)

        quit_btn = Button(text="Beenden", font_size="26sp", size_hint=(1, 0.25), background_color=(0.7, 0.2, 0.2, 1), bold=True)
        quit_btn.bind(on_press=self.quit_app)
        button_container.add_widget(quit_btn)

        panel.add_widget(button_container)

        main_layout.add_widget(panel)
        self.add_widget(main_layout)

    def resume_game(self, instance):
        if self.controller:
            self.controller.go_to_game()
        else:
            self.manager.current = "game"

    def restart_game(self, instance):
        if self.controller:
            self.controller.start_new_game()
            self.controller.go_to_game()
        else:
            self.manager.current = "game"

    def go_to_menu(self, instance):
        if self.controller:
            self.controller.go_to_menu()
        else:
            self.manager.current = "menu"

    def quit_app(self, instance):
        if self.controller:
            self.controller.quit_app()
        else:
            App.get_running_app().stop()


__all__ = [
    "StartMenuScreen",
    "PlayerSelectionScreen",
    "GameScreen",
    "StatsMenuScreen",
    "LeaderboardScreen",
    "GameHistoryScreen",
    "GameReplayScreen",
    "PauseMenuScreen",
]
