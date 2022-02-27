from ast import Call, arg
import time
from threading import Thread
from typing import *
from pynput.mouse import Listener, Button
from base_mouse_listener import BaseMouseListener


class PynputMouseListener(BaseMouseListener):

    def __init__(self, on_dbclick: Callable[[int, int], None], dbclick_gap=0.3) -> None:
        super().__init__(on_dbclick, dbclick_gap)

        self._init_listener()

        self._last_click = 0

    def _init_listener(self):
        self._listener = Listener(
            on_click=self._handle_click
        )

    def start(self, wait=True):
        self._listener.start()
        if wait:
            self._listener.join()

    def stop(self):
        self._listener.stop()
        self._init_listener()

    def _handle_click(self, x, y, btn, pressed):

        if btn == Button.left and pressed:

            current_time = time.time()
            diff = abs(current_time - self._last_click)

            if diff < self._dbclick_gap:
                # self._on_dbclick()
                Thread(target=self._on_dbclick, args=(x, y)).start()

            self._last_click = current_time
