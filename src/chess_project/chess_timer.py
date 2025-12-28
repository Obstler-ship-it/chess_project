"""
Chess Timer - Schachuhr für das Schachspiel.

Verwaltet die Zeit für beide Spieler mit:
- Countdown-Timer pro Spieler
- Automatischer Wechsel zwischen Spielern
- Pause/Resume-Funktionalität
- Callback bei Zeitablauf
"""

from kivy.clock import Clock


class ChessTimer:
    """
    Schachuhr für zwei Spieler.
    
    Jeder Spieler hat eine festgelegte Zeit. Die Uhr läuft für den
    aktiven Spieler und stoppt, wenn der Zug beendet wird.
    """
    
    def __init__(self, time_per_player_minutes, on_time_up_callback=None, stopwatch_mode=False):
        """
        Initialisiert die Schachuhr.
        
        Args:
            time_per_player_minutes: Zeit pro Spieler in Minuten (int) - nur für Countdown
            on_time_up_callback: Funktion die aufgerufen wird wenn Zeit abläuft
                                 Parameter: color ('white' oder 'black')
            stopwatch_mode: Wenn True, zählt die Zeit hoch statt runter (Stoppuhr)
        """
        self.stopwatch_mode = stopwatch_mode
        
        if stopwatch_mode:
            # Stoppuhr-Modus: Zeit beginnt bei 0 und zählt hoch
            self.white_time = 0
            self.black_time = 0
            self.initial_time = 0
        else:
            # Countdown-Modus: Zeit in Sekunden speichern
            self.white_time = time_per_player_minutes * 60
            self.black_time = time_per_player_minutes * 60
            # Original-Zeit für Reset
            self.initial_time = time_per_player_minutes * 60
        
        # Zustand
        self.current_player = 'white'  # Wer ist gerade am Zug
        self.is_running = False
        self.is_paused = False
        
        # Callback bei Zeitablauf
        self.on_time_up = on_time_up_callback
        
        # Kivy Clock Event für Timer-Update
        self.clock_event = None
        
        # UI-Update Callback (wird vom GameScreen gesetzt)
        self.on_timer_update = None
    
    def start(self):
        """Startet den Timer für den aktuellen Spieler."""
        if self.is_running and not self.is_paused:
            return  # Schon aktiv
        
        self.is_running = True
        self.is_paused = False
        
        # Starte Kivy Clock (wird jede Sekunde aufgerufen)
        if self.clock_event:
            self.clock_event.cancel()
        self.clock_event = Clock.schedule_interval(self._tick, 1.0)
    
    def pause(self):
        """Pausiert den Timer."""
        if not self.is_running or self.is_paused:
            return
        
        self.is_paused = True
        
        # Stoppe Clock
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
    
    def resume(self):
        """Setzt den Timer nach einer Pause fort."""
        if not self.is_running or not self.is_paused:
            return
        
        self.is_paused = False
        
        # Starte Clock wieder
        if self.clock_event:
            self.clock_event.cancel()
        self.clock_event = Clock.schedule_interval(self._tick, 1.0)
    
    def stop(self):
        """Stoppt den Timer komplett."""
        self.is_running = False
        self.is_paused = False
        
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
    
    def switch_player(self):
        """
        Wechselt zum anderen Spieler.
        
        Timer läuft weiter, aber für den anderen Spieler.
        """
        if self.current_player == 'white':
            self.current_player = 'black'
        else:
            self.current_player = 'white'
        
        # UI aktualisieren
        if self.on_timer_update:
            self.on_timer_update(self.white_time, self.black_time, self.current_player)
    
    def reset(self):
        """Setzt den Timer auf die Anfangszeit zurück."""
        self.stop()
        self.white_time = self.initial_time
        self.black_time = self.initial_time
        self.current_player = 'white'
        
        # UI aktualisieren
        if self.on_timer_update:
            self.on_timer_update(self.white_time, self.black_time, self.current_player)
    
    def _tick(self, dt):
        """
        Wird jede Sekunde aufgerufen (von Kivy Clock).
        
        Reduziert die Zeit des aktuellen Spielers (Countdown) oder
        erhöht sie (Stopwatch).
        """
        if self.is_paused:
            return
        
        if self.stopwatch_mode:
            # Stopwatch-Modus: Zeit hochzählen
            if self.current_player == 'white':
                self.white_time += 1
            else:
                self.black_time += 1
        else:
            # Countdown-Modus: Zeit reduzieren
            if self.current_player == 'white':
                self.white_time -= 1
                if self.white_time <= 0:
                    self.white_time = 0
                    self._time_up('white')
                    return
            else:
                self.black_time -= 1
                if self.black_time <= 0:
                    self.black_time = 0
                    self._time_up('black')
                    return
        
        # UI aktualisieren
        if self.on_timer_update:
            self.on_timer_update(self.white_time, self.black_time, self.current_player)
    
    def _time_up(self, color):
        """
        Wird aufgerufen wenn die Zeit eines Spielers abgelaufen ist.
        
        Args:
            color: 'white' oder 'black'
        """
        self.stop()
        
        # Callback aufrufen
        if self.on_time_up:
            self.on_time_up(color)
    
    def get_time_string(self, seconds):
        """
        Konvertiert Sekunden in MM:SS Format.
        
        Args:
            seconds: Zeit in Sekunden
            
        Returns:
            String im Format "MM:SS"
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def get_white_time_string(self):
        """Gibt die verbleibende Zeit von Weiß als String zurück."""
        return self.get_time_string(self.white_time)
    
    def get_black_time_string(self):
        """Gibt die verbleibende Zeit von Schwarz als String zurück."""
        return self.get_time_string(self.black_time)
