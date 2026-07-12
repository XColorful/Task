"""ImportService -- facade for importing old project data."""

import os
from .pkl_migrator import PklMigrator


class ImportService:
    """Import old project data into new JSON format."""

    def __init__(self):
        self._migrator = None

    def migrate_pkl(self, pkl_path, data_dir):
        """Migrate from old pkl file to new JSON format.

        Returns:
            (tasker_count, task_count) tuple
        """
        m = PklMigrator(pkl_path, data_dir)
        return m.migrate()

    def reload_backup(self, storage_manager, backup_dir):
        """Load backup data and apply."""
        result = storage_manager.reload_from_backup(backup_dir)
        if result is not None:
            storage_manager.apply_backup(backup_dir)
        return result
