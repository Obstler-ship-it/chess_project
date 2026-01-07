"""Popup-Dialoge für Spielende und Bauern-Beförderung."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup


class GameOverPopup(Popup):
    """Popup für Spielende (Checkmate oder Remis)."""

    def __init__(self, result_type, winner=None, controller=None, white_player=None, black_player=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.title = ""
        self.size_hint = (0.5, 0.5)
        self.separator_height = 0
        self.auto_dismiss = True

        content = BoxLayout(orientation="vertical", padding=20, spacing=15)

        if result_type == "checkmate":
            title_text = "SCHACHMATT!"
            title_color = (1, 0.7, 0, 1)
            if winner == "white" and white_player:
                winner_name = white_player[1] if isinstance(white_player, tuple) else white_player.get("username", "Weiß")
            elif winner == "black" and black_player:
                winner_name = black_player[1] if isinstance(black_player, tuple) else black_player.get("username", "Schwarz")
            else:
                winner_name = "Weiß" if winner == "white" else "Schwarz"
            message = f"{winner_name} gewinnt!"
        elif result_type == "draw":
            title_text = "PATT!"
            title_color = (0.7, 0.7, 0.3, 1)
            message = "Unentschieden!"
        elif result_type == "remis":
            title_text = "REMIS!"
            title_color = (0.7, 0.7, 0.3, 1)
            message = "Unentschieden!"
        else:
            raise ValueError("Ungültiger Spielende-Typ für GameOverPopup!")
        
        title_label = Label(text=title_text, font_size="32sp", bold=True, size_hint=(1, 0.25), color=title_color)
        content.add_widget(title_label)

        message_label = Label(text=message, font_size="24sp", size_hint=(1, 0.4), halign="center")
        message_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        content.add_widget(message_label)

        button_box = BoxLayout(orientation="horizontal", spacing=15, size_hint=(1, 0.35))

        menu_btn = Button(text="Hauptmenü", font_size="22sp", background_color=(0.3, 0.4, 0.7, 1), bold=True)
        menu_btn.bind(on_press=lambda x: (self.dismiss(), self.controller.go_to_menu() if self.controller else None))
        button_box.add_widget(menu_btn)

        restart_btn = Button(text="Neu starten", font_size="22sp", background_color=(0.2, 0.7, 0.3, 1), bold=True)
        restart_btn.bind(on_press=lambda x: (self.dismiss(), self.controller.restart_game() if self.controller else None))
        button_box.add_widget(restart_btn)

        content.add_widget(button_box)
        self.content = content


class PromotionPopup(Popup):
    """Popup für Bauern-Promotion (Wahl zwischen Q, R, B, N)."""

    def __init__(self, color, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.color = color

        color_text = "Weißer" if color == "white" else "Schwarzer"
        self.title = "Bauern-Beförderung"
        self.size_hint = (0.6, 0.5)
        self.auto_dismiss = False

        layout = BoxLayout(orientation="vertical", spacing=20, padding=20)

        info_label = Label(
            text=f"{color_text} Bauer erreicht die gegnerische Grundlinie!\nWähle eine neue Figur:",
            size_hint=(1, 0.2),
            font_size="20sp",
            halign="center",
        )
        info_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        layout.add_widget(info_label)

        button_grid = GridLayout(cols=2, spacing=15, size_hint=(1, 0.8))

        queen_btn = Button(text="Dame (Q)", font_size="22sp", background_color=(0.9, 0.7, 0.2, 1), bold=True)
        queen_btn.bind(on_press=lambda x: self.select_piece("Q"))
        button_grid.add_widget(queen_btn)

        rook_btn = Button(text="Turm (R)", font_size="22sp", background_color=(0.3, 0.6, 0.8, 1), bold=True)
        rook_btn.bind(on_press=lambda x: self.select_piece("R"))
        button_grid.add_widget(rook_btn)

        bishop_btn = Button(text="Läufer (B)", font_size="22sp", background_color=(0.6, 0.4, 0.7, 1), bold=True)
        bishop_btn.bind(on_press=lambda x: self.select_piece("B"))
        button_grid.add_widget(bishop_btn)

        knight_btn = Button(text="Springer (N)", font_size="22sp", background_color=(0.4, 0.7, 0.4, 1), bold=True)
        knight_btn.bind(on_press=lambda x: self.select_piece("N"))
        button_grid.add_widget(knight_btn)

        layout.add_widget(button_grid)
        self.content = layout

    def select_piece(self, piece_type):
        """Wird aufgerufen wenn Spieler eine Figur wählt."""

        if self.callback:
            self.callback(piece_type)
        self.dismiss()


class RemisConfirmPopup(Popup):
    """Popup zur Bestätigung eines Remis."""

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.title = ""
        self.size_hint = (0.5, 0.4)
        self.separator_height = 0
        self.auto_dismiss = True

        content = BoxLayout(orientation="vertical", padding=20, spacing=15)

        title_label = Label(
            text="REMIS AKZEPTIEREN?",
            font_size="28sp",
            bold=True,
            size_hint=(1, 0.3),
            color=(0.9, 0.7, 0.3, 1)
        )
        content.add_widget(title_label)

        message_label = Label(
            text="Möchten Sie ein Remis vereinbaren?\nBeide Spieler erhalten +1 Punkt.",
            font_size="20sp",
            size_hint=(1, 0.4),
            halign="center"
        )
        message_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        content.add_widget(message_label)

        button_box = BoxLayout(orientation="horizontal", spacing=15, size_hint=(1, 0.3))

        cancel_btn = Button(
            text="Abbrechen",
            font_size="20sp",
            background_color=(0.6, 0.3, 0.3, 1),
            bold=True
        )
        cancel_btn.bind(
            on_press=lambda x: (
                self.dismiss(),
                self.controller.cancel_draw() if self.controller else None
            )
        )
        button_box.add_widget(cancel_btn)

        confirm_btn = Button(
            text="Remis bestätigen",
            font_size="20sp",
            background_color=(0.2, 0.7, 0.3, 1),
            bold=True
        )
        confirm_btn.bind(
            on_press=lambda x: (
                self.dismiss(),
                self.controller.confirm_draw() if self.controller else None
            )
        )
        button_box.add_widget(confirm_btn)

        content.add_widget(button_box)
        self.content = content


__all__ = ["GameOverPopup", "PromotionPopup", "RemisConfirmPopup"]
