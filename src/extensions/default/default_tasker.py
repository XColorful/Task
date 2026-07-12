"""Default Tasker — 默认四字段记录容器。"""

from core.abstract import BaseTasker, BaseTask
from core.types import QuickButtonDef


class DefaultTasker(BaseTasker):
    """默认 Tasker——四字段 CRUD。"""

    def __init__(self, tasker_id: str = "", label: str = "",
                 description: str = "", folder: str = "",
                 quick_buttons: list[QuickButtonDef] | None = None):
        super().__init__()
        self.type = "default"
        self.version = "1.0"
        self.tasker_id = tasker_id
        self.label = label
        self.description = description
        self.folder = folder
        self._quick_buttons: list[QuickButtonDef] = quick_buttons or []

    def get_commands(self) -> list[str]:
        return ["search", "new", "delete", "edit", "backup", "reload"]

    def create_task(self, fields: dict) -> BaseTask:
        from .default_task import DefaultTask
        from util.date_utils import today_str
        return DefaultTask(
            date=fields.get("date", today_str()),
            attribute=fields.get("attribute", "N/A"),
            content=fields.get("content", ""),
            comment=fields.get("comment", ""),
        )

    def execute_quick_button(self, button_template: dict) -> BaseTask | None:
        preset = button_template.get("preset", {})
        from util.date_utils import today_str
        fields = {
            "date": today_str() if preset.get("use_default_date") else preset.get("date", today_str()),
            "attribute": preset.get("attribute", "N/A"),
            "content": preset.get("content", ""),
            "comment": preset.get("comment", ""),
        }
        if not fields["content"]:
            return None
        return self.create_task(fields)

    def mark_dirty(self, segment_filename: str) -> None:
        self.dirty_segments.add(segment_filename)
