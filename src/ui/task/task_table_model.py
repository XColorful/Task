"""TaskTableModel -- QAbstractTableModel for Task data."""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from core.abstract import BaseTask


class TaskTableModel(QAbstractTableModel):
    """5-column model: index, date, attribute, content, comment."""

    _columns = ["Index", "Date", "Attribute", "Content", "Comment"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []

    def set_tasks(self, tasks):
        self.beginResetModel()
        self._tasks = tasks
        self.endResetModel()

    def append_tasks(self, tasks):
        if not tasks:
            return
        self.beginInsertRows(QModelIndex(), len(self._tasks), len(self._tasks) + len(tasks) - 1)
        self._tasks.extend(tasks)
        self.endInsertRows()

    def update_task(self, row, task):
        if 0 <= row < len(self._tasks):
            self._tasks[row] = task
            self.dataChanged.emit(self.index(row, 0), self.index(row, 4))

    def remove_task(self, row):
        if 0 <= row < len(self._tasks):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._tasks[row]
            self.endRemoveRows()

    def rowCount(self, parent=QModelIndex()):
        return len(self._tasks)

    def columnCount(self, parent=QModelIndex()):
        return 5

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        task = self._tasks[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return str(index.row())
            elif col == 1:
                return task.date
            elif col == 2:
                return task.attribute
            elif col == 3:
                return task.content
            elif col == 4:
                return task.comment

        elif role == Qt.UserRole:
            return task

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._columns[section]
        return None
