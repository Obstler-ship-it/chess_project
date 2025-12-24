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
        castelling: Das Turm-Objekt bei Rochade (oder None)
        en_passant: True wenn Zug en-passant ist
        time: Optional dictionary mit 'white' und 'black' Zeitstrings im Format "MM:SS"
    """
    from_pos: tuple
    to_pos: tuple
    piece: 'Piece'
    captured: Optional['Piece'] = None
    promotion: Optional[str] = None
    castelling: Optional['Piece'] = None
    en_passant: bool = False
    time: Optional[dict] = None
