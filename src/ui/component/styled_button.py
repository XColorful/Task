"""StyledButton -- unified style button with color presets, icons, shortcut labels."""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon


class StyledButton(QPushButton):
    """Unified style button with color presets and keyboard shortcut label."""

    class Color:
        PRIMARY = ("#4A90D9", "#3A7BC8", "#FFFFFF")
        SUCCESS = ("#27AE60", "#219A52", "#FFFFFF")
        DANGER = ("#E74C3C", "#C0392B", "#FFFFFF")
        NEUTRAL = ("#7F8C8D", "#6C7A7B", "#FFFFFF")
        GHOST = ("transparent", "#3A3A3A", "#CCCCCC")

    def __init__(self, text="", parent=None, *,
                 color=None, shortcut="", icon_path="", size=None):
        super().__init__(text, parent)
        self._color = color or self.Color.PRIMARY
        self._shortcut = shortcut
        self._apply_style()
        if icon_path:
            self.setIcon(QIcon(icon_path))
        if size:
            self.setFixedSize(*size)
        if shortcut:
            display = f"{text} [{shortcut}]" if text else shortcut
            self.setText(display)

    def _apply_style(self):
        bg, hover, fg = self._color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {hover};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)
