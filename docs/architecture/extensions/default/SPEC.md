# SPEC: extensions/default — 默认四字段日常记录

> 对应源码路径: `src/extensions/default/`
> 最基础且最常用的记录类型。每个 Task 包含 date, attribute, content, comment 四个字段。

## 1. default_task.py

```python
from core.abstract import BaseTask

class DefaultTask(BaseTask):
    """四字段日常记录 Task。"""

    # 继承 BaseTask 的全部字段: type, version, date, attribute, content, comment

    def __init__(self, date: str = "", attribute: str = "N/A",
                 content: str = "", comment: str = ""):
        super().__init__()
        self.type = "default"
        self.version = "1.0"
        self.date = date
        self.attribute = attribute
        self.content = content
        self.comment = comment

    def to_dict(self) -> dict:
        """序列化——字段顺序: type, version, date, attribute, content, comment"""
        from collections import OrderedDict
        return OrderedDict([
            ("type", self.type),
            ("version", self.version),
            ("date", self.date),
            ("attribute", self.attribute),
            ("content", self.content),
            ("comment", self.comment),
        ])

    @classmethod
    def from_dict(cls, data: dict) -> 'DefaultTask':
        return cls(
            date=data.get("date", ""),
            attribute=data.get("attribute", "N/A"),
            content=data.get("content", ""),
            comment=data.get("comment", ""),
        )

    def matches_search(self, query: str) -> bool:
        """搜索范围: date, attribute, content, comment"""
        q = query.lower()
        return any(q in str(f).lower() for f in [
            self.date, self.attribute, self.content, self.comment
        ])

    def __str__(self) -> str:
        return f"{self.date}|{self.attribute}|{self.content}"
```

## 2. default_tasker.py

```python
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
        """从字段 dict 创建 DefaultTask。

        fields 应包含: date (可选, 默认今天), attribute (可选, 默认 "N/A"),
                       content, comment (可选)
        """
        from .default_task import DefaultTask
        from util.date_utils import today_str
        return DefaultTask(
            date=fields.get("date", today_str()),
            attribute=fields.get("attribute", "N/A"),
            content=fields.get("content", ""),
            comment=fields.get("comment", ""),
        )

    def execute_quick_button(self, button_template: dict) -> BaseTask | None:
        """从外部触发快捷按钮。

        Args:
            button_template: QuickButtonDef 格式的 dict
                {"command": "hw", "label": "记作业",
                 "preset": {"attribute": "作业", "use_default_date": true}}

        Returns:
            创建的 Task 或 None（content 为空且用户取消输入时）
        """
        preset = button_template.get("preset", {})
        from util.date_utils import today_str
        fields = {
            "date": today_str() if preset.get("use_default_date") else preset.get("date", today_str()),
            "attribute": preset.get("attribute", "N/A"),
            "content": preset.get("content", ""),
            "comment": preset.get("comment", ""),
        }
        # content 为空时由 UI 弹出输入框——此处返回标记由调用方处理
        if not fields["content"]:
            return None  # 调用方应弹出输入框补充 content 后再次调用
        return self.create_task(fields)

    def mark_dirty(self, segment_filename: str) -> None:
        """标记 segment 为脏"""
        self.dirty_segments.add(segment_filename)
```

## 3. __init__.py — 注册

```python
from core.extension_registry import ExtensionRegistry
from core.input_processor import InputPreprocessor, step_plus_to_search
from .default_task import DefaultTask
from .default_tasker import DefaultTasker

# 注册类型
ExtensionRegistry.register_task_type("default", DefaultTask)
ExtensionRegistry.register_tasker_type("default", DefaultTasker)

# 注册图表页面
ExtensionRegistry.register_chart_page("attr_count", "extensions/default/charts/attr_count.html")
ExtensionRegistry.register_chart_page("monthly_count", "extensions/default/charts/monthly_count.html")

# 注册输入预处理步骤（仅一次，由首先加载的扩展模块执行）
InputPreprocessor.register_step(step_plus_to_search)
```
