# SPEC: extensions/timer — 计时器模块

> 对应源码路径: `src/extensions/timer/`

## 1. timer_task.py

```python
from core.abstract import BaseTask
from collections import OrderedDict
from datetime import datetime


class TimerTask(BaseTask):
    """计时器记录 Task。包含起止时间和时长计算。"""

    start_time: str = ""  # "YYYY_MM_DD-HH:MM"
    end_time: str = ""    # "YYYY_MM_DD-HH:MM" ("" = 进行中)

    def __init__(self, date: str = "", attribute: str = "",
                 content: str = "", comment: str = "",
                 start_time: str = "", end_time: str = ""):
        super().__init__()
        self.type = "timer"
        self.version = "timer"
        self.date = date
        self.attribute = attribute
        self.content = content
        self.comment = comment
        self.start_time = start_time
        self.end_time = end_time

    @property
    def is_running(self) -> bool:
        """是否进行中（end_time 为空）"""
        return self.end_time == ""

    @property
    def duration_minutes(self) -> int | None:
        """计算持续分钟数。进行中返回 None。"""
        if self.is_running:
            return None
        fmt = "%Y_%m_%d-%H:%M"
        try:
            t1 = datetime.strptime(self.start_time, fmt)
            t2 = datetime.strptime(self.end_time, fmt)
            return int((t2 - t1).total_seconds() / 60)
        except ValueError:
            return 0

    def to_dict(self) -> OrderedDict:
        return OrderedDict([
            ("type", self.type),
            ("version", self.version),
            ("date", self.date),
            ("attribute", self.attribute),
            ("content", self.content),
            ("comment", self.comment),
            ("start_time", self.start_time),
            ("end_time", self.end_time),
        ])

    @classmethod
    def from_dict(cls, data: dict) -> 'TimerTask':
        return cls(
            date=data.get("date", ""),
            attribute=data.get("attribute", ""),
            content=data.get("content", ""),
            comment=data.get("comment", ""),
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
        )

    def matches_search(self, query: str) -> bool:
        """搜索范围: date, attribute, content, comment, start_time, end_time"""
        q = query.lower()
        return any(q in str(f).lower() for f in [
            self.date, self.attribute, self.content, self.comment,
            self.start_time, self.end_time,
        ])

    def __str__(self) -> str:
        return f"{self.start_time}|{self.end_time}|{self.attribute}|{self.content}"
```

## 2. timer_tasker.py

```python
from core.abstract import BaseTasker, BaseTask


class TimerTasker(BaseTasker):
    """计时器 Tasker。维护进行中/已完成的分类视图。"""

    # 默认配置
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
        """返回所有进行中的 TimerTask 及其索引。"""
        return [(i, t) for i, t in enumerate(self.task_list) if getattr(t, 'is_running', False)]

    def create_task(self, fields: dict) -> BaseTask:
        from .timer_task import TimerTask
        from util.date_utils import now_str
        return TimerTask(
            date=fields.get("date", ""),
            attribute=fields.get("attribute", self.default_attribute),
            content=(self.content_prefix or "") + fields.get("content", self.default_content),
            comment=fields.get("comment", ""),
            start_time=fields.get("start_time", now_str()),
            end_time=fields.get("end_time", ""),
        )

    def end_timer(self, task_index: int) -> bool:
        """结束指定索引的计时，填入当前时间。"""
        if 0 <= task_index < len(self.task_list):
            from util.date_utils import now_str
            task = self.task_list[task_index]
            if getattr(task, 'is_running', False):
                task.end_time = now_str()
                # 标记所在 segment 为 dirty（由调用方或存储服务处理）
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
            "start_time": now_str(),
            "end_time": "",
        }
        if not fields["content"]:
            return None
        return self.create_task(fields)

    def mark_dirty(self, segment_filename: str) -> None:
        self.dirty_segments.add(segment_filename)
```

## 3. duration_calculator.py

```python
class DurationCalculator:
    """纯计算工具——格式化时长和跨日天数统计。"""

    @staticmethod
    def format_duration(minutes: int) -> str:
        """格式化分钟数为可读字符串。
        >>> DurationCalculator.format_duration(3255)
        ' 2d  6h 15m'
        """
        if minutes < 0:
            return "Error"
        days, remainder = divmod(minutes, 1440)
        hours, minutes = divmod(remainder, 60)
        parts = []
        if days > 0: parts.append(f"{days:>2}d")
        if hours > 0: parts.append(f"{hours:>2}h")
        if minutes > 0: parts.append(f"{minutes:>2}m")
        return " ".join(parts) if parts else " 0m"

    @staticmethod
    def get_days_list(start_time: str, end_time: str | None = None) -> list[str]:
        """返回从 start_time 到 end_time（或现在）之间的所有日期 "YYYY_MM_DD" 列表。"""
        ...
```

## 4. __init__.py

```python
from core.extension_registry import ExtensionRegistry
from .timer_task import TimerTask
from .timer_tasker import TimerTasker

ExtensionRegistry.register_task_type("timer", TimerTask)
ExtensionRegistry.register_tasker_type("timer", TimerTasker)
ExtensionRegistry.register_chart_page("duration", "extensions/timer/charts/duration.html")
ExtensionRegistry.register_chart_page("3d_monthly", "extensions/timer/charts/3d_monthly.html")
```
