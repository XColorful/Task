"""Tasker 索引管理——taskers.json 的读写。

管理所有 Tasker 的简要索引。不存储 Task 数量字段（避免每次增删触发 OneDrive 同步）。
所有 JSON 读写保持插入顺序——Tasker 列表顺序 = 文件中的数组顺序。
"""

import os
from collections import OrderedDict
from util.json_utils import JsonUtils


class TaskerIndexManager:
    """管理 taskers.json 的读写。"""

    def __init__(self, data_dir: str):
        self._path = os.path.join(data_dir, 'taskers.json')

    def load(self) -> list[dict]:
        """读取 taskers.json，返回 Tasker 列表（保持 JSON 数组顺序）。

        Returns:
            list[dict]: 每个 dict 包含 id, type, label, description, folder, quick_buttons

        文件不存在时返回空列表。
        """
        try:
            data = JsonUtils.load_json(self._path)
            return data.get('taskers', [])
        except FileNotFoundError:
            return []

    def save(self, taskers: list[dict]) -> None:
        """写入 taskers.json（原子写入）。

        Args:
            taskers: Tasker 列表，顺序即为文件中的数组顺序
        """
        data = OrderedDict()
        data['taskers'] = taskers
        JsonUtils.save_json(self._path, data, atomic=True)

    @property
    def path(self) -> str:
        return self._path
