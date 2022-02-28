from typing import *
import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

from engine import Engine
from theme import palette
from word_history import WordHistory


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


class TableItemDelegateSignals(QObject):
    selected = Signal(str, int, int)


class TableItemDelegate(QStyledItemDelegate):

    def __init__(self, engine: Engine) -> None:
        super().__init__()

        self.signals = TableItemDelegateSignals()

        self._engine = engine

        self._icon_cache: Dict[str, QPixmap] = {}
        self._hover_icon_cache: Dict[str, QPixmap] = {}
        self._selected_icon_cache: Dict[str, QPixmap] = {}

        self.state_to_cache = {
            "normal": self._icon_cache,
            "hover": self._hover_icon_cache,
            "selected": self._selected_icon_cache
        }

        self.state_to_color = {
            "normal": QColor.fromRgb(200, 200, 200),
            "hover": QColor.fromRgb(255, 255, 255),
            "selected": QColor.fromRgb(50, 50, 50)
        }

    def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:

        if event.type() == QEvent.MouseButtonRelease:

            mouse_event: QMouseEvent = event

            model: WordHistory = index.model()
            word: str = model.data(model.createIndex(
                index.row(), 0), Qt.DisplayRole)

            if index.column() == 2:

                self.signals.selected.emit(self._engine.resolve_url(
                    word), mouse_event.globalX(), mouse_event.globalY())

            elif index.column() == 3:
                model.remove_word(word)

        return super().editorEvent(event, model, option, index)

    def _get_icon(self, icon_path: str, flag: QStyle.StateFlag):

        # determine state
        state = "normal"
        if flag & QStyle.State_MouseOver > 0:
            state = "hover"
        elif flag & QStyle.State_Selected > 0:
            state = "selected"

        cache = self.state_to_cache[state]

        if icon_path in cache:
            return cache[icon_path]

        # cache miss

        # read the image file specified by the model
        pixmap = QPixmap(icon_path)

        # fill icon with desired color
        mask = pixmap.createMaskFromColor(QColor('black'), Qt.MaskOutColor)

        pixmap.fill(self.state_to_color[state])
        pixmap.setMask(mask)
        cache[icon_path] = pixmap

        return pixmap

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        # return super().paint(painter, option, index)
        if index.column() >= 2:
            # paint QIcon here using data provided by the model
            icon_path = index.data()
            icon = QIcon(self._get_icon(icon_path, option.state))

            opt = QStyleOptionViewItem(option)
            self.initStyleOption(opt, index)

            icon_size = 20
            opt.icon = icon
            opt.decorationSize = QSize(icon_size, icon_size)
            opt.features = QStyleOptionViewItem.HasDecoration
            opt.text = ""

            opt.widget.style().drawControl(QStyle.CE_ItemViewItem, opt, painter, opt.widget)
        else:
            return super().paint(painter, option, index)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.is_listening = False
        self.dict_win = DictWindow()

        self.engine = Engine()
        self.engine.signals.selected.connect(self._show_dict)

        self.main_layout = QVBoxLayout()

        self.listen_btn = QPushButton("Start Listening")
        self.listen_btn.clicked.connect(self._handle_start_btn)
        self.main_layout.addWidget(self.listen_btn)

        # Vocab list table
        self.vocab_list_table = QTableView()
        self.vocab_list_table.setStyleSheet("""
QTableView::item:selected{
    background-color: rgb(149, 187, 232);
}
        """)
        self.vocab_list_table.setModel(self.engine.word_history_model)
        self.vocab_list_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        self.vocab_list_table.verticalHeader().setStyleSheet("""
QHeaderView::section {
    border: 0;
    border-left: 3px solid rgba(0, 0, 0, 0);
    padding-left: 3px;
}
QHeaderView::section:checked {
    border: 0;
    border-left: 3px solid rgb(149, 187, 232);
}

        """)

        self.vocab_list_table.viewport().setMouseTracking(True)
        self.vocab_list_table_delegate = TableItemDelegate(self.engine)
        self.vocab_list_table_delegate.signals.selected.connect(
            self._show_dict)
        self.vocab_list_table.setItemDelegate(self.vocab_list_table_delegate)

        self.vocab_list_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.vocab_list_table.horizontalHeader().setSectionResizeMode(1,
                                                                      QHeaderView.ResizeToContents)
        self.vocab_list_table.horizontalHeader().setSectionResizeMode(2,
                                                                      QHeaderView.ResizeToContents)
        self.vocab_list_table.horizontalHeader().setSectionResizeMode(3,
                                                                      QHeaderView.ResizeToContents)

        self.vocab_list_table.horizontalHeader()
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
