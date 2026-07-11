"""Main Controller -- UI state machine, connects window signals to services."""

from PySide6.QtCore import QObject

from core.input_processor import InputPreprocessor


class MainController(QObject):
    """Manages UI state transitions and delegates input to services."""

    STATE_MAIN = "main"
    STATE_TASKER = "tasker"
    STATE_SETTINGS = "settings"
    STATE_CHART = "chart"

    def __init__(self, window, tray, storage=None):
        super().__init__()
        self._window = window
        self._tray = tray
        self._storage = storage
        self._state = self.STATE_MAIN
        self._current_tasker_id = None
        self._tasker_service = None
        self._task_service = None
        self._history = []

        # Connect signals
        self._window.input_submitted.connect(self._on_input)
        self._tray.activated.connect(self._on_tray_activated)

        # Register commands
        self._commands = {
            self.STATE_MAIN: ["exit", "settings", "backup", "reload", "txt", "chart"],
            self.STATE_TASKER: ["exit", "new", "search", "delete", "edit", "backup", "reload"],
        }

        # Initialize
        self._enter_main()

    def _enter_main(self):
        self._state = self.STATE_MAIN
        self._current_tasker_id = None
        cmds = self._commands.get(self.STATE_MAIN, [])
        self._window.set_commands(cmds)
        # Show Tasker list in content area (placeholder for phase 6)
        self._clear_content()
        label = QLabel("Task v2.0\n\nType a Tasker name to enter.\n/settings for configuration.\nexit to quit.")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #666; font-size: 16px;")
        self._window.content_area.addWidget(label)
        self._window.content_area.setCurrentWidget(label)
        self._window.log("Task ready.")

    def _clear_content(self):
        while self._window.content_area.count() > 0:
            w = self._window.content_area.widget(0)
            self._window.content_area.removeWidget(w)
            w.deleteLater()

    def _on_input(self, text):
        """Handle submitted input through preprocessing chain."""
        if not text:
            return

        # Preprocessing
        processed = InputPreprocessor.process(text)
        self._window.log(f"> {text}")

        parts = processed.split(" ", 1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        self._dispatch(cmd, arg)

    def _dispatch(self, cmd, arg):
        """Dispatch command based on current state."""
        if cmd == "exit":
            self._on_exit()
            return
        elif cmd == "settings":
            self._enter_settings()
            return

        if self._state == self.STATE_MAIN:
            self._dispatch_main(cmd, arg)
        elif self._state == self.STATE_TASKER:
            self._dispatch_tasker(cmd, arg)
        elif self._state == self.STATE_SETTINGS:
            self._dispatch_settings(cmd, arg)

    def _dispatch_main(self, cmd, arg):
        if cmd == "chart":
            self._window.log("[TODO] Chart mode not yet implemented")
        elif cmd == "backup":
            self._window.log("[TODO] Backup not yet integrated")
        else:
            # Try entering a Tasker by name
            self._window.log(f"Looking for Tasker: {cmd}")
            if self._tasker_service:
                taskers = self._tasker_service.list_taskers()
                for t in taskers:
                    if cmd in t.get("label", "") or cmd == t.get("id", ""):
                        self._enter_tasker(t["id"])
                        return
            self._window.log(f"No Tasker found matching '{cmd}'")

    def _dispatch_tasker(self, cmd, arg):
        if cmd == "new":
            self._window.log(f"[TODO] new task with arg: {arg}")
        elif cmd == "search":
            self._window.log(f"[TODO] search: {arg}")
        elif cmd == "delete":
            self._window.log(f"[TODO] delete: {arg}")
        elif cmd == "edit":
            self._window.log(f"[TODO] edit: {arg}")
        else:
            self._window.log(f"Unknown command in Tasker: {cmd}")

    def _dispatch_settings(self, cmd, arg):
        self._window.log(f"[settings] {cmd} {arg}")

    def _enter_tasker(self, tasker_id):
        self._state = self.STATE_TASKER
        self._current_tasker_id = tasker_id
        cmds = self._commands.get(self.STATE_TASKER, [])
        self._window.set_commands(cmds)
        # Phase 6 will add Task table here
        self._clear_content()
        if self._tasker_service:
            tasker = self._tasker_service.get_tasker(tasker_id)
            if tasker:
                label = QLabel(f"Tasker: {tasker.label}\n\n{len(tasker.task_list)} tasks loaded\n\nType 'new' to create, 'search' to find.")
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("color: #aaa; font-size: 14px;")
                self._window.content_area.addWidget(label)
                self._window.content_area.setCurrentWidget(label)
                self._window.log(f"Entered Tasker: {tasker.label}")
                self._window.setWindowTitle(f"Task - {tasker.label}")
                return
        self._window.log("Failed to load Tasker.")

    def _enter_settings(self):
        self._state = self.STATE_SETTINGS
        self._window.log("Entered settings mode.")

    def _on_exit(self):
        if self._state == self.STATE_MAIN:
            self._window.close()
            self._tray._on_exit()
        elif self._state == self.STATE_TASKER:
            self._enter_main()
            self._window.setWindowTitle("Task")
            self._window.log("Returned to main.")
        else:
            self._enter_main()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._window.show()
            self._window.raise_()
            self._window.activateWindow()

    def set_tasker_service(self, service):
        self._tasker_service = service

    def set_task_service(self, service):
        self._task_service = service

from PySide6.QtWidgets import QLabel, QSystemTrayIcon
from PySide6.QtCore import Qt
