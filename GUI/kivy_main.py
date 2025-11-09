from kivy.app import App
from kivy.uix.widget import Widget

class ChessBoard(Widget):
    pass

class ChessApp(App):
    def build(self):
        return ChessBoard()
