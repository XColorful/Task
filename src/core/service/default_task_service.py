"""Default Task Service -- Task CRUD default implementation."""

from core.base_service import BaseTaskService
from core.storage.storage_manager import StorageManager
from core.abstract import BaseTask, BaseTasker


class DefaultTaskService(BaseTaskService):
    """Task CRUD default implementation."""

    def __init__(self, storage: StorageManager, tasker_service=None):
        self._storage = storage
        if tasker_service is not None:
            self._tasker_service = tasker_service
        else:
            from core.service.default_tasker_service import DefaultTaskerService
            self._tasker_service = DefaultTaskerService(storage)

    def get_tasks(self, tasker_id, offset=0, limit=50):
        tasker = self._get_tasker_with_tasks(tasker_id)
        if tasker is None:
            return []
        task_list = tasker.task_list
        if offset < 0:
            start = max(0, len(task_list) + offset)
        else:
            start = offset
        end = min(start + limit, len(task_list))
        return task_list[start:end]

    def create_task(self, tasker_id, fields):
        tasker = self._get_tasker_with_tasks(tasker_id)
        if tasker is None:
            return None
        task = tasker.create_task(fields)
        tasker.task_list.append(task)
        files = self._storage.list_segment_files(tasker.folder)
        if files:
            tasker.mark_dirty(files[-1])
        return task

    def update_task(self, tasker_id, task_index, updates):
        tasker = self._get_tasker_with_tasks(tasker_id)
        if tasker is None or not (0 <= task_index < len(tasker.task_list)):
            return None
        task = tasker.task_list[task_index]
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        files = self._storage.list_segment_files(tasker.folder)
        max_per_seg = 500
        seg_idx = task_index // max_per_seg
        if seg_idx < len(files):
            tasker.mark_dirty(files[seg_idx])
        return task

    def delete_task(self, tasker_id, task_index):
        tasker = self._get_tasker_with_tasks(tasker_id)
        if tasker is None or not (0 <= task_index < len(tasker.task_list)):
            return False
        del tasker.task_list[task_index]
        files = self._storage.list_segment_files(tasker.folder)
        max_per_seg = 500
        seg_idx = task_index // max_per_seg
        if seg_idx < len(files):
            tasker.mark_dirty(files[seg_idx])
        return True

    def search_tasks(self, tasker_id, query):
        tasker = self._get_tasker_with_tasks(tasker_id)
        if tasker is None:
            return []
        results = []
        for i, task in enumerate(tasker.task_list):
            if task.matches_search(query):
                results.append((i, task))
        return results

    def _get_tasker_with_tasks(self, tasker_id):
        return self._tasker_service.get_tasker(tasker_id)
