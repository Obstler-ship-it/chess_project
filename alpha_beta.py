from utils.evaluation import evaluate_position
from utils.move_ordering import order_moves
from utils.hash_utils import TranspositionTable

class AlphaBetaEngine:
    def __init__(self):
        self.tt = TranspositionTable()
        
    def get_best_move(self, board, depth=4):
        # TODO: Implement alpha-beta search
        return None
