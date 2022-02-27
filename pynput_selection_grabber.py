import time

import pyperclip

from pynput.keyboard import Controller, Key
from base_selection_grabber import BaseSelectionGrabber

class PynputSelectionGrabber(BaseSelectionGrabber):

    def __init__(self) -> None:
        super().__init__()
        self._keyboard = Controller()

    def grab(self) -> str:
        # send Ctrl + C
        print("sent")
        self._keyboard.type("Hello")
        self._keyboard.press(Key.ctrl)
        self._keyboard.press('c')
        self._keyboard.release('c')
        self._keyboard.release(Key.ctrl)
        time.sleep(0.1)

        selection = pyperclip.paste().strip()
        pyperclip.copy("")
        return selection