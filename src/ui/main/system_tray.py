"""System Tray -- minimize to tray, right-click menu for exit."""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication


class SystemTray(QSystemTrayIcon):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(self._make_icon())
        self.setToolTip("Task")

        menu = QMenu()
        show_action = menu.addAction("Show Window")
        show_action.triggered.connect(self._on_show)
        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self._on_exit)
        self.setContextMenu(menu)
        self.activated.connect(self._on_activated)

    def _make_icon(self):
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPixmap, QPainter, QColor
        p = QPixmap(32, 32)
        p.fill(QColor(0, 0, 0, 0))
        pt = QPainter(p)
        pt.setPen(Qt.PenStyle.NoPen)
        pt.setBrush(QColor("#4A90D9"))
        pt.drawRoundedRect(2, 2, 28, 28, 6, 6)
        pt.end()
        return QIcon(p)

    def _on_show(self):
        if self.parent():
            self.parent().show()
            self.parent().raise_()
            self.parent().activateWindow()

    def _on_exit(self):
        self.hide()
        QCoreApplication.quit()

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._on_show()
