"""TaskerListWidget -- clickable Tasker list in main view content area."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
)
from PySide6.QtCore import Signal, Qt


class TaskerListWidget(QWidget):
    """Clickable Tasker list ordered by taskers.json. Placed as foreground over watermark."""

    tasker_selected = Signal(str)
    tasker_double_clicked = Signal(str)
    rename_requested = Signal(str)
    delete_requested = Signal(str)
    info_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        header = QLabel("Taskers")
        header.setStyleSheet("color: #888; font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        self._list = QListWidget()
        self._list.setStyleSheet("""
            QListWidget { background: transparent; border: none; }
            QListWidget::item { padding: 8px 12px; margin: 2px 0; border-radius: 4px; }
            QListWidget::item:hover { background: #3a3a3a; }
            QListWidget::item:selected { background: #4A90D9; color: white; }
        """)
        self._list.itemClicked.connect(self._on_clicked)
        self._list.itemDoubleClicked.connect(self._on_double_clicked)
        layout.addWidget(self._list)

    def refresh(self, taskers):
        """Reload list from taskers.json data.

        Args:
            taskers: list of dicts with 'id', 'label', 'type', 'description'
        """
        self._list.clear()
        self._taskers = taskers
        for t in taskers:
            label = t.get("label", "?")
            ttype = t.get("type", "")
            item = QListWidgetItem(f"{label}  [{ttype}]")
            item.setData(Qt.UserRole, t["id"])
            self._list.addItem(item)

    def _on_clicked(self, item):
        tid = item.data(Qt.UserRole)
        self.tasker_selected.emit(tid)

    def _on_double_clicked(self, item):
        tid = item.data(Qt.UserRole)
        self.tasker_double_clicked.emit(tid)
