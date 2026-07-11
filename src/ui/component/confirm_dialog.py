"""ConfirmDialog -- confirmation dialog with optional 'do not ask again'."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QDialogButtonBox
from PySide6.QtCore import Qt


class ConfirmDialog(QDialog):
    """Simple confirm/cancel dialog."""

    def __init__(self, parent, title, message, detail="", dangerous=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_font = msg_label.font()
        msg_font.setBold(True)
        msg_label.setFont(msg_font)
        layout.addWidget(msg_label)

        if detail:
            detail_label = QLabel(detail)
            detail_label.setWordWrap(True)
            detail_label.setStyleSheet("color: #888;")
            layout.addWidget(detail_label)

        self._dont_ask = QCheckBox("Don't ask again")
        layout.addWidget(self._dont_ask)

        buttons = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        if dangerous:
            buttons.button(QDialogButtonBox.Yes).setStyleSheet(
                "background: #E74C3C; color: white; border-radius: 3px; padding: 4px 16px;")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._result = False

    def is_dont_ask_checked(self):
        return self._dont_ask.isChecked()

    @staticmethod
    def confirm(parent, title, message, detail="", dangerous=False):
        dlg = ConfirmDialog(parent, title, message, detail, dangerous)
        return dlg.exec() == QDialog.Accepted
