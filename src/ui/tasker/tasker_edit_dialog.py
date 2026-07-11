"""TaskerEditDialog -- modal dialog for creating/editing a Tasker."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox
)
from PySide6.QtCore import Qt


class TaskerEditDialog(QDialog):
    """Modal dialog: create or edit a Tasker."""

    def __init__(self, parent=None, tasker_data=None, types=None):
        super().__init__(parent)
        self.setWindowTitle("New Tasker" if tasker_data is None else "Edit Tasker")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._label_edit = QLineEdit(tasker_data.get("label", "") if tasker_data else "")
        self._label_edit.setPlaceholderText("Tasker name")
        form.addRow("Label:", self._label_edit)

        self._desc_edit = QLineEdit(tasker_data.get("description", "") if tasker_data else "")
        self._desc_edit.setPlaceholderText("Optional description")
        form.addRow("Description:", self._desc_edit)

        self._type_combo = QComboBox()
        for t in (types or ["default", "timer", "account", "label"]):
            self._type_combo.addItem(t)
        if tasker_data:
            idx = self._type_combo.findText(tasker_data.get("type", "default"))
            if idx >= 0:
                self._type_combo.setCurrentIndex(idx)
        self._type_combo.setEnabled(tasker_data is None)
        form.addRow("Type:", self._type_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "label": self._label_edit.text().strip(),
            "description": self._desc_edit.text().strip(),
            "type": self._type_combo.currentText(),
        }
