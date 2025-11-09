import logging
from board import Board
from player import HumanPlayer, AIPlayer

class Game:
	def __init__(self):
		self.board = Board()
		# Weiß beginnt
		self.players = [HumanPlayer('white'), AIPlayer('black')]
		self.current = 0

	def play(self, max_moves=20):
		logging.info("Spiel gestartet (max %d Züge als Demo)", max_moves)
		for move_no in range(1, max_moves + 1):
			player = self.players[self.current]
			logging.info("Zug %d: %s am Zug", move_no, player.color)
			self.board.print_board()
			move = player.select_move(self.board)
			if move is None:
				# In diesem Scaffold gibt es noch keine echte Move-Anwendung
				logging.info("Kein Zug ausgewählt (Stub). Wechsel Spieler.")
			else:
				# Hier würde ein Move angewendet werden
				logging.info("Ausgewählter Zug: %s (nicht angewendet in Scaffold)", move)
			self.current = 1 - self.current
		logging.info("Spiel beendet (Demo)")
		self.board.print_board()