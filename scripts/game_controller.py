import logging
from board import Board
from engine.alpha_beta import AlphaBetaEngine

class GameController:
    def __init__(self):
        self.board = Board()
        self.engine = AlphaBetaEngine()
        
    def run(self):
        logging.info("Starting chess game")
        self.board.print_board()
        # TODO: Implement game loop with GUI
