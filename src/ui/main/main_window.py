"""Main Window -- three-zone layout with sidebar, system tray support, x button removed."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPlainTextEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QSplitter, QLabel, QFrame,
)
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QCloseEvent, QKeyEvent


class MainWindow(QMainWindow):
    """Main window with unified three-zone layout + right sidebar."""

    input_submitted = Signal(str)
    window_hidden = Signal()
    window_shown = Signal()
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task")
        self.resize(900, 600)

        self._setup_flags()
        self._build_layout()
        self._connect_signals()

    def _setup_flags(self):
        """Remove x button via window flags."""
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint |
            Qt.WindowCloseButtonHint
        )

    def _build_layout(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # Left: main area
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Content area (switched by controller)
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background: #1e1e1e;")

        # Output area (read-only log)
        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setMaximumBlockCount(500)
        self.output_area.setStyleSheet("background: #0d0d0d; color: #ccc; font-size: 12px;")
        self.output_area.setFixedHeight(120)

        # Input box (multi-line, word-wrap, no auto-newline)
        self.input_box = QPlainTextEdit()
        self.input_box.setPlaceholderText("Type command or content here...")
        self.input_box.setStyleSheet("background: #2d2d2d; color: #fff; font-size: 14px; padding: 8px;")
        self.input_box.setFixedHeight(60)
        self.input_box.setTabChangesFocus(False)

        left_layout.addWidget(self.content_area, 1)
        left_layout.addWidget(self.output_area)
        left_layout.addWidget(self.input_box)

        # Right: sidebar
        right = QWidget()
        right.setFixedWidth(200)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right.setStyleSheet("background: #252525;")

        # Commands panel
        cmds_label = QLabel("Commands")
        cmds_label.setStyleSheet("color: #888; font-size: 11px; font-weight: bold;")
        right_layout.addWidget(cmds_label)
        self.commands_panel = QWidget()
        self.commands_layout = QVBoxLayout(self.commands_panel)
        self.commands_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.commands_panel)

        # Quick buttons panel
        qb_label = QLabel("Quick Buttons")
        qb_label.setStyleSheet("color: #888; font-size: 11px; font-weight: bold;")
        right_layout.addWidget(qb_label)
        self.quick_buttons_panel = QWidget()
        self.quick_buttons_layout = QVBoxLayout(self.quick_buttons_panel)
        self.quick_buttons_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.quick_buttons_panel)

        # Search results table
        sr_label = QLabel("Search Results")
        sr_label.setStyleSheet("color: #888; font-size: 11px; font-weight: bold;")
        right_layout.addWidget(sr_label)
        self.search_results = QTableWidget(0, 2)
        self.search_results.setHorizontalHeaderLabels(["Task", "Index"])
        self.search_results.setStyleSheet("color: #ccc;")
        self.search_results.hide()
        right_layout.addWidget(self.search_results, 1)

        right_layout.addStretch()

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter)

    def _connect_signals(self):
        self.input_box.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.input_box and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Return or key_event.key() == Qt.Key_Enter:
                if not (key_event.modifiers() & Qt.ShiftModifier):
                    text = self.input_box.toPlainText().strip()
                    self.input_box.clear()
                    if text:
                        self.input_submitted.emit(text)
                    return True
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        """Override: hide to tray instead of closing."""
        event.ignore()
        self.hide()
        self.window_hidden.emit()

    def log(self, message):
        self.output_area.appendPlainText(message)

    def log_error(self, message):
        self.output_area.appendPlainText(f"[Error] {message}")

    def set_commands(self, commands):
        """Populate sidebar commands panel."""
        self._clear_layout(self.commands_layout)
        for cmd in commands:
            btn = QPushButton(cmd)
            btn.setStyleSheet("text-align: left; padding: 2px 6px;")
            btn.clicked.connect(lambda checked=False, c=cmd: self.input_submitted.emit(c))
            self.commands_layout.addWidget(btn)

    def set_quick_buttons(self, buttons):
        self._clear_layout(self.quick_buttons_layout)
        for btn_def in buttons:
            label = btn_def.get("label", btn_def.get("command", "?"))
            btn = QPushButton(label)
            btn.setStyleSheet("text-align: left; padding: 2px 6px;")
            btn.clicked.connect(
                lambda checked=False, b=btn_def: self.input_submitted.emit(b.get("command", "")))
            self.quick_buttons_layout.addWidget(btn)

    def show_search_results(self, results):
        """results: list of (index, content_str) tuples."""
        self.search_results.setRowCount(len(results))
        for row, (idx, content) in enumerate(results):
            self.search_results.setItem(row, 0, QTableWidgetItem(str(idx)))
            self.search_results.setItem(row, 1, QTableWidgetItem(content))
        self.search_results.show()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
