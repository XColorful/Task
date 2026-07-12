"""Label Tasker — 标签记录容器。支持按标签筛选。"""

from core.abstract import BaseTasker, BaseTask


class LabelTasker(BaseTasker):
    """标签 Tasker。"""

    def __init__(self, tasker_id: str = "", label: str = "",
                 description: str = "", folder: str = ""):
        super().__init__()
        self.type = "label"
        self.version = "label"
        self.tasker_id = tasker_id
        self.label = label
        self.description = description
        self.folder = folder

    def get_commands(self) -> list[str]:
        return ["new", "search", "edit", "delete", "filter"]

    def filter_by_label(self, key: str, value: str | None = None) -> list[tuple[int, BaseTask]]:
        """按标签筛选。value 为 None 时只匹配 key。"""
        results = []
        for i, t in enumerate(self.task_list):
            labels = getattr(t, 'label_list', [])
            for k, v in labels:
                if k == key and (value is None or v == value):
                    results.append((i, t))
                    break
        return results

    def get_all_label_keys(self) -> list[str]:
        keys = set()
        for t in self.task_list:
            for k, _ in getattr(t, 'label_list', []):
                keys.add(k)
        return sorted(keys)

    def create_task(self, fields: dict) -> BaseTask:
        from .label_task import LabelTask
        return LabelTask(
            date=fields.get("date", ""),
            attribute=fields.get("attribute", ""),
            content=fields.get("content", ""),
            comment=fields.get("comment", ""),
            label_list=fields.get("label_list", []),
        )

    def execute_quick_button(self, button_template: dict) -> BaseTask | None:
        return self.create_task(button_template.get("preset", {}))

    def mark_dirty(self, segment_filename: str) -> None:
        self.dirty_segments.add(segment_filename)
