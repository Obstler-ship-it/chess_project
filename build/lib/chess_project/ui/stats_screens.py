"""Stats Screens: StatsMenu, Leaderboard, GameHistory."""

from kivy.graphics import Color, Rectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from .common import ScreenBackgroundMixin, PanelMixin


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

    def _rgb_to_hex(self, rgb_tuple):
        """Konvertiert RGB-Tupel (0-1) zu Hex-String für Markup."""
        r, g, b, a = rgb_tuple
        return f"{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"

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

            # Ergebnis und Ergebnistyp
            result = game.get("result", "")
            result_type = game.get("final_position", "")
            
            if result == "white_win":
                winner_name = white['username']
                if result_type == "checkmate":
                    result_text = f"{winner_name} - Schachmatt"
                elif result_type == "timeover":
                    result_text = f"{winner_name} - Zeit"
                else:
                    result_text = f"{winner_name} gewinnt"
                result_color = (0.3, 0.8, 0.3, 1)
            elif result == "black_win":
                winner_name = black['username']
                if result_type == "checkmate":
                    result_text = f"{winner_name} - Schachmatt"
                elif result_type == "timeover":
                    result_text = f"{winner_name} - Zeit"
                else:
                    result_text = f"{winner_name} gewinnt"
                result_color = (0.3, 0.8, 0.3, 1)
            elif result == "draw":
                if result_type == "Patt":
                    result_text = "Patt"
                elif result_type == "Remis":
                    result_text = "Remis vereinbart"
                else:
                    result_text = "Remis"
                result_color = (0.8, 0.8, 0.3, 1)
            else:
                result_text = "Nicht beendet"
                result_color = (0.6, 0.6, 0.7, 1)

            game_type = "Timer" if game["game_type"] == "timed" else "Ohne Timer"
            start_time = game["start_time"][:16].replace("T", " ")

            # Widget-Container statt Button für bessere Kontrolle
            game_widget = BoxLayout(orientation="vertical", size_hint_y=None, height=110, padding=[10, 8], spacing=6)
            
            # Hintergrund
            with game_widget.canvas.before:
                Color(0.22, 0.24, 0.30, 1)
                game_rect = Rectangle()
            game_widget.bind(
                pos=lambda instance, value, r=game_rect: setattr(r, "pos", instance.pos),
                size=lambda instance, value, r=game_rect: setattr(r, "size", instance.size)
            )

            # Spielernamen
            players_label = Label(
                text=f"[b][color=FFFFFF]{white['username']}[/color][/b]  vs  [b][color=DDDDDD]{black['username']}[/color][/b]", 
                font_size="19sp", 
                markup=True, 
                size_hint=(1, 0.35), 
                halign="center",
                valign="middle"
            )
            players_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], s[1])))
            game_widget.add_widget(players_label)

            # Ergebnis
            result_label = Label(
                text=f"[color={self._rgb_to_hex(result_color)}][b]{result_text}[/b][/color]", 
                font_size="17sp", 
                markup=True,
                size_hint=(1, 0.35),
                halign="center",
                valign="middle"
            )
            result_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], s[1])))
            game_widget.add_widget(result_label)

            # Typ und Zeit
            info_label = Label(
                text=f"[color=AAAAAA]{game_type}  •  {start_time}[/color]",
                font_size="14sp",
                markup=True,
                size_hint=(1, 0.25),
                halign="center",
                valign="middle"
            )
            info_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], s[1])))
            game_widget.add_widget(info_label)

            # Mache das Widget klickbar
            class ClickableBox(ButtonBehavior, BoxLayout):
                pass
            
            clickable_widget = ClickableBox(orientation="vertical", size_hint_y=None, height=110)
            clickable_widget.add_widget(game_widget)
            clickable_widget.bind(on_press=lambda instance, g=game: self.view_game(g))
            
            self.games_container.add_widget(clickable_widget)

    def view_game(self, game):
        if self.controller:
            self.controller.view_game_replay(game["id"])

    def go_back(self, instance):
        if self.controller:
            self.controller.go_to_stats_menu()
        else:
            self.manager.current = "stats_menu"
