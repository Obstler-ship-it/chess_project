"""Move Datenstruktur für Schachzüge."""

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
    """
    from_pos: tuple
    to_pos: tuple
    piece: 'Piece'
    captured: Optional['Piece'] = False
    promotion: Optional[str] = False
