"""TaskSearchBar -- debounced search input that filters table in real time."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Signal, QTimer


class TaskSearchBar(QWidget):
    """Debounced (200ms) real-time search with clear button and result count."""

    search_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Search tasks...")
        self._input.setStyleSheet("padding: 4px 8px;")
        layout.addWidget(self._input)

        self._clear = QPushButton("X")
        self._clear.setFixedWidth(24)
        self._clear.clicked.connect(self._do_clear)
        layout.addWidget(self._clear)

        self._count_label = QLabel("")
        layout.addWidget(self._count_label)

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._emit_search)
        self._input.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        self._timer.start()

    def _emit_search(self):
        self.search_requested.emit(self._input.text())

    def _do_clear(self):
        self._input.clear()
        self.search_requested.emit("")

    def set_count(self, n):
        self._count_label.setText(f"({n})" if n > 0 else "")
