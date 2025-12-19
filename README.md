#chessproject

Project/
│
├─ main.py                  # Entry Point, startet GameController / GUI
├─ game_controller.py       # High-Level Spielsteuerung (Player, Engine, GUI)
├─ board.py                 # Board Klasse + MoveStack + UpdateDict
│
├─ pieces.py
│   ├─ piece                # Basisklasse Piece
│   ├─ pawn                 # Unterklasse Pawn
│   ├─ rook                 # Unterklasse Rook
│   ├─ knight               # Unterklasse Knight
│   ├─ bishop               # Unterklasse Bishop
│   ├─ queen                # Unterklasse Queen
│   └─ king                 # Unterklasse King
│
├─ engine/
│   └─ alpha_beta.py        # Alpha-Beta Engine + Bewertungsfunktion + Move Ordering
├─ utils/
│   ├─ hash_utils.py        # Hashing / Transposition Table Helper
│   ├─ evaluation.py        # Bewertungslogik für Board
│   └─ move_ordering.py     # Heuristiken für Move Ordering
├─ tests/
│   ├─ test_pieces.py       # Unit Tests für Piece-Methoden
│   ├─ test_board.py        # Unit Tests für Board / MoveStack
│   └─ test_engine.py       # Unit Tests für Alpha-Beta & Evaluation
└─ gui/
    ├─ pngs                 # Enthält die Grafiken, für die GUI
    └─ kivy_main.py         # Kivy GUI für Spielerinteraktion


Bilder der Spielfiguren stammen von: By Cburnett - Own work, CC BY-SA 3.0, https://commons.wikimedia.org/w/index.php?curid=1499809