from typing import *


class BaseMouseListener:
    def __init__(self, on_dbclick: Callable[[int, int], None], dbclick_gap=0.2) -> None:
        self._on_dbclick = on_dbclick
        self._dbclick_gap = dbclick_gap

    def start(self, wait=True):
        pass

    def stop(self):
        pass
