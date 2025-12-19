# Kivy Architektur & Design Patterns

Diese Datei erklärt die Architektur der Schach-App und wie Kivy funktioniert.

## 📐 Architektur-Übersicht

```
┌─────────────────────────────────────────────────────┐
│                   ChessApp (Kivy)                   │
│  - Haupteinstieg                                    │
│  - Erstellt ScreenManager                           │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│              ScreenManager (Kivy)                   │
│  - Verwaltet verschiedene Screens                   │
│  - Wechselt zwischen Menüs                          │
└────────────┬────────────────────────────────────────┘
             │
             ├─► StartMenuScreen
             ├─► PlayerSelectionScreen  
             ├─► GameScreen ◄───┐
             ├─► PauseMenuScreen│
             └─► StatsMenuScreen│
                                 │
                    ┌────────────┴────────────┐
                    │   GameController        │
                    │  - Spiellogik           │
                    │  - Verbindet UI+Backend │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   Board (Backend)       │
                    │  - Spielregeln          │
                    │  - Figuren-Logik        │
                    └─────────────────────────┘
```

## 🎨 Kivy Grundkonzepte

### 1. **Widgets - Die Bausteine**

Kivy basiert auf **Widgets** - das sind UI-Elemente wie Buttons, Labels, TextInputs etc.

```python
# Beispiel aus unserem Code:
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

# Ein Button ist ein Widget
pause_btn = Button(
    text='Pause',              # Text im Button
    size_hint=(0.1, 1),        # Größe relativ zum Container (10% Breite, 100% Höhe)
    background_color=(0.8, 0.6, 0.2, 1),  # RGBA Farbe
    font_size='16sp'           # Schriftgröße in scale-independent pixels
)
```

**Wichtige Widget-Typen in unserer App:**
- `BoxLayout` - Ordnet Widgets horizontal/vertikal an
- `GridLayout` - Ordnet Widgets in einem Raster (unser Schachbrett!)
- `Button` - Klickbare Schaltfläche
- `Label` - Textanzeige
- `TextInput` - Texteingabefeld
- `Screen` - Ein ganzer Bildschirm/Menü
- `ScreenManager` - Verwaltet mehrere Screens

### 2. **size_hint - Dynamische Größen**

Kivy verwendet `size_hint` für responsive Layouts:

```python
# size_hint=(x, y)
# x und y sind Werte zwischen 0.0 und 1.0
# Bedeutung: "Nimm X% der verfügbaren Breite/Höhe"

button = Button(size_hint=(1, 0.3))  # 100% Breite, 30% Höhe
label = Label(size_hint=(0.5, 1))    # 50% Breite, 100% Höhe

# size_hint=None bedeutet: Fixe Größe verwenden
board = ChessBoard(size_hint=(None, None), size=(500, 500))
```

### 3. **Layouts - Container für Widgets**

**BoxLayout** - Stapelt Widgets in einer Richtung:
```python
# Vertikal (von oben nach unten)
layout = BoxLayout(orientation='vertical')
layout.add_widget(Label(text='Oben'))
layout.add_widget(Button(text='Mitte'))
layout.add_widget(Label(text='Unten'))

# Horizontal (von links nach rechts)
row = BoxLayout(orientation='horizontal')
row.add_widget(Button(text='Links'))
row.add_widget(Button(text='Rechts'))
```

**GridLayout** - Raster-Layout (unser Schachbrett):
```python
board = GridLayout(cols=10, rows=10)  # 10x10 Raster
# Fügt Widgets automatisch in Zeilen/Spalten ein
for row in range(10):
    for col in range(10):
        board.add_widget(ChessSquare(...))
```

### 4. **Callbacks - Event-Handling**

Kivy nutzt **Callbacks** für Events (Klicks, Größenänderungen etc.):

```python
# Button-Klick
button = Button(text='Klick mich')
button.bind(on_press=self.button_clicked)  # Registriere Callback

def button_clicked(self, instance):
    print(f"Button {instance.text} wurde geklickt!")

# Widget-Größe ändert sich
widget.bind(size=self.on_size_change)

def on_size_change(self, instance, value):
    print(f"Neue Größe: {value}")
```

**In unserem Code:**
```python
# ChessSquare - Bei Klick Callback aufrufen
def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):  # Punkt innerhalb Widget?
        if callable(self.press_callback):
            self.press_callback(self)  # Callback ausführen
            return True
    return super().on_touch_down(touch)
```

### 5. **Screens - Verschiedene Menüs**

`Screen` ist ein Container für einen ganzen Bildschirm:

```python
class StartMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Layout erstellen
        layout = BoxLayout(orientation='vertical')
        
        # Widgets hinzufügen
        layout.add_widget(Label(text='Hauptmenü'))
        start_btn = Button(text='Neues Spiel')
        start_btn.bind(on_press=self.start_game)
        layout.add_widget(start_btn)
        
        self.add_widget(layout)
    
    def start_game(self, instance):
        # Wechsel zum Game-Screen
        self.manager.current = 'game'
```

**ScreenManager** verwaltet mehrere Screens:
```python
sm = ScreenManager()
sm.add_widget(StartMenuScreen(name='menu'))
sm.add_widget(GameScreen(name='game'))
sm.add_widget(PauseMenuScreen(name='pause'))

# Zwischen Screens wechseln:
sm.current = 'game'  # Zeige GameScreen
```

### 6. **Canvas - Zeichnen mit Graphics**

Kivy's `canvas` erlaubt direktes Zeichnen:

```python
with self.canvas.before:  # Zeichne VOR Widgets
    Color(0.9, 0.9, 0.95)  # Hellgrau (RGB + Alpha)
    self.rect = Rectangle()  # Rechteck zeichnen

# Rectangle-Position aktualisieren bei Größenänderung
self.bind(pos=self.update_rect, size=self.update_rect)

def update_rect(self, *args):
    self.rect.pos = self.pos
    self.rect.size = self.size
```

**Unsere Anwendung:**
- Schachfeld-Hintergrund (hell/dunkel)
- Highlights für legale Züge (grüne Punkte)
- Menü-Hintergründe

## 🏗️ Design Patterns in unserer App

### 1. **MVC (Model-View-Controller)**

```
Model      = Board + Pieces        (Spiellogik, Daten)
View       = Kivy Widgets          (Darstellung)
Controller = GameController        (Vermittler)
```

**Warum?**
- Trennung von Logik und Darstellung
- Einfacher zu testen (Backend ohne GUI testbar)
- Wiederverwendbar (gleiche Logik, anderes UI)

### 2. **Observer Pattern**

Der Controller "beobachtet" UI-Events:

```python
# ChessBoard (Observer) meldet Klick an Controller
def _on_square_pressed(self, row, col):
    if hasattr(self, 'controller') and self.controller:
        self.controller.on_square_clicked(row, col)

# GameController (Observable) reagiert
def on_square_clicked(self, row, col):
    # Logik ausführen
    # UI aktualisieren
```

### 3. **Mediator Pattern**

Der GameController ist der **Mediator**:

```
ChessBoard ──┐
             ├──► GameController ──┐
GameScreen ──┘                     ├──► Board (Backend)
                                   └──► Pieces
```

**Vorteile:**
- Widgets kennen sich nicht gegenseitig
- Alle Kommunikation läuft über Controller
- Einfacher zu erweitern

## 🔄 Datenfluss in unserer App

### Spielzug ausführen:

```
1. User klickt auf Schachfeld
   │
   ▼
2. ChessSquare.on_touch_down()
   │
   ▼
3. ChessBoard._on_square_pressed(row, col)
   │
   ▼
4. GameController.on_square_clicked(row, col)
   │
   ├─► Validierung (eigene Farbe? legaler Zug?)
   │
   ├─► Board.squares aktualisieren (Backend)
   │
   ├─► move_history.append() (State)
   │
   └─► UI aktualisieren
       │
       ├─► ChessBoard.update_board()
       ├─► GameScreen.update_turn_info()
       └─► GameScreen.update_move_history()
```

## 🎯 Warum diese Architektur?

### ✅ Vorteile:

1. **Separation of Concerns**
   - UI-Code in kivy_main.py
   - Logik in game_controller.py
   - Spielregeln in board.py + pieces.py

2. **Testbarkeit**
   ```python
   # Backend testen ohne GUI
   controller = GameController()
   controller.on_square_clicked(6, 4)  # e2
   controller.on_square_clicked(4, 4)  # e4
   assert controller.current_turn == 'black'
   ```

3. **Wiederverwendbarkeit**
   - Gleiche GameController-Logik
   - Andere UI (z.B. Web, Terminal)

4. **Wartbarkeit**
   - Änderungen in einem Bereich
   - Andere Bereiche nicht betroffen

5. **Erweiterbarkeit**
   - Neue Features einfach hinzufügen
   - z.B. Undo/Redo Button:
     ```python
     undo_btn.bind(on_press=lambda x: self.game_controller.undo_last_move())
     ```

## 📚 Wichtige Kivy-Konzepte aus unserem Code

### ChessSquare - Custom Widget

```python
class ChessSquare(BoxLayout):
    """Ein einzelnes Schachfeld."""
    
    def __init__(self, light, piece=None, **kwargs):
        super().__init__(**kwargs)
        # Custom Logik hier
    
    def set_piece(self, piece):
        """Update-Methode für Controller"""
        # Widget aktualisieren
```

**Warum Custom Widget?**
- Eigene Logik (Highlights, Klick-Handling)
- Wiederverwendbar (64x auf Schachbrett)
- Kapselt Komplexität

### ChessBoard - GridLayout

```python
class ChessBoard(GridLayout):
    """10×10 Brett (8×8 Felder + Koordinaten)."""
    
    def __init__(self, board_array=None, **kwargs):
        super().__init__(**kwargs)
        self.cols = 10
        self.rows = 10
        # Erstelle 100 Widgets (64 Felder + 36 Labels/Spacer)
```

**Clever:**
- Raster mit Koordinaten (a-h, 1-8)
- Automatisches Layout
- Controller-Integration

### GameScreen - Haupt-Spielbildschirm

```python
class GameScreen(Screen):
    """Spiel-Screen mit Brett + Infos."""
    
    def _init_game_controller(self):
        # Controller erstellen
        self.game_controller = GameController()
        
        # Verbindungen herstellen
        self.game_controller.set_board_widget(self.board)
        self.game_controller.set_game_screen(self)
        self.board.set_controller(self.game_controller)
```

**Controller-Integration:**
1. Controller erstellen
2. Widget-Referenzen setzen
3. Callbacks registrieren
4. Neues Spiel starten

## 🚀 Wie man erweitert

### Neuen Button hinzufügen (z.B. Undo):

```python
# In GameScreen.__init__():
undo_btn = Button(
    text='Zug zurück',
    size_hint=(0.15, 1),
    background_color=(0.8, 0.5, 0.1, 1)
)
undo_btn.bind(on_press=lambda x: self.game_controller.undo_last_move())
top_bar.add_widget(undo_btn)
```

### Neues Feature im Controller:

```python
# In GameController:
def suggest_move(self):
    """KI schlägt Zug vor."""
    # Implementiere Alpha-Beta
    best_move = self.alpha_beta_search()
    
    # Highlight vorgeschlagenen Zug
    if self.board_widget:
        self.board_widget.highlight_suggestion(best_move)
```

### Neuen Screen hinzufügen:

```python
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Layout erstellen
        ...

# In ChessApp.build():
sm.add_widget(SettingsScreen(name='settings'))
```

## 💡 Best Practices

1. **Immer über Controller kommunizieren**
   ```python
   # ❌ Falsch
   self.board.squares[row][col] = piece
   
   # ✅ Richtig
   self.game_controller.on_square_clicked(row, col)
   ```

2. **UI-Updates im Controller**
   ```python
   # Controller updated UI nach Logik
   self._execute_move(from_pos, to_pos)
   self.board_widget.update_board(self.board.squares)
   self.game_screen.update_turn_info(self.current_turn)
   ```

3. **Callbacks für Events**
   ```python
   widget.bind(on_press=self.my_callback)
   ```

4. **size_hint für responsive Layout**
   ```python
   # Flex-Größen
   button = Button(size_hint=(1, 0.3))
   
   # Fixe Größen wenn nötig
   board = ChessBoard(size_hint=(None, None), size=(600, 600))
   ```

## 📖 Zusammenfassung

**Kivy** = Framework für Cross-Platform GUI Apps

**Unsere Architektur:**
- **Frontend (View):** Kivy Widgets (kivy_main.py)
- **Backend (Model):** Board + Pieces (board.py, pieces.py)
- **Vermittler (Controller):** GameController (game_controller.py)

**Key Concepts:**
- Widgets = UI-Bausteine
- Layouts = Container (BoxLayout, GridLayout)
- Screens = Verschiedene Menüs
- Callbacks = Event-Handling
- Canvas = Zeichnen

**Kommunikation:**
User → Widget → Controller → Backend → Controller → Widget → User

Das ist sauberer, wartbarer Code! 🎉
