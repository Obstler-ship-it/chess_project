"""Move Datenstruktur für Schachzüge."""

import json
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pieces import Piece


@dataclass
class Move:
    """Repräsentiert einen Schachzug.
    
    Attributes:
        from_pos: Startposition als (row, col) Tupel
        to_pos: Zielposition als (row, col) Tupel
        piece: Das Piece-Objekt das bewegt wird
        captured: Geschlagene Figur (False wenn keine)
        promotion: Promotionstyp ('queen', 'rook', 'bishop', 'knight' oder None)
        castelling: Das Turm-Objekt bei Rochade (oder None)
        en_passant: True wenn Zug en-passant ist
    """
    from_pos: tuple
    to_pos: tuple
    piece: 'Piece'
    captured: Optional['Piece'] = None
    promotion: Optional[str] = None
    castelling: Optional['Piece'] = None
    en_passant: bool = False
    
    def to_json(self) -> str:
        """
        Serialisiert den Move als JSON-String.
        
        Konvertiert alle Attribute des Zugs in ein Dictionary und dann in JSON.
        Piece-Objekte werden als Dictionary mit Typ und Farbe dargestellt.
        
        Returns:
            JSON-String mit allen Move-Attributen
        """
        move_dict = {
            'from_pos': self.from_pos,
            'to_pos': self.to_pos,
            'piece': {
                'type': self.piece.__class__.__name__,
                'color': self.piece.color,
                'notation': self.piece.notation
            } if self.piece else None,
            'captured': {
                'type': self.captured.__class__.__name__,
                'color': self.captured.color,
                'notation': self.captured.notation
            } if self.captured else None,
            'promotion': self.promotion,
            'castelling': {
                'type': self.castelling.__class__.__name__,
                'color': self.castelling.color,
                'notation': self.castelling.notation
            } if self.castelling else None,
            'en_passant': self.en_passant
        }
        
        return json.dumps(move_dict)
