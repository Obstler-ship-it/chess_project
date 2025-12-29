"""Menu Screens: StartMenu, PlayerSelection, PauseMenu."""

from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from .common import ScreenBackgroundMixin, PanelMixin


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

        # Background
        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # Main Layout
        main_layout = BoxLayout(orientation="vertical", padding=[150, 50, 150, 80], spacing=20)
        
        # Title Box (außerhalb des Panels)
        title_box = BoxLayout(orientation="vertical", size_hint=(1, None), height=60, padding=[0, 0, 0, 5])
        title = Label(text="SPIELER-ANMELDUNG", font_size="48sp", size_hint=(1, 1), bold=True, color=(0.95, 0.95, 1, 1))
        title_box.add_widget(title)
        main_layout.add_widget(title_box)

        # Separator (außerhalb des Panels)
        separator_container = BoxLayout(size_hint=(1, None), height=8)
        separator = Widget(size_hint=(1, None), height=2)
        with separator.canvas:
            Color(0.4, 0.4, 0.5, 1)
            self.sep_rect = Rectangle()
        separator.bind(pos=self._update_separator, size=self._update_separator)
        separator_container.add_widget(separator)
        main_layout.add_widget(separator_container)
        
        # Panel (ohne Title und Separator)
        panel = BoxLayout(orientation="vertical", spacing=20)

        with panel.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self.panel_rect = Rectangle()
        panel.bind(pos=self._update_panel, size=self._update_panel)

        # Content Container
        content_container = BoxLayout(orientation="vertical", spacing=15, size_hint=(1, 0.75), padding=[80, 20, 80, 20])

        # Spieler Eingaben - Horizontal Layout
        players_layout = BoxLayout(orientation="horizontal", spacing=40, size_hint=(1, 0.5))
        
        # Weiß Spieler
        white_container = RelativeLayout(size_hint=(0.5, 1))
        white_box = BoxLayout(orientation="vertical", spacing=10, size_hint=(1, None), height=100, pos_hint={'top': 1})
        
        white_label = Label(
            text="WEISS", 
            font_size="24sp", 
            size_hint=(1, None), 
            height=35, 
            bold=True, 
            color=(1, 1, 1, 1)
        )
        white_box.add_widget(white_label)
        
        self.white_input = TextInput(
            hint_text="Benutzername", 
            multiline=False, 
            size_hint=(1, None), 
            height=55, 
            font_size="22sp", 
            write_tab=False,
            background_color=(0.22, 0.24, 0.28, 1), 
            foreground_color=(1, 1, 1, 1), 
            padding=[15, 15]
        )
        self.white_input.bind(text=lambda instance, value: self.limit_name_length(instance, value, 20))
        self.white_input.bind(text=self.on_white_text_change)
        white_box.add_widget(self.white_input)
        white_container.add_widget(white_box)
        
        # Dropdown für Weiß
        self.white_scroll = ScrollView(
            size_hint=(1, None), 
            height=0, 
            do_scroll_x=False,
            pos_hint={'top': 0.38}
        )
        self.white_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=2, padding=5)
        self.white_list.bind(minimum_height=self.white_list.setter('height'))
        self.white_scroll.add_widget(self.white_list)
        white_container.add_widget(self.white_scroll)
        
        players_layout.add_widget(white_container)
        
        # Schwarz Spieler
        black_container = RelativeLayout(size_hint=(0.5, 1))
        black_box = BoxLayout(orientation="vertical", spacing=10, size_hint=(1, None), height=100, pos_hint={'top': 1})
        
        black_label = Label(
            text="SCHWARZ", 
            font_size="24sp", 
            size_hint=(1, None), 
            height=35, 
            bold=True, 
            color=(0.85, 0.85, 0.85, 1)
        )
        black_box.add_widget(black_label)
        
        self.black_input = TextInput(
            hint_text="Benutzername", 
            multiline=False, 
            size_hint=(1, None), 
            height=55, 
            font_size="22sp", 
            write_tab=False,
            background_color=(0.22, 0.24, 0.28, 1), 
            foreground_color=(1, 1, 1, 1), 
            padding=[15, 15]
        )
        self.black_input.bind(text=lambda instance, value: self.limit_name_length(instance, value, 20))
        self.black_input.bind(text=self.on_black_text_change)
        black_box.add_widget(self.black_input)
        black_container.add_widget(black_box)
        
        # Dropdown für Schwarz
        self.black_scroll = ScrollView(
            size_hint=(1, None), 
            height=0, 
            do_scroll_x=False,
            pos_hint={'top': 0.38}
        )
        self.black_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=2, padding=5)
        self.black_list.bind(minimum_height=self.black_list.setter('height'))
        self.black_scroll.add_widget(self.black_list)
        black_container.add_widget(self.black_scroll)
        
        players_layout.add_widget(black_container)
        
        content_container.add_widget(players_layout)

        # Timer Einstellungen
        timer_section = BoxLayout(orientation="vertical", spacing=12, size_hint=(1, 0.25), padding=[0, 25, 0, 0])
        
        timer_controls = BoxLayout(orientation="horizontal", spacing=20, size_hint=(1, None), height=55)
        timer_controls.add_widget(Widget(size_hint=(0.15, 1)))
        
        self.timer_checkbox = CheckBox(size_hint=(None, None), size=(40, 40), active=False)
        self.timer_checkbox.bind(active=self.toggle_timer_input)
        timer_controls.add_widget(self.timer_checkbox)
        
        timer_label = Label(
            text="Timer aktivieren", 
            size_hint=(None, 1), 
            width=180, 
            font_size="20sp", 
            bold=True, 
            color=(0.9, 0.92, 1, 1)
        )
        timer_controls.add_widget(timer_label)
        timer_controls.add_widget(Widget(size_hint=(1, 1)))
        
        self.time_input = TextInput(
            text="10", 
            multiline=False, 
            size_hint=(None, None), 
            size=(90, 50), 
            font_size="22sp", 
            input_filter="int", 
            disabled=True,
            background_color=(0.22, 0.24, 0.28, 1), 
            foreground_color=(1, 1, 1, 1), 
            padding=[15, 12], 
            halign="center"
        )
        self.time_input.bind(text=lambda instance, value: self.limit_name_length(instance, value, 2))
        timer_controls.add_widget(self.time_input)
        
        time_label = Label(
            text="Minuten", 
            size_hint=(None, 1), 
            width=100, 
            font_size="19sp", 
            color=(0.75, 0.78, 0.88, 1)
        )
        timer_controls.add_widget(time_label)
        timer_controls.add_widget(Widget(size_hint=(0.15, 1)))
        
        timer_section.add_widget(timer_controls)
        content_container.add_widget(timer_section)

        panel.add_widget(content_container)

        # Button Bar
        button_bar = BoxLayout(orientation="horizontal", spacing=20, size_hint=(1, 0.25), padding=[80, 15, 80, 15])
        
        back_btn = Button(
            text="Zurück", 
            font_size="26sp", 
            bold=True, 
            background_color=(0.7, 0.2, 0.2, 1), 
            size_hint=(0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        button_bar.add_widget(back_btn)
        
        start_btn = Button(
            text="Spiel starten", 
            font_size="26sp", 
            bold=True, 
            background_color=(0.2, 0.7, 0.3, 1), 
            size_hint=(0.5, 1)
        )
        start_btn.bind(on_press=self.start_game)
        button_bar.add_widget(start_btn)
        
        panel.add_widget(button_bar)

        main_layout.add_widget(panel)
        self.add_widget(main_layout)
        
        # Dropdown-Zustände initialisieren
        self.white_dropdown_open = False
        self.black_dropdown_open = False

    def limit_name_length(self, instance, value, max_length):
        if len(value) > max_length:
            instance.text = value[:max_length]

    def toggle_timer_input(self, checkbox, value):
        self.time_input.disabled = not value
    
    def on_white_text_change(self, instance, value):
        """Zeigt/versteckt die Dropdown-Liste für weiße Spieler."""
        if value:
            self.populate_white_list(value)
            self.white_scroll.height = 120
            self.white_dropdown_open = True
        else:
            self.white_scroll.height = 0
            self.white_dropdown_open = False
    
    def on_black_text_change(self, instance, value):
        """Zeigt/versteckt die Dropdown-Liste für schwarze Spieler."""
        if value:
            self.populate_black_list(value)
            self.black_scroll.height = 120
            self.black_dropdown_open = True
        else:
            self.black_scroll.height = 0
            self.black_dropdown_open = False
    
    def populate_white_list(self, filter_text=""):
        """Füllt die weiße Spielerliste, optional gefiltert."""
        if not self.controller:
            return
        self.white_list.clear_widgets()
        players = self.controller.get_all_players()
        filtered = [p for p in players if filter_text.lower() in p['username'].lower()][:10]
        for player in filtered:
            btn = Button(
                text=player['username'],
                size_hint_y=None,
                height=35,
                background_normal='',
                background_color=(0.28, 0.38, 0.48, 1),
                color=(1, 1, 1, 1),
                font_size="17sp"
            )
            btn.bind(on_press=lambda btn, name=player['username']: self.select_white_player(name))
            self.white_list.add_widget(btn)
    
    def populate_black_list(self, filter_text=""):
        """Füllt die schwarze Spielerliste, optional gefiltert."""
        if not self.controller:
            return
        self.black_list.clear_widgets()
        players = self.controller.get_all_players()
        filtered = [p for p in players if filter_text.lower() in p['username'].lower()][:10]
        for player in filtered:
            btn = Button(
                text=player['username'],
                size_hint_y=None,
                height=35,
                background_normal='',
                background_color=(0.28, 0.38, 0.48, 1),
                color=(1, 1, 1, 1),
                font_size="17sp"
            )
            btn.bind(on_press=lambda btn, name=player['username']: self.select_black_player(name))
            self.black_list.add_widget(btn)
    
    def select_white_player(self, name):
        """Wählt einen Spieler für Weiß aus der Liste aus."""
        self.white_input.text = name
        self.white_scroll.height = 0
        self.white_dropdown_open = False
    
    def select_black_player(self, name):
        """Wählt einen Spieler für Schwarz aus der Liste aus."""
        self.black_input.text = name
        self.black_scroll.height = 0
        self.black_dropdown_open = False

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
