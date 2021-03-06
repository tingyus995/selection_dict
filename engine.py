import re

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

from pynput_mouse_listener import PynputMouseListener
from pynput_selection_grabber import PynputSelectionGrabber
from url_resolver import UrlResolver
from word_history import WordHistory


class EngineSignals(QObject):
    selected = Signal(str, int, int)


class Engine:

    def __init__(self) -> None:
        self.signals = EngineSignals()
        self.word_history_model = WordHistory()
        self._mouse_listener = PynputMouseListener(
            on_dbclick=self._handle_mouse_dbclick)
        self._selection_grabber = PynputSelectionGrabber()
        self.filename = "history.txt"

        self.url_resolver = UrlResolver()

        # load history file if there's one
        try:
            self.load_history()
        except FileNotFoundError:
            pass

    def start_listening(self):
        self._mouse_listener.start(wait=False)

    def stop_listening(self):
        self._mouse_listener.stop()

    def save_history(self):
        self.word_history_model.save_data(self.filename)

    def load_history(self):
        self.word_history_model.load_data(self.filename)

    def _handle_mouse_dbclick(self, x: int, y: int):

        selection = self._selection_grabber.grab()
        print(f"selection = {selection}")

        if len(selection) == 0:
            return

        self.word_history_model.add_word(selection)

        url = self.url_resolver.resolve(selection)

        if url is not None:
            self.signals.selected.emit(url, x, y)
