"""Game Replay Screen zum Durchspielen aufgezeichneter Spiele."""

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from .board_widgets import ChessBoard
from .common import ScreenBackgroundMixin, create_move_history_display


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

        # Board-Container mit horizontaler und vertikaler Zentrierung
        board_container = BoxLayout(orientation="vertical", size_hint=(0.7, 1))
        vertical_spacer_top = Widget(size_hint=(1, 0.5))
        
        horizontal_container = BoxLayout(orientation="horizontal", size_hint=(1, None))
        horizontal_container.bind(minimum_height=horizontal_container.setter("height"))
        
        horizontal_spacer_left = Widget(size_hint=(0.5, 1))
        self.board = ChessBoard(board_array=None)
        self.board.size_hint = (None, None)
        self.board.bind(size=self._update_board_size)
        horizontal_spacer_right = Widget(size_hint=(0.5, 1))
        
        horizontal_container.add_widget(horizontal_spacer_left)
        horizontal_container.add_widget(self.board)
        horizontal_container.add_widget(horizontal_spacer_right)
        
        vertical_spacer_bottom = Widget(size_hint=(1, 0.5))
        
        board_container.bind(size=self._update_board_size)
        board_container.add_widget(vertical_spacer_top)
        board_container.add_widget(horizontal_container)
        board_container.add_widget(vertical_spacer_bottom)
        game_layout.add_widget(board_container)

        right_panel = BoxLayout(orientation="vertical", size_hint=(0.3, 1), spacing=10)

        move_info_box = BoxLayout(orientation="vertical", size_hint=(1, 0.15), padding=[10, 10])
        with move_info_box.canvas.before:
            Color(0.15, 0.18, 0.22, 0.9)
            self.move_info_bg = Rectangle()
        move_info_box.bind(pos=self._update_move_info_bg, size=self._update_move_info_bg)

        self.move_info_label = Label(text="Zug 0 / 0", font_size="24sp", bold=True, size_hint=(1, 1), color=(0.9, 0.92, 1, 1))
        move_info_box.add_widget(self.move_info_label)
        right_panel.add_widget(move_info_box)

        # Zughistorie
        history_box = BoxLayout(orientation="vertical", size_hint=(1, 0.5), spacing=8, padding=[10, 10])
        with history_box.canvas.before:
            Color(0.3, 0.4, 0.6, 0.8)
            self.history_border_rect = Rectangle()
            Color(0.15, 0.18, 0.22, 0.9)
            self.history_bg_rect = Rectangle()
        history_box.bind(pos=self._update_history_bg, size=self._update_history_bg)

        history_title = Label(text="ZUGHISTORIE", font_size="20sp", size_hint=(1, None), height=30, bold=True, color=(0.9, 0.92, 1, 1))
        history_box.add_widget(history_title)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)

        self.history_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=3, padding=[5, 5])
        self.history_container.bind(minimum_height=self.history_container.setter("height"))

        scroll.add_widget(self.history_container)
        history_box.add_widget(scroll)

        right_panel.add_widget(history_box)

        # Steuerungsbuttons
        controls_box = BoxLayout(orientation="vertical", size_hint=(1, 0.35), spacing=10, padding=[10, 10])
        
        row1 = BoxLayout(orientation="horizontal", size_hint=(1, 0.33), spacing=10)
        start_btn = Button(text="⏮", font_size="24sp", background_color=(0.3, 0.4, 0.6, 1), bold=True)
        start_btn.bind(on_press=self.go_to_start)
        row1.add_widget(start_btn)
        
        prev_btn = Button(text="◀", font_size="24sp", background_color=(0.3, 0.4, 0.6, 1), bold=True)
        prev_btn.bind(on_press=self.previous_move)
        row1.add_widget(prev_btn)
        
        controls_box.add_widget(row1)
        
        row2 = BoxLayout(orientation="horizontal", size_hint=(1, 0.33), spacing=10)
        next_btn = Button(text="▶", font_size="24sp", background_color=(0.3, 0.4, 0.6, 1), bold=True)
        next_btn.bind(on_press=self.next_move)
        row2.add_widget(next_btn)
        
        end_btn = Button(text="⏭", font_size="24sp", background_color=(0.3, 0.4, 0.6, 1), bold=True)
        end_btn.bind(on_press=self.go_to_end)
        row2.add_widget(end_btn)
        
        controls_box.add_widget(row2)
        
        row3 = BoxLayout(orientation="horizontal", size_hint=(1, 0.33), spacing=10)
        self.autoplay_btn = Button(text="Auto Play", font_size="20sp", background_color=(0.2, 0.6, 0.3, 1), bold=True)
        self.autoplay_btn.bind(on_press=self.toggle_autoplay)
        row3.add_widget(self.autoplay_btn)
        
        controls_box.add_widget(row3)
        
        right_panel.add_widget(controls_box)
        
        game_layout.add_widget(right_panel)
        main_layout.add_widget(game_layout)

        self.add_widget(main_layout)
        
        self.autoplay_active = False
        self.autoplay_event = None

    def _update_board_size(self, instance, value):
        container_size = min(instance.width, instance.height) * 0.9
        self.board.width = container_size
        self.board.height = container_size

    def _update_move_info_bg(self, instance, value):
        self.move_info_bg.pos = instance.pos
        self.move_info_bg.size = instance.size

    def _update_history_bg(self, instance, value):
        border_width = 2
        self.history_border_rect.pos = instance.pos
        self.history_border_rect.size = instance.size
        self.history_bg_rect.pos = (instance.x + border_width, instance.y + border_width)
        self.history_bg_rect.size = (instance.width - 2 * border_width, instance.height - 2 * border_width)

    def load_game(self, game_id):
        if not self.controller:
            return

        self.game_data = self.controller.get_game_by_id(game_id)
        if not self.game_data:
            self.game_info_label.text = "Spiel nicht gefunden"
            return

        white = self.controller.get_player_by_id(self.game_data["white_player_id"])
        black = self.controller.get_player_by_id(self.game_data["black_player_id"])

        if white and black:
            self.game_info_label.text = f"[b]{white['username']}[/b] vs [b]{black['username']}[/b]"

        self.moves = self.controller.get_moves_for_game(game_id)
        self.current_move_index = 0
        
        # Initialisiere Board
        if self.controller.replay_board:
            self.board.update_from_array(self.controller.replay_board.get_board_array())
        
        self.update_display()

    def update_display(self):
        self.move_info_label.text = f"Zug {self.current_move_index} / {len(self.moves)}"
        
        # Update Zughistorie
        move_notations = [self.controller.get_move_notation_from_data(m) for m in self.moves[:self.current_move_index]]
        create_move_history_display(self.history_container, move_notations)

    def go_to_start(self, instance):
        self.stop_autoplay()
        if self.controller:
            self.controller.replay_go_to_start()
            self.current_move_index = 0
            self.board.update_from_array(self.controller.replay_board.get_board_array())
            self.update_display()

    def previous_move(self, instance):
        self.stop_autoplay()
        if self.controller and self.current_move_index > 0:
            self.controller.replay_previous_move()
            self.current_move_index -= 1
            self.board.update_from_array(self.controller.replay_board.get_board_array())
            self.update_display()

    def next_move(self, instance):
        self.stop_autoplay()
        if self.controller and self.current_move_index < len(self.moves):
            self.controller.replay_next_move()
            self.current_move_index += 1
            self.board.update_from_array(self.controller.replay_board.get_board_array())
            self.update_display()

    def go_to_end(self, instance):
        self.stop_autoplay()
        if self.controller:
            while self.current_move_index < len(self.moves):
                self.controller.replay_next_move()
                self.current_move_index += 1
            self.board.update_from_array(self.controller.replay_board.get_board_array())
            self.update_display()

    def toggle_autoplay(self, instance):
        if self.autoplay_active:
            self.stop_autoplay()
        else:
            self.start_autoplay()

    def start_autoplay(self):
        self.autoplay_active = True
        self.autoplay_btn.text = "Stop"
        self.autoplay_btn.background_color = (0.7, 0.2, 0.2, 1)
        self.autoplay_event = Clock.schedule_interval(self.autoplay_step, 1.0)

    def stop_autoplay(self):
        if self.autoplay_event:
            self.autoplay_event.cancel()
            self.autoplay_event = None
        self.autoplay_active = False
        self.autoplay_btn.text = "Auto Play"
        self.autoplay_btn.background_color = (0.2, 0.6, 0.3, 1)

    def autoplay_step(self, dt):
        if self.current_move_index >= len(self.moves):
            self.stop_autoplay()
            return
        self.next_move(None)

    def go_back(self, instance):
        self.stop_autoplay()
        if self.controller:
            self.controller.go_to_game_history()
        else:
            self.manager.current = "game_history"

    def on_pre_leave(self):
        self.stop_autoplay()
