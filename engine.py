import re

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

from pynput_mouse_listener import PynputMouseListener
from pynput_selection_grabber import PynputSelectionGrabber

class EngineSignals(QObject):
    selected = pyqtSignal(str, int, int)

class Engine:

    def __init__(self) -> None:
        self.signals = EngineSignals()
        self._mouse_listener = PynputMouseListener(on_dbclick=self._handle_mouse_dbclick)
        self._selection_grabber = PynputSelectionGrabber()

        self.eng_re = re.compile("[A-z]+")

    def start_listening(self):
        self._mouse_listener.start(wait=False)

    def stop_listening(self):
        self._mouse_listener.stop()

    def _handle_mouse_dbclick(self, x: int, y: int):

        selection = self._selection_grabber.grab()
        print(f"selection = {selection}")

        if len(selection) == 0:
            return

        url = None

        if self.eng_re.match(selection) is not None:
            url = f"https://dictionary.cambridge.org/dictionary/english-chinese-traditional/{selection}"
        else:
            url = f"https://jisho.org/search/{selection}"
        
        if url is not None:
            self.signals.selected.emit(url, x, y)