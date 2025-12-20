"""
Chess Game - Main Entry Point
Startet die Kivy-Anwendung.
"""

import sys
from pathlib import Path
from kivy_main import ChessApp


# Optional: Projekt-Root zum Python-Path hinzufügen
# Nützlich wenn Module aus Unterordnern importiert werden
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Haupteinstiegspunkt der Anwendung."""
    app = ChessApp()
    app.run()

if __name__ == '__main__':
    main()
