"""Gemeinsame Mixins und Hilfsfunktionen für alle Screens."""

from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class ScreenBackgroundMixin:
    """Mixin für gemeinsame Background-Update Methode."""
    
    def update_bg(self, *args):
        """Aktualisiert das Background-Rectangle."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class PanelMixin:
    """Mixin für Panel und Separator Updates."""
    
    def _update_panel(self, instance, value):
        """Aktualisiert das Panel-Rectangle."""
        self.panel_rect.pos = instance.pos
        self.panel_rect.size = instance.size
    
    def _update_separator(self, instance, value):
        """Aktualisiert den Separator mit 20% Margin."""
        margin = instance.width * 0.2
        self.sep_rect.pos = (instance.x + margin, instance.y)
        self.sep_rect.size = (instance.width * 0.6, 2)


def create_move_history_display(container, moves_list):
    """
    Gemeinsame Hilfsfunktion zum Erstellen der Zughistorie-Anzeige.
    
    Args:
        container: BoxLayout Container für die Züge
        moves_list: Liste von Zugnotationen (Strings)
    """
    container.clear_widgets()
    
    if not moves_list:
        empty_label = Label(
            text="Keine Züge",
            font_size=dp(18),
            size_hint_y=None,
            height=40,
            color=(0.6, 0.6, 0.7, 1),
            italic=True
        )
        container.add_widget(empty_label)
        return

    # Gruppiere Züge paarweise (Weiß und Schwarz)
    move_pairs = []
    for i in range(0, len(moves_list), 2):
        white_move = moves_list[i]
        black_move = moves_list[i + 1] if i + 1 < len(moves_list) else None
        move_pairs.append((white_move, black_move))

    for move_num, (white_move, black_move) in enumerate(move_pairs, 1):
        # Container für ein Zugpaar (eine Zeile)
        move_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=35,
            spacing=4,
            padding=[2, 2]
        )

        # Zugnummer Box
        num_box = BoxLayout(size_hint_x=0.18, padding=[4, 2])
        with num_box.canvas.before:
            Color(0.25, 0.3, 0.4, 0.9)
            num_rect = Rectangle()
        num_box.bind(
            pos=lambda instance, value, r=num_rect: setattr(r, "pos", instance.pos),
            size=lambda instance, value, r=num_rect: setattr(r, "size", instance.size)
        )
        
        num_label = Label(
            text=f"{move_num}.",
            font_size=dp(16),
            bold=True,
            color=(0.7, 0.8, 0.95, 1)
        )
        num_box.add_widget(num_label)
        move_row.add_widget(num_box)

        # Weißer Zug Box
        white_box = BoxLayout(size_hint_x=0.41, padding=[6, 2])
        with white_box.canvas.before:
            Color(0.2, 0.25, 0.35, 0.95)
            white_rect = Rectangle()
        white_box.bind(
            pos=lambda instance, value, r=white_rect: setattr(r, "pos", instance.pos),
            size=lambda instance, value, r=white_rect: setattr(r, "size", instance.size)
        )
        
        white_label = Label(
            text=white_move,
            font_size=dp(16),
            color=(0.95, 0.95, 1, 1),
            bold=True
        )
        white_box.add_widget(white_label)
        move_row.add_widget(white_box)

        # Schwarzer Zug Box (falls vorhanden)
        if black_move:
            black_box = BoxLayout(size_hint_x=0.41, padding=[6, 2])
            with black_box.canvas.before:
                Color(0.15, 0.18, 0.25, 0.95)
                black_rect = Rectangle()
            black_box.bind(
                pos=lambda instance, value, r=black_rect: setattr(r, "pos", instance.pos),
                size=lambda instance, value, r=black_rect: setattr(r, "size", instance.size)
            )
            
            black_label = Label(
                text=black_move,
                font_size=dp(16),
                color=(0.85, 0.85, 0.9, 1)
            )
            black_box.add_widget(black_label)
            move_row.add_widget(black_box)
        else:
            # Leere Box wenn nur weißer Zug vorhanden
            move_row.add_widget(Widget(size_hint_x=0.41))

        container.add_widget(move_row)
