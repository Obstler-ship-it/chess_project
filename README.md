#chessproject

Project/
│
├─ main.py                  # Entry Point, startet GameController / GUI
├─ game_controller.py       # High-Level Spielsteuerung (Player, Engine, GUI)
├─ board.py                 # Board Klasse + MoveStack + UpdateDict
├─ pieces/
│   ├─ piece.py             # Basisklasse Piece
│   ├─ pawn.py              # Unterklasse Pawn
│   ├─ rook.py              # Unterklasse Rook
│   ├─ knight.py            # Unterklasse Knight
│   ├─ bishop.py            # Unterklasse Bishop
│   ├─ queen.py             # Unterklasse Queen
│   └─ king.py              # Unterklasse King
├─ engine/
│   └─ alpha_beta.py        # Alpha-Beta Engine + Bewertungsfunktion + Move Ordering
├─ utils/
│   ├─ hash_utils.py        # Hashing / Transposition Table Helper
│   ├─ evaluation.py        # Bewertungslogik für Board
│   └─ move_ordering.py     # Heuristiken für Move Ordering
├─ tests/
│   └─ test_pieces.py       # Unit Tests für Piece-Methoden
│   └─ test_board.py        # Unit Tests für Board / MoveStack
│   └─ test_engine.py       # Unit Tests für Alpha-Beta & Evaluation
└─ gui/
    └─ kivy_main.py         # Kivy GUI für Spielerinteraktion
