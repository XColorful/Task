"""ChartModeController -- manages chart HTTP server lifecycle."""

from PySide6.QtCore import QObject


class ChartModeController(QObject):
    """Manages server start/stop for chart mode. Does not block input."""

    def __init__(self, server, parent=None):
        super().__init__(parent)
        self._server = server
        self._active = False

    def open_chart(self, chart_type, engine, chart_dir):
        self._server.set_engine(engine)
        self._server.set_chart_dir(chart_dir)
        if self._active:
            self._server.stop()
        self._server.start()
        self._active = True

    def close_charts(self):
        if self._active:
            self._server.stop()
            self._active = False

    def is_active(self):
        return self._active
