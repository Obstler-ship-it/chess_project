"""Game Screen mit Schachbrett und Timer."""

from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from .board_widgets import ChessBoard
from .common import create_move_history_display
from .popups import GameOverPopup, PromotionPopup, RemisConfirmPopup


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

    def show_time_up_popup(self, winner_color, controller):
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
