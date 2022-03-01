from typing import *
import json
import re
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class DictSourceModelSignals(QObject):
    rejected = Signal(str)


class DictSourceModel(QAbstractTableModel):

    def __init__(self, data: List[List[str]]) -> None:
        super().__init__()
        self.source_data = data
        self.signals = DictSourceModelSignals()

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 2

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.source_data)

    def data(self, index: QModelIndex, role: int = ...) -> Any:

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.source_data[row][col]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "pattern (re)"
            elif section == 1:
                return "url"

        return super().headerData(section, orientation, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return super().flags(index) | Qt.ItemIsEditable

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:

        row = index.row()
        col = index.column()

        if col == 0:
            try:
                re.compile(value)
            except re.error:
                self.signals.rejected.emit(
                    f'"{value}" is not a valid regular expression.')
                return False

        self.source_data[row][col] = value
        self.dataChanged.emit(index, index)

        return True


class DictionarySourceEditor(QDialog):

    def __init__(self, data: List[List[str]]) -> None:
        super().__init__()

        self.main_layout = QVBoxLayout()

        self.source_view = QTableView()
        self.source_model = DictSourceModel(data)
        self.source_model.signals.rejected.connect(self._show_error)
        self.source_view.setModel(self.source_model)
        self.main_layout.addWidget(self.source_view)
        self.source_view.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.source_view.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents)

        self.setLayout(self.main_layout)

    def _show_error(self, msg: str):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Error")
        dlg.setIcon(QMessageBox.Critical)
        dlg.setText(msg)
        dlg.exec_()
