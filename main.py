from typing import *
import shutil
import os
import sys
import json

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

import pyperclip

from engine import Engine
from theme import palette
from word_history import WordHistory
from dict_window import DictWindow


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

    def __init__(self, engine: Engine, menu: QMenu) -> None:
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

        self._menu = menu

    def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        if event.type() == QEvent.MouseButtonRelease:

            mouse_event: QMouseEvent = event

            if mouse_event.button() == Qt.LeftButton:

                model: WordHistory = index.model()
                word: str = model.data(model.createIndex(
                    index.row(), 0), Qt.DisplayRole)

                if index.column() == 2:

                    self.signals.selected.emit(self._engine.resolve_url(
                        word), mouse_event.globalX(), mouse_event.globalY())

                elif index.column() == 3:
                    model.remove_word(word)
            elif mouse_event.button() == Qt.RightButton:
                self._menu.exec_(mouse_event.globalPos())

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
        self.vocab_list_table.setSelectionMode(
            QAbstractItemView.SingleSelection)
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

        self._create_menu()

        self.vocab_list_table.viewport().setMouseTracking(True)
        self.vocab_list_table_delegate = TableItemDelegate(
            self.engine, self.word_menu)
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

        self._load_config()

    def _load_config(self):
        if not os.path.exists("config.json"):
            shutil.copy("config.default.json", "config.json")

        with open("config.json", 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # restore opacity
        opacity = self.config["dict_opacity"]
        idx = int(int(opacity * 100) / 5)
        self.opacity_action_group.actions()[idx - 1].setChecked(True)

        # restore always on top
        if self.config["always_on_top"]:
            self._enable_always_on_top()
            self.always_on_top_action.setChecked(True)
        

    def _save_config(self):

        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(self.config, f)

    def _set_opacity(self, opacity: float):
        print(f"set opacity {opacity}")
        self.config["dict_opacity"] = opacity

    def _get_opacity(self):
        return self.config["dict_opacity"]

    def _copy_selected_word(self):
        row = self.vocab_list_table.selectionModel().selectedIndexes()[0].row()
        word = self.engine.word_history_model.data(
            self.engine.word_history_model.createIndex(row, 0), Qt.DisplayRole)
        pyperclip.copy(word)

    def _reset_selected_word_count(self):
        row = self.vocab_list_table.selectionModel().selectedIndexes()[0].row()
        self.engine.word_history_model.reset_count(row)

    def _create_menu(self):
        
        self.options_menu = self.menuBar().addMenu("&Options")

        self.always_on_top_action = QAction("Always On Top")
        self.always_on_top_action.setCheckable(True)
        self.always_on_top_action.triggered.connect(self._handle_always_on_top_action)
        self.options_menu.addAction(self.always_on_top_action)

        self.dict_opacity_menu = self.options_menu.addMenu(
            "&Dictionary Opacity")

        self.opacity_action_group = QActionGroup(self)

        for i in range(5, 101, 5):
            action = QAction(f"{i}%", self)
            action.setCheckable(True)

            def closure():

                opacity = i / 100

                return lambda: self._set_opacity(opacity)

            action.triggered.connect(closure())
            self.opacity_action_group.addAction(action)

        self.dict_opacity_menu.addActions(self.opacity_action_group.actions())

        self.word_menu = QMenu()
        self.copy_word_action = QAction("Copy Word")
        self.copy_word_action.triggered.connect(self._copy_selected_word)
        self.word_menu.addAction(self.copy_word_action)
        self.reset_count_action = QAction("Reset Count")
        self.reset_count_action.triggered.connect(
            self._reset_selected_word_count)
        self.word_menu.addAction(self.reset_count_action)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.engine.save_history()
        self._save_config()
    
    def _handle_always_on_top_action(self, checked: bool):
        if checked:
            self._enable_always_on_top()
        else:
            self._disble_always_on_top()
    
    def _enable_always_on_top(self):
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.config["always_on_top"] = True
        self.show()

    def _disble_always_on_top(self):
        self.setWindowFlags(self.windowFlags() & (~Qt.WindowStaysOnTopHint))
        self.config["always_on_top"] = False
        self.show()

    def _show_dict(self, url, x, y):
        print(url)
        self.dict_win.set_location(x, y)
        self.dict_win.set_url(url)
        self.dict_win.setWindowOpacity(self._get_opacity())
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
