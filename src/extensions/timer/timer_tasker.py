"""Timer Tasker — 计时器记录容器。"""

from core.abstract import BaseTasker, BaseTask


class TimerTasker(BaseTasker):
    """计时器 Tasker。"""

    default_attribute: str = ""
    default_content: str = ""
    content_prefix: str = ""

    def __init__(self, tasker_id: str = "", label: str = "",
                 description: str = "", folder: str = ""):
        super().__init__()
        self.type = "timer"
        self.version = "timer"
        self.tasker_id = tasker_id
        self.label = label
        self.description = description
        self.folder = folder

    def get_commands(self) -> list[str]:
        return ["new", "edit", "config", "delete", "search", "end", "categorize"]

    def get_running_tasks(self) -> list[tuple[int, BaseTask]]:
        return [(i, t) for i, t in enumerate(self.task_list) if getattr(t, 'is_running', False)]

    def create_task(self, fields: dict) -> BaseTask:
        from .timer_task import TimerTask
        from util.date_utils import now_str, today_str
        return TimerTask(
            create_date=fields.get("create_date", today_str()),
            date=fields.get("date", ""),
            attribute=fields.get("attribute", self.default_attribute),
            content=(self.content_prefix or "") + fields.get("content", self.default_content),
            comment=fields.get("comment", ""),
            start_time=fields.get("start_time", now_str()),
            end_time=fields.get("end_time", ""),
        )

    def end_timer(self, task_index: int) -> bool:
        if 0 <= task_index < len(self.task_list):
            from util.date_utils import now_str
            task = self.task_list[task_index]
            if getattr(task, 'is_running', False):
                task.end_time = now_str()
                return True
        return False

    def execute_quick_button(self, button_template: dict) -> BaseTask | None:
        preset = button_template.get("preset", {})
        from util.date_utils import now_str, today_str
        fields = {
            "date": today_str() if preset.get("use_default_date") else preset.get("date", today_str()),
            "attribute": preset.get("attribute", self.default_attribute),
            "content": preset.get("content", ""),
            "comment": preset.get("comment", ""),
            "create_date": today_str(),
            "start_time": now_str(),
            "end_time": "",
        }
        if not fields["content"]:
            return None
        return self.create_task(fields)
