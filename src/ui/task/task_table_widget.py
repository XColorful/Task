"""TaskTableWidget -- sortable, scrollable Task table with dynamic segment loading."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView
from PySide6.QtCore import QSortFilterProxyModel, Qt, Signal
from .task_table_model import TaskTableModel


class TaskTableWidget(QWidget):
    """Central Task table with sorting and scroll-based segment loading."""

    more_data_needed = Signal(int)  # direction: 1 = older, -1 = newer
    task_selected = Signal(int)     # global index
    task_double_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._model = TaskTableModel()
        self._proxy = QSortFilterProxyModel()
        self._proxy.setSourceModel(self._model)
        self._proxy.setSortRole(Qt.DisplayRole)

        self._table = QTableView()
        self._table.setModel(self._proxy)
        self._table.setSortingEnabled(True)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.setStyleSheet("""
            QTableView { background: #1e1e1e; color: #ccc; gridline-color: #333; }
            QTableView::item:selected { background: #4A90D9; }
            QHeaderView::section { background: #2d2d2d; color: #aaa; padding: 4px; }
        """)
        self._table.clicked.connect(self._on_click)
        self._table.doubleClicked.connect(self._on_double_click)

        layout.addWidget(self._table)

    def set_tasks(self, tasks, total_count=None):
        self._model.set_tasks(tasks, total_count=total_count)
        self._table.scrollToBottom()

    def append_tasks(self, tasks):
        self._model.append_tasks(tasks)

    def update_task(self, row, task):
        self._model.update_task(row, task)

    def remove_task(self, row):
        self._model.remove_task(row)

    def get_task_at(self, row):
        return self._model.data(self._model.index(row, 0), Qt.UserRole)

    def _on_click(self, index):
        source = self._proxy.mapToSource(index)
        self.task_selected.emit(source.row())

    def _on_double_click(self, index):
        source = self._proxy.mapToSource(index)
        self.task_double_clicked.emit(source.row())
