import time

import pyperclip

from pynput.keyboard import Controller, Key
from base_selection_grabber import BaseSelectionGrabber


class PynputSelectionGrabber(BaseSelectionGrabber):

    def __init__(self) -> None:
        super().__init__()
        self._keyboard = Controller()

    def grab(self) -> str:
        # backup clipboard content (text only)
        original_clipboard = pyperclip.paste()

        # set clipboard to "" in case nothing is selected
        pyperclip.copy("")

        # send Ctrl + C to copy selected text
        self._keyboard.press(Key.ctrl)
        self._keyboard.press('c')
        self._keyboard.release('c')
        self._keyboard.release(Key.ctrl)

        # wait for item to be copied into clipboard
        time.sleep(0.1)

        # get clipboard content
        selection = pyperclip.paste().strip()

        # restore original clipboard content
        pyperclip.copy(original_clipboard)

        return selection
