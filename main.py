import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

from engine import Engine
from theme import palette


class DictWindow(QMainWindow):

    def __init__(self, url: str, x: int, y: int) -> None:
        super().__init__()
        self.setWindowFlag(Qt.Popup)

        self.set_location(x, y)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.main_layout.addWidget(self.web_view)
        self.set_url(url)
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.radius = 10
        self.border_pen = QPen()
        self.border_pen.setWidth(3)
        self.border_pen.setColor(Qt.red)
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
        self.web_view.setHtml("")


class ListeningStatusIndicator(QLabel):

    def __init__(self) -> None:
        super().__init__()

        size = 10
        self.green_dot = self._create_dot(QColor.fromRgb(94, 235, 52), size)
        self.red_dot = self._create_dot(QColor.fromRgb(235, 92, 52), size)

    def _create_dot(self, color: QColor, size: int):
        brush = QBrush()
        brush.setColor(color)
        brush.setStyle(Qt.SolidPattern)

        image = QImage(size, size, QImage.Format_RGBA8888)
        image.fill(0)

        pixmap = QPixmap.fromImage(image)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(brush)

        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.fillPath(path, brush)
        painter.end()

        return pixmap

    def show_green_dot(self):
        self.setPixmap(self.green_dot)

    def show_red_dot(self):
        self.setPixmap(self.red_dot)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.is_listening = False
        self.dict_win = None

        self.engine = Engine()
        self.engine.signals.selected.connect(self._show_dict)

        self.main_layout = QVBoxLayout()

        self.listen_btn = QPushButton("Start Listening")
        self.listen_btn.clicked.connect(self._handle_start_btn)
        self.main_layout.addWidget(self.listen_btn)

        self.vocab_list_table = QTableView()
        self.vocab_list_table.setModel(self.engine.word_history_model)
        self.main_layout.addWidget(self.vocab_list_table)

        self.listening_status_indicator = ListeningStatusIndicator()
        self.listening_status_indicator.show_red_dot()
        self.statusBar().addWidget(self.listening_status_indicator)

        self.listeining_status_text = QLabel("not listening")
        self.statusBar().addWidget(self.listeining_status_text)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.engine.save_history()

    def _show_dict(self, url, x, y):
        print(url)
        if self.dict_win is None:
            self.dict_win = DictWindow(url, x, y)
            self.dict_win.show()
        else:
            self.dict_win.set_location(x, y)
            self.dict_win.set_url(url)
            self.dict_win.show()

    def _handle_start_btn(self):
        if self.is_listening:
            self.engine.stop_listening()
            self.listening_status_indicator.show_red_dot()
            self.listeining_status_text.setText("not listening")
            self.listen_btn.setText("Start Listening")
        else:
            self.engine.start_listening()
            self.listening_status_indicator.show_green_dot()
            self.listeining_status_text.setText("listening")
            self.listen_btn.setText("Stop Listening")

        self.is_listening = not self.is_listening


app = QApplication(sys.argv)
# Force the style to be the same on all OSs
app.setStyle("Fusion")
# Apply dark theme using palette
app.setPalette(palette)
win = MainWindow()
win.show()
app.exec_()
