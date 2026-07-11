"""ToastNotification -- lightweight auto-dismiss feedback popup."""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PySide6.QtGui import QColor


class ToastNotification(QWidget):
    """Lightweight popup that auto-dismisses after ~2 seconds. Stacks multiple toasts."""

    _active_toasts: list['ToastNotification'] = []

    def __init__(self, parent, message, duration_ms=2000):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        label = QLabel(message, self)
        label.setStyleSheet("background: #333; color: #fff; padding: 10px 20px; border-radius: 6px; font-size: 13px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label)
        self.adjustSize()

        # Position above existing toasts
        y_offset = 10
        for t in self._active_toasts:
            y_offset += t.height() + 10
        px = parent.x() + (parent.width() - self.width()) // 2
        py = parent.y() + parent.height() - self.height() - y_offset
        self.move(px, py)

        self._active_toasts.append(self)
        self.show()
        QTimer.singleShot(duration_ms, self._dismiss)

    def _dismiss(self):
        if self in self._active_toasts:
            self._active_toasts.remove(self)
        self.close()
        self.deleteLater()

    @staticmethod
    def show_message(parent, message, duration_ms=2000):
        ToastNotification(parent, message, duration_ms)
