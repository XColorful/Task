"""ExportService -- facade for exporting human-readable text and backup files."""

import os
from .txt_exporter import TxtExporter


class ExportService:
    """Export tasks to human-readable formats."""

    def __init__(self):
        self._exporter = TxtExporter()

    def export_txt(self, tasker_list, sort_mode="date", output_path=None):
        """Export taskers to text, optionally writing to file."""
        lines = self._exporter.export(tasker_list, sort_mode)
        text = "\n".join(lines)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
        return text

    def backup(self, storage_manager, backup_dir):
        """Create a full backup via StorageManager."""
        return storage_manager.backup_all(backup_dir)
