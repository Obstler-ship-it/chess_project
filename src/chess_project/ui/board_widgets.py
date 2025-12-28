"""Kivy Widgets für das Schachbrett."""

from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label


class ChessSquare(BoxLayout):
    """Ein einzelnes Schachfeld mit optionaler Figur."""

    def __init__(self, light, piece=None, **kwargs):
        super().__init__(**kwargs)
        self.light = light
        self.piece = piece
        self.press_callback = None
        self.dot = None  # Ellipse highlight for legal move
        self.selection_overlay = None  # Rectangle für ausgewähltes Feld
        self.check_overlay = None  # Rectangle für König im Schach (separater Layer)
        self.check_event = None  # Scheduled event zum Entfernen der Check-Markierung
        self.bind(pos=self.update_rect, size=self.update_rect)

        with self.canvas.before:
            if self.light:
                Color(0.9, 0.9, 0.95)
            else:
                Color(0.45, 0.55, 0.75)
            self.rect = Rectangle()

        if piece:
            self.piece_image = Image(source=piece.get_image_path(), fit_mode="contain")
            self.add_widget(self.piece_image)

    def update_rect(self, *args):
        """Hält Hintergründe und Overlays synchron zur Widget-Größe."""

        self.rect.pos = self.pos
        self.rect.size = self.size
        if self.dot is not None:
            d = min(self.width, self.height) * 0.25
            self.dot.pos = (
                self.x + self.width / 2 - d / 2,
                self.y + self.height / 2 - d / 2,
            )
            self.dot.size = (d, d)
        if self.selection_overlay is not None:
            self.selection_overlay.pos = self.pos
            self.selection_overlay.size = self.size
        if self.check_overlay is not None:
            self.check_overlay.pos = self.pos
            self.check_overlay.size = self.size

    def set_piece(self, piece):
        """Setzt oder aktualisiert die Figur auf diesem Feld."""

        self.clear_widgets()
        self.piece = piece

        if piece:
            self.piece_image = Image(source=piece.get_image_path(), fit_mode="contain")
            self.add_widget(self.piece_image)

    def set_press_callback(self, callback):
        """Setzt Callback, der bei Klick auf das Feld ausgelöst wird."""

        self.press_callback = callback

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if callable(self.press_callback):
                self.press_callback(self)
                return True
        return super().on_touch_down(touch)

    def add_highlight_dot(self, color="gray"):
        """Zeigt einen Punkt auf dem Feld (legal move)."""

        with self.canvas.after:
            if color == "red":
                Color(1, 0, 0, 0.7)
            else:
                Color(0.2, 0.2, 0.2, 0.8)

            d = min(self.width, self.height) * 0.25
            self.dot = Ellipse(
                pos=(self.x + self.width / 2 - d / 2, self.y + self.height / 2 - d / 2),
                size=(d, d),
            )

    def clear_highlight(self):
        """Entfernt Punkt und Selection-Overlay."""

        self.canvas.after.clear()
        self.dot = None
        self.selection_overlay = None

    def add_selection_highlight(self):
        """Markiert dieses Feld als ausgewählt."""

        with self.canvas.after:
            Color(0.5, 0.5, 0.5, 0.3)
            self.selection_overlay = Rectangle(pos=self.pos, size=self.size)

    def add_check_highlight(self):
        """Markiert König im Schach (rot, verschwindet nach 0.8 Sekunden)."""

        from kivy.clock import Clock

        self.remove_check_highlight()

        with self.canvas:
            Color(1, 0, 0, 0.4)
            self.check_overlay = Rectangle(pos=self.pos, size=self.size)

        self.check_event = Clock.schedule_once(lambda dt: self.remove_check_highlight(), 0.8)

    def remove_check_highlight(self):
        """Entfernt Check-Markierung vom König."""

        if self.check_event:
            self.check_event.cancel()
            self.check_event = None

        if self.check_overlay:
            self.canvas.remove(self.check_overlay)
            self.check_overlay = None


class ChessBoard(GridLayout):
    """10x10 Brett mit dünnem Rahmen und Koordinaten."""

    def __init__(self, board_array=None, **kwargs):
        super().__init__(**kwargs)
        self.cols = 10
        self.rows = 10
        self.spacing = 0.2
        self.padding = 0.2
        self.board_array = board_array
        self.board_obj = None
        self.squares = {}
        self.checkmate_position = None

        with self.canvas.before:
            Color(0.35, 0.35, 0.4, 1)
            self.bg_rect = Rectangle()
        self.bind(pos=self._update_bg, size=self._update_bg)

        for row in range(10):
            for col in range(10):
                if (row == 0 or row == 9) and (col == 0 or col == 9):
                    self.add_widget(Label(text="", size_hint=(None, None), size=(20, 20)))
                    continue

                if row == 0 and 1 <= col <= 8:
                    letter = chr(ord("a") + (col - 1))
                    lbl = Label(text=letter, font_size=13, size_hint=(None, None), size=(25, 25), bold=True)
                    self.add_widget(lbl)
                    continue

                if row == 9 and 1 <= col <= 8:
                    letter = chr(ord("a") + (col - 1))
                    lbl = Label(text=letter, font_size=13, size_hint=(None, None), size=(20, 20), bold=True)
                    self.add_widget(lbl)
                    continue

                if col == 0 and 1 <= row <= 8:
                    number = str(9 - row)
                    lbl = Label(text=number, font_size=13, size_hint=(None, None), size=(20, 20), bold=True)
                    self.add_widget(lbl)
                    continue

                if col == 9 and 1 <= row <= 8:
                    self.add_widget(Label(text="", size_hint=(None, None), size=(20, 20)))
                    continue

                board_row = row - 1
                board_col = col - 1

                if 0 <= board_row <= 7 and 0 <= board_col <= 7:
                    is_light = (board_row + board_col) % 2 == 0

                    piece = None
                    if board_array is not None:
                        piece = board_array[board_row, board_col]

                    square = ChessSquare(is_light, piece)
                    self.squares[(board_row, board_col)] = square
                    square.set_press_callback(lambda _sq, r=board_row, c=board_col: self._on_square_pressed(r, c))
                    self.add_widget(square)
                else:
                    self.add_widget(Label(text=""))

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_board(self, board_array, checkmate_position: tuple = None):
        """Aktualisiert das Brett mit einem neuen board_array."""

        self.board_array = board_array
        for (row, col), square in self.squares.items():
            piece = board_array[row, col] if board_array is not None else None
            square.set_piece(piece)

            if checkmate_position is not None and (row, col) == checkmate_position:
                square.add_check_highlight()

    def set_board(self, board_obj):
        """Setzt Referenz auf das Board-Objekt (für legal_moves)."""

        self.board_obj = board_obj

    def set_controller(self, controller):
        """Setzt Referenz auf den GameController."""

        self.controller = controller

    def clear_highlights(self):
        for sq in self.squares.values():
            sq.clear_highlight()

    def _on_square_pressed(self, row, col):
        """Delegiert Klicks an den Controller oder nutzt Fallback."""

        if hasattr(self, "controller") and self.controller:
            self.controller.on_square_clicked(row, col)
        elif self.board_obj is not None:
            piece = self.board_obj.squares[row, col]
            self.clear_highlights()
            if not piece:
                return
            try:
                moves = piece.get_legal_moves(self.board_obj)
            except Exception:
                moves = []
            for mv in moves:
                if isinstance(mv, (tuple, list)) and len(mv) == 2:
                    r, c = mv
                    if (r, c) in self.squares:
                        self.squares[(r, c)].add_highlight_dot()


__all__ = ["ChessSquare", "ChessBoard"]
