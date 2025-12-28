"""UI Package mit Screens, Widgets und Popups."""

from .board_widgets import ChessBoard, ChessSquare
from .popups import GameOverPopup, PromotionPopup
from .screens import (
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
