"""Default Tasker Service -- Tasker CRUD default implementation."""

import uuid
import os
import shutil
from collections import OrderedDict
from core.base_service import BaseTaskerService
from core.storage.storage_manager import StorageManager
from core.extension_registry import ExtensionRegistry
from core.abstract import BaseTasker


class DefaultTaskerService(BaseTaskerService):

    def __init__(self, storage):
        self._storage = storage
        self._tasker_cache = {}

    def list_taskers(self):
        return self._storage.tasker_index.load()

    def create_tasker(self, tasker_data):
        tasker_type = tasker_data.get("type", "default")
        label = tasker_data.get("label", "")
        description = tasker_data.get("description", "")
        tasker_id = uuid.uuid4().hex[:12]
        folder = f"{label}_{tasker_id}"

        seg_dir = os.path.join(self._storage.data_dir, folder)
        os.makedirs(seg_dir, exist_ok=True)
        from util.json_utils import JsonUtils
        JsonUtils.save_json(
            os.path.join(seg_dir, "segment_0001.json"),
            OrderedDict([("tasks", [])]),
            atomic=True,
        )

        tasker_summary = OrderedDict([
            ("id", tasker_id),
            ("type", tasker_type),
            ("label", label),
            ("description", description),
            ("folder", folder),
            ("quick_buttons", []),
        ])
        taskers = self._storage.tasker_index.load()
        taskers.append(tasker_summary)
        self._storage.tasker_index.save(taskers)

        return dict(tasker_summary)

    def delete_tasker(self, tasker_id):
        taskers = self._storage.tasker_index.load()
        for i, t in enumerate(taskers):
            if t['id'] == tasker_id:
                folder = t['folder']
                del taskers[i]
                self._storage.tasker_index.save(taskers)
                folder_path = os.path.join(self._storage.data_dir, folder)
                if os.path.isdir(folder_path):
                    shutil.rmtree(folder_path)
                self._tasker_cache.pop(tasker_id, None)
                return True
        return False

    def update_tasker(self, tasker_id, updates):
        taskers = self._storage.tasker_index.load()
        for t in taskers:
            if t['id'] == tasker_id:
                if 'label' in updates:
                    t['label'] = updates['label']
                if 'description' in updates:
                    t['description'] = updates['description']
                self._storage.tasker_index.save(taskers)
                return dict(t)
        return None

    def get_tasker(self, tasker_id):
        if tasker_id in self._tasker_cache:
            return self._tasker_cache[tasker_id]

        taskers = self._storage.tasker_index.load()
        for t in taskers:
            if t['id'] == tasker_id:
                tasker_type = t['type']
                try:
                    tasker = ExtensionRegistry.create_tasker(
                        tasker_type,
                        tasker_id=t['id'],
                        label=t['label'],
                        description=t.get('description', ''),
                        folder=t['folder'],
                    )
                except KeyError:
                    return None

                tasks_dict = self._storage.segment.load_last(t['folder'], count=2)
                last_files = self._storage.segment.list_files(t['folder'])
                loaded = set(last_files[-2:]) if len(last_files) >= 2 else set(last_files)
                tasker.loaded_segments = loaded
                tasker._partial_load = len(last_files) > 2
                tasker._total_task_count = self._storage.segment.count_tasks(t['folder'])
                if tasks_dict:
                    tasker.task_list = [self._create_task_from_dict(td, tasker_type) for td in tasks_dict]

                self._tasker_cache[tasker_id] = tasker
                return tasker
        return None

    def _create_task_from_dict(self, data, tasker_type):
        cls = ExtensionRegistry._task_types.get(tasker_type)
        if cls is None:
            cls = ExtensionRegistry._task_types.get('default')
        if cls is None:
            raise KeyError(f"No task