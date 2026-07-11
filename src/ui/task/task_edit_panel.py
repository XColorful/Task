"""TaskEditPanel -- collapsible form for create/edit Task."""

from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Signal, Qt
from util.date_utils import today_str


class TaskEditPanel(QWidget):
    """Form panel for creating/editing a single Task. Collapsible."""

    task_submitted = Signal(dict)  # fields dict
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)

        main = QVBoxLayout(self)
        form = QFormLayout()

        self._date = QLineEdit(today_str())
        self._date.setPlaceholderText("YYYY_MM_DD")
        form.addRow("Date:", self._date)

        self._attribute = QLineEdit()
        self._attribute.setPlaceholderText("Category (e.g. homework, buy)")
        form.addRow("Attribute:", self._attribute)

        self._content = QLineEdit()
        self._content.setPlaceholderText("Content")
        form.addRow("Content:", self._content)

        self._comment = QLineEdit()
        self._comment.setPlaceholderText("Optional comment")
        form.addRow("Comment:", self._comment)

        main.addLayout(form)

        btns = QHBoxLayout()
        submit = QPushButton("Create")
        submit.setStyleSheet("background: #27AE60; color: white; padding: 4px 16px;")
        submit.clicked.connect(self._submit)
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet("background: #7F8C8D; color: white; padding: 4px 16px;")
        cancel.clicked.connect(self._cancel)
        btns.addWidget(submit)
        btns.addWidget(cancel)
        main.addLayout(btns)

    def open_for_create(self, preset=None):
        self._date.setText(preset.get("date", today_str()) if preset else today_str())
        self._attribute.setText(preset.get("attribute", "") if preset else "")
        self._content.setText(preset.get("content", "") if preset else "")
        self._comment.setText(preset.get("comment", "") if preset else "")
        self.setVisible(True)
        self._content.setFocus()

    def hide_panel(self):
        self.setVisible(False)

    def _submit(self):
        fields = {
            "date": self._date.text().strip(),
            "attribute": self._attribute.text().strip() or "N/A",
            "content": self._content.text().strip(),
            "comment": self._comment.text().strip(),
        }
        if fields["content"]:
            self.task_submitted.emit(fields)
            self.hide_panel()

    def _cancel(self):
        self.cancelled.emit()
        self.hide_panel()
