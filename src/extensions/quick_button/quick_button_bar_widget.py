"""QuickButtonBarWidget -- sidebar widget showing quick buttons for all Taskers."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt


class QuickButtonBarWidget(QWidget):
    """Sidebar quick buttons panel. Lists buttons from all Taskers in main view,
    or from current Tasker in tasker view."""

    button_clicked = Signal(dict)  # emits button_def dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._buttons = []

    def refresh(self, buttons, show_tasker_label=False):
        """Reload buttons list.

        Args:
            buttons: list of dicts: {command, label, preset, tasker_id?, tasker_label?}
            show_tasker_label: if True, show which Tasker each button belongs to
        """
        self._clear()
        self._buttons = []
        for i, btn in enumerate(buttons):
            label = btn.get("label", btn.get("command", "?"))
            display = label
            if show_tasker_label and "tasker_label" in btn:
                display = f"[{btn['tasker_label']}] {label}"

            widget = QPushButton(display)
            widget.setStyleSheet("text-align: left; padding: 3px 8px; font-size: 12px;")
            widget.clicked.connect(lambda checked=False, b=btn: self.button_clicked.emit(b))
            self._layout.addWidget(widget)
            self._buttons.append(widget)

        self._layout.addStretch()

    def _clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
