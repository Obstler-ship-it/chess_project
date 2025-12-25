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

## Projektstruktur

```
chess_project/
│
├── main.py                  # Python Entry Point
├── kivy_main.py             # Kivy-App und ScreenManager-Aufbau
├── game_controller.py       # Spielsteuerung und Navigation
├── board.py                 # Schachbrett-Logik
├── chess_logic.py           # Regelvalidierung und Zugprüfung
├── chess_timer.py           # Timer-Handling für Blitz/rapid
├── pieces.py                # Spielfiguren (King, Queen, Rook, etc.)
├── move.py                  # Move-Datenstruktur
├── database.py              # Datenbank-Management
├── ui/
│   ├── board_widgets.py     # ChessBoard/ChessSquare Widgets
│   ├── popups.py            # Promotion- & Game-Over-Popups
│   ├── screens.py           # Start/Game/Stats/Replay/Pause Screens
│   └── __init__.py
├── pieces/                  # Figuren-Grafiken (PNG) + KIVY_ARCHITECTURE.md
├── tests/                   # Unit Tests
│   ├── test_board.py        # Tests für Board-Klasse
│   ├── test_pieces.py       # Tests für Figuren
│   ├── test_chess_logic.py  # Tests für Spiellogik
│   └── test_database.py     # Tests für Datenbank
├── class_diagram.puml       # UML-Klassendiagramm
├── sequence_diagram.puml    # UML-Sequenzdiagramm
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

```bash
python main.py
```

### Spielanleitung

1. **Neues Spiel**: "Neues Spiel" im Hauptmenü wählen
2. **Spieler wählen**: Namen für Weiß/Schwarz eingeben; optional Timer aktivieren (Minuten pro Spieler)
3. **Zug ausführen**:
  - Figur anklicken → legale Züge werden markiert
  - Markiertes Zielfeld anklicken, um den Zug auszuführen
4. **Promotion**: Bei Bauernumwandlung erscheint ein Auswahl-Popup
5. **Pause/Statistiken**: Über das Menü pausieren oder Rangliste/Spielhistorie öffnen

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

**Mit Coverage-Report (HTML):**
```bash
pytest tests/ --cov=. --cov-report=html
```
Nach der Ausführung öffnen Sie `htmlcov/index.html` im Browser.

**Mit Coverage-Report (Terminal):**
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

**Nur fehlgeschlagene Tests erneut ausführen:**
```bash
pytest tests/ --lf
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

## UML-Diagramme

Das Projekt enthält zwei UML-Diagramme im PlantUML-Format zur Dokumentation der Architektur:

### 📐 Klassendiagramm ([class_diagram.puml](class_diagram.puml))

Zeigt die gesamte Systemarchitektur:
- **Vererbungshierarchie der Figuren**: Basisklasse `Piece` → `King`, `Queen`, `Rook`, `Bishop`, `Knight`, `Pawn`
- **Hauptklassen**: 
  - `GameController`: Steuerung des Spielablaufs
  - `Board`: Repräsentation des Schachbretts (8x8 NumPy Array)
  - `ChessLogic`: Regelvalidierung und Zugprüfung
  - `DatabaseManager`: Datenbankzugriff (SQLite)
- **UI-Komponenten**: 
  - Screens: `StartScreen`, `GameScreen`, `StatsScreen`, `GameReplayScreen`, `PauseScreen`
  - Widgets: `ChessBoard`, `ChessSquare`, `PromotionPopup`, `GameOverPopup`
- **Beziehungen und Abhängigkeiten**: Assoziationen, Kompositionen und Vererbungen

### 🔄 Sequenzdiagramm ([sequence_diagram.puml](sequence_diagram.puml))

Zeigt den detaillierten Ablauf eines Spielzugs:
1. **Figur-Auswahl**: Spieler klickt auf eine Figur
2. **Zugvalidierung**: ChessLogic prüft legale Züge
3. **Zugausführung**: Board führt Zug aus (inkl. Spezialzüge wie Rochade, En Passant, Promotion)
4. **Board-Aktualisierung**: GUI wird aktualisiert
5. **Datenbankpersistenz**: Zug wird in Datenbank gespeichert
6. **Spielende-Prüfung**: Prüfung auf Schachmatt/Patt

### 🖼️ Diagramme anzeigen

Die `.puml`-Dateien können mit folgenden Tools gerendert werden:

**Online (einfachste Methode):**
- [PlantUML Web Server](http://www.plantuml.com/plantuml/uml/) - Datei hochladen oder Code kopieren

**VS Code:**
- Extension installieren: "PlantUML" von jebbs
- Rechtsklick auf `.puml` Datei → "Preview Current Diagram"
- Oder: `Ctrl+Shift+P` → "PlantUML: Preview Current Diagram"

**IntelliJ IDEA / PyCharm:**
- Plugin installieren: "PlantUML Integration"
- `.puml` Datei öffnen → Vorschau erscheint automatisch

**Kommandozeile:**
```bash
# PlantUML installieren (benötigt Java)
# Debian/Ubuntu:
sudo apt-get install plantuml

# macOS:
brew install plantuml

# Windows: Download von https://plantuml.com/download

# Diagramm generieren (PNG):
plantuml class_diagram.puml
plantuml sequence_diagram.puml

# Diagramm generieren (SVG, bessere Qualität):
plantuml -tsvg class_diagram.puml
```

## Tests

```bash
pytest tests/
```

## Bekannte Einschränkungen / Nicht implementiert

- ⚠️ **Keine KI-Engine** (nur 2-Spieler-Modus)
- ⚠️ **Keine 50-Züge-Regel** (Remis nach 50 Zügen ohne Bauernzug/Schlagen)
- ⚠️ **Keine dreifache Stellungswiederholung** (automatisches Remis)

Diese Features sind bewusst ausgeschlossen, da der Fokus auf der Implementierung der Kernregeln und der GUI liegt.

## Credits

**Figuren-Grafiken**: By Cburnett - Own work, CC BY-SA 3.0  
https://commons.wikimedia.org/w/index.php?curid=1499809

## Lizenz

Dieses Projekt wurde zu Bildungszwecken erstellt.