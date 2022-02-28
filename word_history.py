from typing import *
import csv

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt, QSize
from PySide2.QtGui import QColor


class WordHistory(QAbstractTableModel):

    def __init__(self) -> None:
        super().__init__()

        self.history_data: Dict[str, int] = {}
        print(self.history_data)

    def load_data(self, path: str):

        self.beginResetModel()
        with open(path, 'r', encoding='utf-8') as f:
            for k, v in csv.reader(f):
                self.history_data[k] = int(v)
        self.endResetModel()

    def save_data(self, path):
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.history_data.items())

    def add_word(self, word: str):
        try:
            row = list(self.history_data.keys()).index(word)
            idx = self.createIndex(row, 1)
            self.history_data[word] += 1
            self.dataChanged.emit(idx, idx, [])

        except ValueError:
            self.beginInsertRows(QModelIndex(), len(
                self.history_data), len(self.history_data))
            self.history_data[word] = 1
            self.endInsertRows()

        print(self.history_data)

    def remove_word(self, word: str):
        try:
            row = list(self.history_data.keys()).index(word)
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.history_data[word]
            self.endRemoveRows()
        except ValueError:
            pass

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.history_data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 4

    def data(self, index: QModelIndex, role: int = ...):

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:

            if col == 0:
                return list(self.history_data.keys())[row]
            elif col == 1:
                return self.history_data[list(self.history_data.keys())[row]]
            elif col == 2:
                return "icons/book-atlas.svg"
            elif col == 3:
                return "icons/trash-can.svg"

        elif role == Qt.BackgroundRole:

            val = self.history_data[list(self.history_data.keys())[row]]

            a = 100

            if val >= 5:
                return QColor.fromRgb(235, 64, 52, a)
            elif val == 4:
                return QColor.fromRgb(235, 147, 52, a)
            elif val == 3:
                return QColor.fromRgb(235, 223, 52, a)
            elif val == 2:
                return QColor.fromRgb(159, 235, 52, a)
            elif val == 1:
                return QColor.fromRgb(83, 235, 52, a)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        if role == Qt.SizeHintRole:
            if col >= 2:
                return QSize(20, 20)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == 0:
                    return "Word"
                elif section == 1:
                    return "Count"
                else:
                    return ""

        return super().headerData(section, orientation, role)
