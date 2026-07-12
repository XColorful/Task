"""TaskTableModel — QAbstractTableModel for Task data.

Supports per-type columns: default taskers show [Index, Date, Attribute, Content, Comment],
timer taskers show [Index, Start Time, End Time, Attribute, Content, Comment, Duration].
The model detects the tasker type from the first task in the list.
"""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class TaskTableModel(QAbstractTableModel):

    _DEFAULT_COLUMNS = ["Index", "Date", "Attribute", "Content", "Comment"]
    _TIMER_COLUMNS = ["Index", "Start Time", "End Time", "Attribute", "Content", "Comment", "Duration"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._columns = self._DEFAULT_COLUMNS
        self._total_task_count = 0  # estimated total, used for negative index display
        self._partial_load = False  # True when only last 2 segments loaded

    def set_tasks(self, tasks, total_count=None):
        self.beginResetModel()
        self._tasks = tasks
        self._total_task_count = total_count if total_count is not None else len(tasks)
        # Detect column layout from first task type
        if tasks and getattr(tasks[0], 'type', '') == 'timer':
            self._columns = self._TIMER_COLUMNS
        else:
            self._columns = self._DEFAULT_COLUMNS
        self.endResetModel()

    def append_tasks(self, tasks):
        if not tasks:
            return
        self.beginInsertRows(QModelIndex(), len(self._tasks), len(self._tasks) + len(tasks) - 1)
        self._tasks.extend(tasks)
        self._total_task_count = max(self._total_task_count, len(self._tasks))
        self.endInsertRows()

    def update_task(self, row, task):
        if 0 <= row < len(self._tasks):
            self._tasks[row] = task
            col_count = len(self._columns)
            self.dataChanged.emit(self.index(row, 0), self.index(row, col_count - 1))

    def remove_task(self, row):
        if 0 <= row < len(self._tasks):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._tasks[row]
            self._total_task_count = max(0, self._total_task_count - 1)
            self.endRemoveRows()

    def rowCount(self, parent=QModelIndex()):
        return len(self._tasks)

    def columnCount(self, parent=QModelIndex()):
        return len(self._columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        task = self._tasks[index.row()]
        col = index.column()
        is_timer = self._columns[1] == "Start Time"

        if role == Qt.DisplayRole:
            if col == 0:
                # Index: -1 = newest, 0 = oldest, etc.
                # partial load: last N are loaded, so newest task is row N-1
                # total_task_count > len: need negative indices
                return str(index.row() - self._total_task_count)
            elif is_timer:
                # Timer column layout
                if col == 1:
                    return task.start_time
                elif col == 2:
                    return task.end_time
                elif col == 3:
                    return task.attribute
                elif col == 4:
                    return task.content
                elif col == 5:
                    return task.comment
                elif col == 6:
                    dur = getattr(task, 'duration_minutes', None)
                    if dur is not None:
                        from util.date_utils import format_duration
                        return format_duration(dur)
                    return ""
            else:
                # Default column layout
                if col == 1:
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
