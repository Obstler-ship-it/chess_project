"""App-Entry mit ScreenManager-Konfiguration."""

# Kivy Config MUSS vor anderen Kivy-Imports stehen
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from .game_controller import GameController
from .ui.screens import (
    StartMenuScreen,
    PlayerSelectionScreen,
    GameScreen,
    PauseMenuScreen,
    StatsMenuScreen,
    LeaderboardScreen,
    GameHistoryScreen,
    GameReplayScreen,
)


class ChessApp(App):
    """Kivy-App, die alle Screens mit dem GameController verdrahtet."""

    def build(self):
        Window.size = (900, 700)

        screen_manager = ScreenManager()
        self.game_controller = GameController(screen_manager, app=self)

        screen_manager.add_widget(StartMenuScreen(name="menu", controller=self.game_controller))
        screen_manager.add_widget(PlayerSelectionScreen(name="player_selection", controller=self.game_controller))
        screen_manager.add_widget(GameScreen(name="game", controller=self.game_controller))
        screen_manager.add_widget(PauseMenuScreen(name="pause", controller=self.game_controller))
        screen_manager.add_widget(StatsMenuScreen(name="stats_menu", controller=self.game_controller))
        screen_manager.add_widget(LeaderboardScreen(name="leaderboard", controller=self.game_controller))
        screen_manager.add_widget(GameHistoryScreen(name="game_history", controller=self.game_controller))
        screen_manager.add_widget(GameReplayScreen(name="game_replay", controller=self.game_controller))

        return screen_manager


if __name__ == "__main__":
    ChessApp().run()

