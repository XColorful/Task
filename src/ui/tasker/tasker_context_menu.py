"""TaskerContextMenu -- right-click context menu for Tasker list items."""

from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Qt


class TaskerContextMenu(QMenu):
    """Right-click menu: rename, delete, info."""

    rename_requested = None
    delete_requested = None
    info_requested = None

    def __init__(self, tasker_id, tasker_label, parent=None):
        super().__init__(parent)
        self._tasker_id = tasker_id

        rename = self.addAction(f"Rename '{tasker_label}'")
        rename.triggered.connect(lambda: self._emit_rename(tasker_id))

        self.addSeparator()

        delete = self.addAction(f"Delete '{tasker_label}'")
        delete.setStyleSheet("color: #E74C3C;")

        self.addSeparator()

        info = self.addAction("Info")
        info.triggered.connect(lambda: self._emit_info(tasker_id))

    def _emit_rename(self, tid):
        w = self.parent()
        while w:
            if hasattr(w, 'rename_requested') and hasattr(w.rename_requested, 'emit'):
                w.rename_requested.emit(tid)
                break
            w = w.parent()

    def _emit_info(self, tid):
        w = self.parent()
        while w:
            if hasattr(w, 'info_requested') and hasattr(w.info_requested, 'emit'):
                w.info_requested.emit(tid)
                break
            w = w.parent()
