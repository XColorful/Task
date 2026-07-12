"""ChartLauncher -- button + type selection that starts HTTP server and opens browser."""

import webbrowser
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal


class ChartLauncher(QWidget):
    """Toolbar widget: select chart type, then open in external browser."""

    chart_opened = Signal(str)  # chart type name
    chart_closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        types = [
            ("Attr Count", "attr_count"),
            ("Monthly Count", "monthly_count"),
            ("Duration", "duration"),
            ("Heatmap", "heatmap"),
            ("3D Monthly", "3d_monthly"),
        ]

        self._buttons = {}
        for label, ctype in types:
            btn = QPushButton(label)
            btn.setStyleSheet("padding: 4px 10px; font-size: 12px;")
            btn.clicked.connect(lambda checked=False, t=ctype: self._open_chart(t))
            layout.addWidget(btn)

        close = QPushButton("Close Charts")
        close.setStyleSheet("background: #7F8C8D; color: white; padding: 4px 10px;")
        close.clicked.connect(self._close)
        layout.addWidget(close)

        layout.addStretch()

        self._server = None
        self._server_port = 19527

    def set_server(self, server):
        self._server = server

    def _open_chart(self, chart_type):
        if self._server:
            self._server.stop()
        self._server.start()
        url = f"{self._server.url}/chart/{chart_type}.html"
        webbrowser.open(url)
        self.chart_opened.emit(chart_type)

    def _close(self):
        if self._server:
            self._server.stop()
        self.chart_closed.emit()
