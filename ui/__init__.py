"""UI Package mit Screens, Widgets und Popups."""

from ui.board_widgets import ChessBoard, ChessSquare
from ui.popups import GameOverPopup, PromotionPopup
from ui.screens import (
    GameHistoryScreen,
    GameReplayScreen,
    GameScreen,
    LeaderboardScreen,
    PauseMenuScreen,
    PlayerSelectionScreen,
    StartMenuScreen,
    StatsMenuScreen,
)

__all__ = [
    "ChessBoard",
    "ChessSquare",
    "GameOverPopup",
    "PromotionPopup",
    "GameHistoryScreen",
    "GameReplayScreen",
    "GameScreen",
    "LeaderboardScreen",
    "PauseMenuScreen",
    "PlayerSelectionScreen",
    "StartMenuScreen",
    "StatsMenuScreen",
]
