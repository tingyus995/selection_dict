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

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        self.beginRemoveRows(QModelIndex(), row, (row + count - 1))
        del self.source_data[row: (row + count)]
        self.endRemoveRows()
        return True

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

        self.main_layout = QHBoxLayout()

        self.source_view = QTableView()
        self.source_model = DictSourceModel(data)
        self.source_model.signals.rejected.connect(self._show_error)
        self.source_view.setModel(self.source_model)
        self.main_layout.addWidget(self.source_view)
        self.source_view.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.source_view.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents)
        self.source_view.setSelectionMode(
            QAbstractItemView.SingleSelection)
        self.source_view.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        self.source_view.selectionModel().selectionChanged.connect(self._handle_selection_changed)
        
        self.buttons_layout = QVBoxLayout()
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._handle_delete_btn)
        self.delete_button.setEnabled(False)
        self.buttons_layout.addWidget(self.delete_button)
        self.main_layout.addLayout(self.buttons_layout)

        self.setLayout(self.main_layout)
    
    def _handle_delete_btn(self):
        self.source_model.removeRow(self.source_view.selectionModel().selectedIndexes()[0].row())
    
    def _handle_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        if selected.size() == 0:
            self.delete_button.setEnabled(False)
        else:
            self.delete_button.setEnabled(True)

    def _show_error(self, msg: str):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Error")
        dlg.setIcon(QMessageBox.Critical)
        dlg.setText(msg)
        dlg.exec_()
