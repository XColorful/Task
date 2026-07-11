# SPEC: core/service — 默认服务实现

> 对应源码路径: `src/core/service/`
> 提供 BaseTaskerService / BaseTaskService 的默认实现。扩展模块可替换任一服务。

## 1. default_tasker_service.py

```python
from core.base_service import BaseTaskerService
from core.storage.storage_manager import StorageManager
from core.extension_registry import ExtensionRegistry
from core.types import TaskerSummary
from core.abstract import BaseTasker


class DefaultTaskerService(BaseTaskerService):
    """Tasker CRUD 的默认实现。"""

    def __init__(self, storage: StorageManager):
        """
        Args:
            storage: StorageManager 实例（由 main 创建后注入）
        """
        self._storage = storage

    def list_taskers(self) -> list[TaskerSummary]:
        """返回 taskers.json 中的 Tasker 列表（保持 JSON 顺序）。"""
        return self._storage.tasker_index.load()

    def create_tasker(self, tasker_data: dict) -> TaskerSummary:
        """
        Args:
            tasker_data: {"type": "default", "label": "新容器", "description": ""}

        Returns:
            新建 Tasker 的 TaskerSummary

        行为:
        1. 生成唯一 id (uuid4)
        2. 创建文件夹 "{label}_{id前8位}"
        3. 调用 ExtensionRegistry.create_tasker(type) 创建 BaseTasker 实例
        4. 追加到 taskers.json
        5. 创建空 segment_0001.json（空 tasks 数组）
        6. 保存 taskers.json
        """
        ...

    def delete_tasker(self, tasker_id: str) -> bool:
        """
        删除 Tasker 及其文件夹下全部数据。taskers.json 中移除该项。

        Returns:
            bool: 成功返回 True，tasker_id 不存在返回 False
        """
        ...

    def update_tasker(self, tasker_id: str, updates: dict) -> TaskerSummary | None:
        """
        Args:
            tasker_id: Tasker 唯一标识
            updates: {"label": "新标签"} 或 {"description": "新描述"} 或同时

        Returns:
            更新后的 TaskerSummary。tasker_id 不存在返回 None
        """
        ...

    def get_tasker(self, tasker_id: str) -> BaseTasker | None:
        """
        获取完整 Tasker 对象（含 task_list）。
        调用 storage.segment.load_last() 实现两段懒加载。

        Returns:
            BaseTasker 实例。tasker_id 不存在或 Tasker 类型无注册返回 None
        """
        ...

    def reorder_taskers(self, new_order: list[str]) -> None:
        """
        按 new_order 中的 tasker_id 顺序重排 taskers.json。
        new_order 必须是当前所有 Tasker 的全排列。
        """
        ...
```

## 2. default_task_service.py

```python
from core.base_service import BaseTaskService
from core.storage.storage_manager import StorageManager
from core.abstract import BaseTask
from core.types import SearchQuery


class DefaultTaskService(BaseTaskService):
    """Task CRUD 的默认实现。"""

    def __init__(self, storage: StorageManager):
        self._storage = storage

    def get_tasks(self, tasker_id: str, offset: int = 0, limit: int = 50) -> list[BaseTask]:
        """
        获取 Tasker 中指定范围的 Task。

        Args:
            tasker_id: Tasker 唯一标识
            offset: 起始索引（负数表示从末尾倒序，-1 = 最后一条）
            limit: 返回数量上限

        行为:
        - offset >= 0 → 先检查已加载段是否覆盖 → 否则触发全量加载
        - offset < 0 → 在已加载段内查找 → 超出则加载更早段
        """
        ...

    def create_task(self, tasker_id: str, fields: dict) -> BaseTask:
        """
        Args:
            tasker_id: 目标 Tasker
            fields: {"date": "2026_07_11", "attribute": "编程",
                     "content": "写SPEC", "comment": ""}

        行为:
        1. 通过 ExtensionRegistry.create_task(tasker.type) 创建 BaseTask 实例
        2. 调用 task.from_dict() 或直接设置字段
        3. 追加到 tasker.task_list
        4. 标记最新 segment 为 dirty
        5. 触发 auto_save
        """
        ...

    def update_task(self, tasker_id: str, task_index: int, updates: dict) -> BaseTask | None:
        """
        Args:
            task_index: Task 在 task_list 中的索引
            updates: {"content": "新内容"} —— 只包含要修改的字段

        行为:
        1. 修改 task_list[task_index] 的对应字段
        2. 标记该 task 所在 segment 为 dirty
        3. 触发 auto_save
        """
        ...

    def delete_task(self, tasker_id: str, task_index: int) -> bool:
        """
        删除指定索引的 Task。
        - 标记所在 segment 为 dirty
        - 触发 auto_save
        """
        ...

    def search_tasks(self, tasker_id: str, query: str) -> list[tuple[int, BaseTask]]:
        """
        在当前已加载的 task_list 中搜索。调用 BaseTask.matches_search()。
        返回 (task_list 中的索引, Task) 列表。
        """
        ...
```

## 3. search_engine.py — 全文搜索

```python
from core.storage.storage_manager import StorageManager

class SearchEngine:
    """基于已加载 task_list 的全文搜索。"""

    def __init__(self, storage: StorageManager):
        self._storage = storage

    def search(self, tasker_id: str, query: str) -> list[tuple[int, BaseTask]]:
        """
        在当前已加载的 task_list 中搜索。
        不扫描未加载的 segment——用户需先进入 Tasker 触发两段加载或全量加载。

        调用每个 Task 的 matches_search(query) 方法。
        扩展模块自行决定搜索范围。

        Returns:
            list[tuple[int, BaseTask]]: (task_list 索引, Task 实例)
        """
        ...

    def search_all_taskers(self, query: str) -> dict[str, list[tuple[int, BaseTask]]]:
        """
        跨所有已加载 Tasker 搜索。返回 {tasker_id: [(index, Task), ...]}。
        用于全局搜索场景（预留）。
        """
        ...
```

## 4. 依赖关系

```
core/service/
├── default_tasker_service.py  # 依赖 core/abstract.py, core/storage, core/extension_registry.py, core/types.py
├── default_task_service.py    # 依赖同上
├── search_engine.py           # 依赖 core/storage, core/abstract.py
└── __init__.py
```
