"""
Dieses Modul steuert das Schachspiel zwischen dem Backend (board.py und alpha_beta.py)
 und dem Frontend der GUI (GUI und game.py)
"""

from board import Board

class GameController:
    """ Koordiniert den Ablauf des Schachspiels"""
    def __init__(self):
        self.board = Board()

    def run(self):
        """ Startet die Backendlogik des Schachspiels """
        board = self.board
        board.setup_startpos()
        # TODO: Implement game loop with GUI

    def undo_last_move():
        pass
