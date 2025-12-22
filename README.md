# Chess Game

Ein voll funktionsfähiges Schachspiel mit grafischer Benutzeroberfläche, entwickelt in Python mit Kivy.

## Features

- ✅ Vollständige Schachregeln implementiert
  - Alle Figuren mit korrekten Bewegungsregeln
  - Rochade (kurz und lang)
  - En Passant
  - Bauernumwandlung (Promotion)
  - Schach, Schachmatt und Patt-Erkennung
- 🎮 Grafische Benutzeroberfläche (Kivy)
  - Interaktives Schachbrett
  - Drag & Drop Unterstützung
  - Visuelle Anzeige legaler Züge
  - Zughistorie
- 💾 Datenbankverwaltung (SQLite)
  - Spielerverwaltung
  - Spielhistorie
  - Statistiken
- 🏗️ Saubere Architektur
  - MVC-Pattern
  - Objektorientiertes Design
  - Type Hints
  - PEP 8 konform

## Projektstruktur

```
chess_project/
│
├── main.py                  # Entry Point der Anwendung
├── game_controller.py       # Spielsteuerung und Koordination
├── board.py                 # Schachbrett-Logik
├── chess_logic.py           # Regelvalidierung und Zugprüfung
├── pieces.py                # Spielfiguren (King, Queen, Rook, etc.)
├── move.py                  # Move-Datenstruktur
├── database.py              # Datenbank-Management
├── kivy_main.py            # Kivy GUI Implementation
│
├── pieces/                  # Figuren-Grafiken (PNG)
├── tests/                   # Unit Tests
│   ├── test_board.py
│   └── test_pieces.py
│
├── requirements.txt         # Python Dependencies
└── README.md
```

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python Package Manager)

### Setup

1. **Repository klonen**
   ```bash
   git clone <repository-url>
   cd chess_project
   ```

2. **Virtual Environment erstellen (empfohlen)**
   ```bash
   python -m venv .venv
   ```

3. **Virtual Environment aktivieren**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

4. **Dependencies installieren**
   ```bash
   pip install -r requirements.txt
   ```

## Nutzung

### Spiel starten

```bash
python main.py
```

### Spielanleitung

1. **Neues Spiel starten**: Wähle "Neues Spiel" im Hauptmenü
2. **Spieler auswählen**: Gib Namen für Weiß und Schwarz ein
3. **Figur bewegen**: 
   - Klicke auf eine Figur um sie auszuwählen
   - Legale Züge werden hervorgehoben
   - Klicke auf ein markiertes Feld um den Zug auszuführen
4. **Promotion**: Bei Bauernumwandlung erscheint ein Auswahldialog
5. **Pause**: Über das Menü kann das Spiel pausiert werden

## Technische Details

### Architektur

- **MVC-Pattern**: Trennung von Spiellogik, Darstellung und Steuerung
- **Board**: Repräsentation als NumPy 8x8 Array
- **Pieces**: Vererbungshierarchie mit gemeinsamer Basisklasse
- **ChessLogic**: Zentrale Regelvalidierung und Zugprüfung
- **GameController**: Koordiniert Board, Logic und GUI

### Spiellogik

- **Zugvalidierung**: Prüft Regelkonformität jedes Zugs
- **Schach-Erkennung**: Simuliert Züge um König-Gefährdung zu prüfen
- **Rochade**: Vollständige Implementation mit Bedingungsprüfung
- **En Passant**: Korrekte Behandlung mit last_move Tracking
- **Promotion**: Automatische Erkennung mit Auswahl-Dialog

### Datenbank

- **SQLite**: Lokale Datenbank (chess.db)
- **Tabellen**: players, games, moves
- **Features**: Spielerverwaltung, Spielhistorie, Statistiken

## Dependencies

- **NumPy**: Array-Operationen für Board
- **Kivy**: GUI Framework
- **pytest**: Unit Testing

## Tests

```bash
pytest tests/
```

## Bekannte Einschränkungen

- Keine KI-Engine implementiert (nur 2-Spieler-Modus)
- Keine 50-Züge-Regel
- Keine dreifache Stellungswiederholung

## Credits

**Figuren-Grafiken**: By Cburnett - Own work, CC BY-SA 3.0  
https://commons.wikimedia.org/w/index.php?curid=1499809

## Lizenz

Dieses Projekt wurde zu Bildungszwecken erstellt.