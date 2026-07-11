"""QuickButtonEditor -- dialog for creating/editing quick button presets."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QCheckBox, QDialogButtonBox
)


class QuickButtonEditor(QDialog):
    """Modal dialog to add or edit a quick button preset."""

    def __init__(self, parent=None, button_def=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Quick Button" if button_def else "Add Quick Button")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        preset = button_def.get("preset", {}) if button_def else {}

        self._command = QLineEdit(button_def.get("command", "") if button_def else "")
        self._command.setPlaceholderText("e.g. 'hw'")
        form.addRow("Command:", self._command)

        self._label = QLineEdit(button_def.get("label", "") if button_def else "")
        self._label.setPlaceholderText("Display label")
        form.addRow("Label:", self._label)

        self._attr = QLineEdit(preset.get("attribute", ""))
        self._attr.setPlaceholderText("Default attribute")
        form.addRow("Attribute:", self._attr)

        self._content = QLineEdit(preset.get("content", ""))
        self._content.setPlaceholderText("Default content (leave empty for prompt)")
        form.addRow("Content:", self._content)

        self._comment = QLineEdit(preset.get("comment", ""))
        self._comment.setPlaceholderText("Default comment")
        form.addRow("Comment:", self._comment)

        self._use_default_date = QCheckBox()
        self._use_default_date.setChecked(preset.get("use_default_date", True))
        form.addRow("Auto-fill date:", self._use_default_date)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "command": self._command.text().strip(),
            "label": self._label.text().strip() or self._command.text().strip(),
            "preset": {
                "attribute": self._attr.text().strip(),
                "content": self._content.text().strip(),
                "comment": self._comment.text().strip(),
                "use_default_date": self._use_default_date.isChecked(),
            }
        }
