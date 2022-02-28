from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

class DictWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlag(Qt.Popup)

        self.set_location(0, 0)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.main_layout.addWidget(self.web_view)
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.radius = 10
        self.border_pen = QPen()
        self.border_pen.setWidth(3)
        self.border_pen.setColor(Qt.red)

        with open("loading.html", 'r', encoding='utf-8') as f:
            self.loading_html = f.read()

        self.web_view.setHtml(self.loading_html)

        self._rounded_corners()

    def set_url(self, url: str):
        self.web_view.load(QUrl(url))

    def set_location(self, x: int, y: int):
        self.setGeometry(x, y, 300, 600)

    def _rounded_corners(self):
        bitmap = QBitmap(self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(),
                            self.height(), self.radius, self.radius)

        painter = QPainter(bitmap)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.fillPath(path, QBrush(Qt.black))
        painter.end()
        self.setMask(bitmap)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.web_view.setHtml(self.loading_html)