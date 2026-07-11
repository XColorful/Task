"""Search Engine —— 基于已加载 task_list 的全文搜索。"""

from core.storage.storage_manager import StorageManager
from core.abstract import BaseTask


class SearchEngine:
    """全文搜索引擎。不扫描未加载的 segment。"""

    def __init__(self, storage: StorageManager, tasker_service=None):
        self._storage = storage
        if tasker_service is not None:
            self._tasker_service = tasker_service
        else:
            from core.service.default_tasker_service import DefaultTaskerService
            self._tasker_service = DefaultTaskerService(storage)

    def search(self, tasker_id: str, query: str) -> list[tuple[int, BaseTask]]:
        tasker = self._tasker_service.get_tasker(tasker_id)
        if tasker is None:
            return []
        results = []
        for i, task in enumerate(tasker.task_list):
            if task.matches_search(query):
                results.append((i, task))
        return results

    def search_all_taskers(self, query: str) -> dict[str, list[tuple[int, BaseTask]]]:
        """跨所有已加载 Tasker 搜索（预留）。"""
        taskers = self._storage.tasker_index.load()
        result = {}
        for t in taskers:
            hits = self.search(t['id'], query)
            if hits:
                result[t['id']] = hits
        return result
