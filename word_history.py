from typing import *
import csv

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt


class WordHistory(QAbstractTableModel):

    def __init__(self) -> None:
        super().__init__()

        self.history_data: Dict[str, int] = {}
        print(self.history_data)

    def load_data(self, path: str):

        self.beginResetModel()
        with open(path, 'r', encoding='utf-8') as f:
            for k, v in csv.reader(f):
                self.history_data[k] = v
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
        self.beginRemoveRows()
        del self.history_data[word]
        self.endRemoveRows()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.history_data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 2

    def data(self, index: QModelIndex, role: int = ...):

        row = index.row()
        col = index.column()

        if(role == Qt.DisplayRole):

            if col == 0:
                return list(self.history_data.keys())[row]
            elif col == 1:
                return self.history_data[list(self.history_data.keys())[row]]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Word"
            elif section == 1:
                return "Count"

        return super().headerData(section, orientation, role)
