"""服务抽象接口——Tasker 管理和 Task 管理的抽象接口。"""

from abc import ABC, abstractmethod

from core.abstract import BaseTasker, BaseTask


class BaseTaskerService(ABC):
    """Tasker 管理的抽象接口"""

    @abstractmethod
    def list_taskers(self) -> list[dict]:
        """返回所有 Tasker 的简要信息列表（id, type, label, description, folder）。

        Returns:
            list[dict]: 每个 dict 为 TaskerSummary 格式
        """
        ...

    @abstractmethod
    def create_tasker(self, tasker_data: dict) -> dict:
        """创建新 Tasker。

        Args:
            tasker_data: {"type": "default", "label": "新容器", "description": ""}

        Returns:
            dict: 新 Tasker 的 TaskerSummary
        """
        ...

    @abstractmethod
    def delete_tasker(self, tasker_id: str) -> bool:
        """删除 Tasker 及其所有数据。

        Returns:
            bool: 成功返回 True，tasker_id 不存在返回 False
        """
        ...

    @abstractmethod
    def update_tasker(self, tasker_id: str, updates: dict) -> dict | None:
        """更新 Tasker 的 label/description。

        Args:
            tasker_id: Tasker 唯一标识
            updates: {"label": "新标签"} 或 {"description": "新描述"} 或同时

        Returns:
            更新后的 TaskerSummary dict，tasker_id 不存在返回 None
        """
        ...

    @abstractmethod
    def get_tasker(self, tasker_id: str) -> BaseTasker | None:
        """获取完整的 Tasker 对象（含 task_list）。

        调用存储层实现两段懒加载。
        """
        ...


class BaseTaskService(ABC):
    """Task 管理的抽象接口"""

    @abstractmethod
    def get_tasks(self, tasker_id: str, offset: int = 0, limit: int = 50) -> list[BaseTask]:
        """获取 Tasker 中指定范围的 Task 列表。

        Args:
            tasker_id: Tasker 唯一标识
            offset: 起始索引（负数表示从末尾倒序，-1 = 最后一条）
            limit: 返回数量上限
        """
        ...

    @abstractmethod
    def create_task(self, tasker_id: str, fields: dict) -> BaseTask:
        """在指定 Tasker 中创建新 Task。

        Args:
            tasker_id: 目标 Tasker
            fields: {"date": "2026_07_11", "attribute": "编程", "content": "...", "comment": ""}
        """
        ...

    @abstractmethod
    def update_task(self, tasker_id: str, task_index: int, updates: dict) -> BaseTask | None:
        """更新指定索引的 Task。

        Args:
            task_index: Task 在 task_list 中的索引
            updates: {"content": "新内容"} —— 只包含要修改的字段
        """
        ...

    @abstractmethod
    def delete_task(self, tasker_id: str, task_index: int) -> bool:
        """删除指定索引的 Task。"""
        ...

    @abstractmethod
    def search_tasks(self, tasker_id: str, query: str) -> list[tuple[int, BaseTask]]:
        """搜索 Tasker 中匹配 query 的 Task。

        Returns:
            list[tuple[int, BaseTask]]: (索引, Task) 列表
        """
        ...
