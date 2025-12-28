# Chess Project

Ein voll funktionsfähiges Schachspiel mit grafischer Benutzeroberfläche, entwickelt in Python mit Kivy.

## Features

- ✅ Vollständige Schachregeln implementiert
  - Alle Figuren mit korrekten Bewegungsregeln
  - Rochade (kurz und lang)
  - En Passant
  - Bauernumwandlung (Promotion)
  - Schach, Schachmatt und Patt-Erkennung
- 🎮 Grafische Benutzeroberfläche (Kivy)
  - Interaktives Schachbrett (Klick-zu-Zug)
  - Visuelle Anzeige legaler Züge
  - Zughistorie und Spiel-Replay
  - Timer-Unterstützung (optional)
- 💾 Datenbankverwaltung (SQLite)
  - Spielerverwaltung
  - Spielhistorie mit vollständiger Zugspeicherung
  - Board-State-Serialisierung (JSON) mit Metadaten (Timer, Remis-Angebote)
  - Statistiken und Rangliste
- 🏗️ Saubere Architektur
  - Klare Aufteilung: `game_controller.py` (Steuerung) + `ui/` (Kivy-Screens/Widgets) + `board.py`/`chess_logic.py` (Regeln)
  - Objektorientiertes Design, Type Hints, PEP 8

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python Package Manager)

### Paket-Installation

1. **Repository klonen**
   ```bash
   git clone <repository-url>
   cd chess_project
   ```

2. **Paket installieren**
   ```bash
   pip install .
   ```

   Oder für Entwicklung:
   ```bash
   pip install -e .
   ```

### Manuelle Installation (für Entwicklung)

1. **Repository klonen**
   ```bash
   git clone <repository-url>
   cd chess_project
   ```

2. **Virtual Environment erstellen** (empfohlen)
   ```bash
   python -m venv .venv
   ```

3. **Virtual Environment aktivieren**
   - **Windows** (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **Windows** (CMD):
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```

4. **Dependencies installieren**
   ```bash
   pip install -r requirements.txt
   ```

## Nutzung

### Spiel starten

Nach der Installation kann das Spiel mit dem Befehl `chess` gestartet werden:

```bash
chess
```

### Alternative Startmethoden

- **Direkter Python-Aufruf** (nach manueller Installation):
  ```bash
  python -m chess_project.main
  ```

### Spielanleitung

#### Grundlagen
- **Ziel**: Schachmatt setzen oder Patt erzwingen
- **Züge**: Weiß beginnt, Spieler wechseln ab
- **Schach**: König ist bedroht – muss aus Schach ziehen

#### Spielablauf
1. **Neues Spiel starten**: Hauptmenü → "Neues Spiel"
2. **Spieler einrichten**: Namen eingeben, optional Timer (Minuten pro Spieler)
3. **Zug machen**:
   - Figur anklicken → grüne Punkte zeigen legale Züge
   - Zielfeld anklicken → Zug ausführen
4. **Spezialzüge**:
   - **Rochade**: König und Turm bewegen (wenn möglich)
   - **En Passant**: Bauer schlägt seitlich (unter Bedingungen)
   - **Promotion**: Bauer erreicht letzte Reihe → Figur wählen
5. **Spielende**: Schachmatt, Patt oder Zeitüberschreitung
6. **Extras**: Pause-Menü, Statistiken, Spiel-Replay

#### Timer
- Läuft automatisch nach Zug
- Bei Zeitüberschreitung verliert der Spieler
- Kann im Spiel pausiert werden
- Wird kein Timer ausgewählt, wird die verstrichene Zeit gestoppt

## Projektstruktur

```
chess_project/
│
├── src/
│   └── chess_project/
│       ├── __init__.py
│       ├── main.py                  # Python Entry Point
│       ├── kivy_main.py             # Kivy-App und ScreenManager-Aufbau
│       ├── game_controller.py       # Spielsteuerung und Navigation
│       ├── board.py                 # Schachbrett-Logik
│       ├── chess_logic.py           # Regelvalidierung und Zugprüfung
│       ├── chess_timer.py           # Timer-Handling für Blitz/rapid
│       ├── pieces.py                # Spielfiguren (King, Queen, Rook, etc.)
│       ├── move.py                  # Move-Datenstruktur
│       ├── database.py              # Datenbank-Management
│       ├── ui/
│       │   ├── board_widgets.py     # ChessBoard/ChessSquare Widgets
│       │   ├── popups.py            # Promotion- & Game-Over-Popups
│       │   ├── screens.py           # Start/Game/Stats/Replay/Pause Screens
│       │   └── __init__.py
│       └── pieces/                  # Figuren-Grafiken (PNG) + KIVY_ARCHITECTURE.md
├── tests/                           # Unit Tests
│   ├── test_board.py                # Tests für Board-Klasse
│   ├── test_pieces.py               # Tests für Figuren
│   ├── test_chess_logic.py          # Tests für Spiellogik
│   └── test_database.py             # Tests für Datenbank
├── pyproject.toml                   # Paket-Konfiguration
├── README.md                        # Diese Datei
├── LICENSE                          # BSD-Lizenz
├── class_diagram.puml               # UML-Klassendiagramm
└── sequence_diagram.puml            # UML-Sequenzdiagramm
```

## Datenformatspezifikation

### Board-Serialisierung (JSON)

Das Schachbrett wird als JSON-String gespeichert mit folgendem Format:

```json
[
  {"row": 0, "col": 0, "image_path": "path/to/piece.png"},
  {"row": 0, "col": 1, "image_path": null},
  ...
  {"turn": "white", "white_time": 600, "black_time": 600, "draw_offers": {"white": false, "black": false}}
]
```

- `row`, `col`: Position (0-7)
- `image_path`: Pfad zur Figur-Grafik oder `null` für leeres Feld
- `turn`: Aktueller Spieler ("white" oder "black")
- `white_time`, `black_time`: Verbleibende Zeit in Sekunden
- `draw_offers`: Remis-Angebote pro Spieler

### Datenbank-Schema

- **players**: `id`, `name`, `created_at`
- **games**: `id`, `white_player_id`, `black_player_id`, `result`, `start_time`, `end_time`, `use_timer`, `time_per_player`
- **moves**: `id`, `game_id`, `move_number`, `from_pos`, `to_pos`, `piece`, `captured`, `promotion`, `notation`
- **boards**: `id`, `game_id`, `board_number`, `board_JSON`, `notation`, `white_time`, `black_time`

## Abhängigkeiten

### Laufzeit-Abhängigkeiten
- **numpy>=1.24**: Für das Schachbrett-Array
- **kivy>=2.3.1**: Für die grafische Benutzeroberfläche

### Entwicklungs-Abhängigkeiten
- **pytest>=7.0**: Für Unit-Tests
- **flake8**: Für Code-Style-Überprüfung

## Technische Details

### Architektur

- **MVC-Pattern**: Trennung von Spiellogik, Darstellung und Steuerung
- **Board**: Repräsentation als NumPy 8x8 Array
- **Pieces**: Vererbungshierarchie mit gemeinsamer Basisklasse
- **ChessLogic**: Zentrale Regelvalidierung und Zugprüfung
- **GameController**: Koordiniert Board, Logic und GUI

### Spiellogik

- **Zugvalidierung**: Prüft Regelkonformität jedes Zugs vor Ausführung
- **Schach-Erkennung**: Simuliert Züge, um König-Gefährdung zu prüfen (verhindert illegale Züge)
- **Rochade**: Vollständige Implementation mit allen Bedingungen:
  - König und Turm dürfen noch nicht bewegt worden sein
  - Keine Figuren zwischen König und Turm
  - König darf nicht im Schach stehen
  - König darf nicht durch ein bedrohtes Feld ziehen
  - König darf nicht im Schach landen
- **En Passant**: Korrekte Behandlung mit `last_move` Tracking (Bauernschlagen im Vorbeigehen)
- **Promotion**: Automatische Erkennung mit Auswahl-Dialog (Bauer auf Grundlinie → Dame/Turm/Läufer/Springer)
- **Schachmatt**: König im Schach, keine legalen Züge vorhanden
- **Patt**: König nicht im Schach, aber keine legalen Züge vorhanden (Remis)
- **Remis-Angebot**: Spieler können während des Spiels Remis anbieten, Gegner kann annehmen/ablehnen

### Datenbank

- **SQLite**: Lokale Datenbank (`chess.db`) im Projektverzeichnis
- **Tabellen**:
  - `players`: Spielerverwaltung (ID, Name, Elo, Statistiken)
  - `games`: Spielmetadaten (ID, Spieler-IDs, Datum, Ergebnis, Timer-Einstellungen)
  - `boards`: Vollständige Zughistorie mit Board-States (game_id, board_number, JSON-Serialisierung mit Metadaten)
- **Features**:
  - Spielerverwaltung (Erstellen, Suchen, Aktualisieren)
  - Spielhistorie mit vollständiger Replay-Funktionalität
  - Statistiken (Siege, Niederlagen, Remis, Elo-Rating)
  - Rangliste nach Elo sortiert
- **Board-Serialisierung**: Jeder Board-State wird als JSON mit Metadaten gespeichert:
  - Figurenpositionen (8x8 Array)
  - Aktiver Spieler (`turn`)
  - Timer-Stände (`white_time`, `black_time`)
  - Remis-Angebote (`draw_offers`: `{"white": bool, "black": bool}`)
  - Notation (z.B. "e2-e4", "Rochade kurz", "Remis akzeptiert")

## Dependencies

Das Projekt verwendet folgende Python-Bibliotheken:

- **NumPy** (`numpy`): Effiziente Array-Operationen für das 8x8 Schachbrett
- **Kivy** (`kivy`): Cross-Platform GUI Framework für die grafische Oberfläche
- **pytest** (`pytest`): Unit Testing Framework
- **pytest-cov** (`pytest-cov`): Code Coverage Plugin für pytest

Alle Dependencies sind in [requirements.txt](requirements.txt) definiert und werden mit `pip install -r requirements.txt` installiert.

## Tests

Das Projekt enthält umfangreiche Unit Tests für alle Kernkomponenten.

### Voraussetzungen

pytest muss installiert sein (bereits in requirements.txt enthalten):
```bash
pip install pytest pytest-cov
```

### Test-Struktur

```
tests/
├── test_board.py          # Board-Klasse (Setup, Züge, Spezialzüge)
├── test_pieces.py         # Figuren-Klassen (Bewegungsregeln)
├── test_chess_logic.py    # Spiellogik (Schach, Matt, Rochade, En Passant)
├── test_database.py       # Datenbank-Operationen (CRUD, Statistiken)
└── __init__.py
```

### Tests ausführen

**Alle Tests ausführen:**
```bash
pytest tests/
```

**Mit detaillierter Ausgabe:**
```bash
pytest tests/ -v
```

**Einzelne Test-Datei:**
```bash
pytest tests/test_board.py
pytest tests/test_pieces.py
pytest tests/test_chess_logic.py
pytest tests/test_database.py
```

### Test-Coverage

Die Tests decken folgende Bereiche ab:
- ✅ **Board-Setup und Grundoperationen**
  - Initialisierung des 8x8 Boards
  - Figurenplatzierung
  - Zugausführung und Rückgängigmachen
- ✅ **Alle Figuren-Bewegungsregeln**
  - König (1 Feld in alle Richtungen)
  - Dame (beliebig diagonal/gerade)
  - Turm (beliebig gerade)
  - Läufer (beliebig diagonal)
  - Springer (L-Form)
  - Bauer (vorwärts, Schlagen diagonal)
- ✅ **Spezialzüge**
  - Rochade (kurz/lang, mit allen Bedingungen)
  - En Passant (Bauernschlagen im Vorbeigehen)
  - Promotion (Bauernumwandlung)
- ✅ **Schach-, Schachmatt- und Patt-Erkennung**
  - König im Schach
  - Schachmatt (keine legalen Züge, König im Schach)
  - Patt (keine legalen Züge, König nicht im Schach)
- ✅ **Datenbank-Operationen und Persistenz**
  - CRUD-Operationen (Create, Read, Update, Delete)
  - Spielerverwaltung
  - Spielhistorie
  - Statistiken und Rangliste

## Bekannte Einschränkungen / Nicht implementiert

- ⚠️ **Keine KI-Engine** (nur 2-Spieler-Modus)
- ⚠️ **Keine 50-Züge-Regel** (Remis nach 50 Zügen ohne Bauernzug/Schlagen)
- ⚠️ **Keine dreifache Stellungswiederholung** (automatisches Remis)

Diese Features sind bewusst ausgeschlossen, da der Fokus auf der Implementierung der Kernregeln und der GUI liegt.

## Credits

Dieses Projekt wurde mit Unterstützung von KI-Assistenten entwickelt:

- **Tests**: Geschrieben von Grok (xAI) – umfassende Unit-Test-Suite mit 47 Tests
- **UI-Komponenten**: Große Teile der Kivy-Benutzeroberfläche (Screens, Widgets, Popups) entwickelt von Claude Sonnet (Anthropic)

**Figuren-Grafiken**: By Cburnett - Own work, CC BY-SA 3.0  
https://commons.wikimedia.org/w/index.php?curid=1499809

## Lizenz

Dieses Projekt wurde als Hausarbeit des Moduls **Programmieren II** erstellt.
Außerdem ist dieses Projekt unter der BSD 3-Clause-Lizenz lizensiert. Siehe [LICENSE](LICENSE) für Details.
