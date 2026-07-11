# SPEC: extensions/label — 自定义标签模块

> 对应源码路径: `src/extensions/label/`
> 为 Task 附加自定义 key-value 标签对，支持按标签搜索和过滤。每个 LabelTask 可携带任意数量的标签，标签以 `(key, value)` 元组列表存储。

## 1. label_task.py

```python
from core.abstract import BaseTask
from collections import OrderedDict


class LabelTask(BaseTask):
    """带自定义标签的 Task。

    额外字段:
        label_list: 标签列表，每项为 (key, value) 二元组。
                    value 可以为空字符串，表示无值标签（仅 key 起标记作用）。

    示例标签:
        [("priority", "high"), ("project", "Task"), ("reviewed", "")]
    """

    label_list: list[tuple[str, str]]

    def __init__(
        self,
        date: str = "",
        attribute: str = "",
        content: str = "",
        comment: str = "",
        label_list: list[tuple[str, str]] | None = None,
    ):
        super().__init__()
        self.type = "label"
        self.version = "1.0"
        self.date = date
        self.attribute = attribute
        self.content = content
        self.comment = comment
        self.label_list = label_list or []

    # ------------------------------------------------------------------
    # 序列化
    # ------------------------------------------------------------------

    def to_dict(self) -> OrderedDict:
        """序列化——字段顺序:
        type, version, date, attribute, content, comment, label_list

        label_list 序列化为 list[list[str]]，保持插入顺序。
        """
        return OrderedDict([
            ("type", self.type),
            ("version", self.version),
            ("date", self.date),
            ("attribute", self.attribute),
            ("content", self.content),
            ("comment", self.comment),
            ("label_list", [list(pair) for pair in self.label_list]),
        ])

    @classmethod
    def from_dict(cls, data: dict) -> 'LabelTask':
        """从字典反序列化。

        label_list 从 list[list[str]] 解析为 list[tuple[str, str]]。
        缺失或格式异常时默认为空列表。
        """
        raw_labels = data.get("label_list", [])
        parsed_labels: list[tuple[str, str]] = []
        if isinstance(raw_labels, list):
            for item in raw_labels:
                if isinstance(item, list) and len(item) >= 2:
                    parsed_labels.append((str(item[0]), str(item[1])))
                elif isinstance(item, list) and len(item) == 1:
                    parsed_labels.append((str(item[0]), ""))
        return cls(
            date=data.get("date", ""),
            attribute=data.get("attribute", ""),
            content=data.get("content", ""),
            comment=data.get("comment", ""),
            label_list=parsed_labels,
        )

    # ------------------------------------------------------------------
    # 搜索
    # ------------------------------------------------------------------

    def matches_search(self, query: str) -> bool:
        """搜索范围: date, attribute, content, comment, label_list 所有 key 和 value。

        标签搜索同时匹配 key 和 value，例如 query="priority" 能命中
        label_list 中任意 key 或 value 包含 "priority" 的条目。
        """
        q = query.lower()
        # 标准字段
        if any(q in str(f).lower() for f in [
            self.date, self.attribute, self.content, self.comment,
        ]):
            return True
        # 标签字段
        for key, value in self.label_list:
            if q in key.lower() or q in value.lower():
                return True
        return False

    # ------------------------------------------------------------------
    # 标签操作
    # ------------------------------------------------------------------

    def get_label(self, key: str) -> str | None:
        """获取指定 key 的第一个 value。不存在返回 None。

        若同一 key 存在多条，仅返回第一条。
        """
        for k, v in self.label_list:
            if k == key:
                return v
        return None

    def get_labels(self, key: str) -> list[str]:
        """获取指定 key 的所有 value（允许同 key 多条标签）。"""
        return [v for k, v in self.label_list if k == key]

    def set_label(self, key: str, value: str = "") -> None:
        """设置标签——若 key 已存在则更新第一条的 value，否则追加新条目。"""
        for i, (k, _) in enumerate(self.label_list):
            if k == key:
                self.label_list[i] = (key, value)
                return
        self.label_list.append((key, value))

    def remove_label(self, key: str, value: str | None = None) -> int:
        """移除匹配的标签。value 为 None 时移除该 key 的全部条目。
        返回实际移除的条数。
        """
        before = len(self.label_list)
        if value is None:
            self.label_list = [(k, v) for k, v in self.label_list if k != key]
        else:
            self.label_list = [
                (k, v) for k, v in self.label_list
                if not (k == key and v == value)
            ]
        return before - len(self.label_list)

    def has_label(self, key: str, value: str | None = None) -> bool:
        """是否存在指定标签。value 为 None 时仅检查 key 是否存在。"""
        for k, v in self.label_list:
            if k == key and (value is None or v == value):
                return True
        return False

    # ------------------------------------------------------------------
    # 显示
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        labels_str = ", ".join(
            f"{k}={v}" if v else k for k, v in self.label_list
        )
        base = f"{self.date}|{self.attribute}|{self.content}"
        if labels_str:
            return f"{base} [{labels_str}]"
        return base
```

## 2. label_tasker.py

```python
from core.abstract import BaseTasker, BaseTask
from core.types import QuickButtonDef


class LabelTasker(BaseTasker):
    """标签 Tasker。管理带标签的 Task，支持按标签过滤。

    标签过滤:
        - filter 指令按 key 或 key+value 筛选 task_list
        - 搜索结果可与标签过滤叠加使用
        - filter_by_label 返回匹配的索引列表，不修改 task_list
    """

    def __init__(
        self,
        tasker_id: str = "",
        label: str = "",
        description: str = "",
        folder: str = "",
        quick_buttons: list[QuickButtonDef] | None = None,
    ):
        super().__init__()
        self.type = "label"
        self.version = "1.0"
        self.tasker_id = tasker_id
        self.label = label
        self.description = description
        self.folder = folder
        self._quick_buttons: list[QuickButtonDef] = quick_buttons or []

    # ------------------------------------------------------------------
    # 指令集
    # ------------------------------------------------------------------

    def get_commands(self) -> list[str]:
        return ["new", "search", "edit", "delete", "filter"]

    # ------------------------------------------------------------------
    # 标签过滤
    # ------------------------------------------------------------------

    def filter_by_label(
        self, key: str, value: str | None = None
    ) -> list[int]:
        """按标签过滤，返回匹配的 task_list 索引列表。

        Args:
            key: 标签 key（必选）
            value: 标签 value。None 表示匹配该 key 的任意值（包括空值）。

        Returns:
            list[int]: 匹配 task 在 task_list 中的索引，保持原顺序。

        示例:
            tasker.filter_by_label("priority")          → 所有含 priority 标签的索引
            tasker.filter_by_label("priority", "high")  → priority=high 的索引
        """
        from .label_task import LabelTask

        result: list[int] = []
        for i, task in enumerate(self.task_list):
            if not isinstance(task, LabelTask):
                continue
            if task.has_label(key, value):
                result.append(i)
        return result

    def get_all_label_keys(self) -> list[str]:
        """获取 task_list 中所有出现过的标签 key（去重，按首次出现排序）。"""
        from .label_task import LabelTask

        seen: set[str] = set()
        keys: list[str] = []
        for task in self.task_list:
            if not isinstance(task, LabelTask):
                continue
            for k, _ in task.label_list:
                if k not in seen:
                    seen.add(k)
                    keys.append(k)
        return keys

    def get_label_values(self, key: str) -> list[str]:
        """获取指定 key 的所有不同 value（去重，按首次出现排序）。"""
        from .label_task import LabelTask

        seen: set[str] = set()
        values: list[str] = []
        for task in self.task_list:
            if not isinstance(task, LabelTask):
                continue
            for v in task.get_labels(key):
                if v not in seen:
                    seen.add(v)
                    values.append(v)
        return values

    # ------------------------------------------------------------------
    # Task 生命周期
    # ------------------------------------------------------------------

    def create_task(self, fields: dict) -> BaseTask:
        """从字段 dict 创建 LabelTask。

        fields 可包含:
            date, attribute, content, comment (继承自 BaseTask)
            label_list (list[tuple[str, str]] | list[list[str]])
        """
        from .label_task import LabelTask
        from util.date_utils import today_str

        raw_labels = fields.get("label_list", [])
        parsed_labels: list[tuple[str, str]] = []
        if isinstance(raw_labels, list):
            for item in raw_labels:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    parsed_labels.append((str(item[0]), str(item[1])))
                elif isinstance(item, (list, tuple)) and len(item) == 1:
                    parsed_labels.append((str(item[0]), ""))

        return LabelTask(
            date=fields.get("date", today_str()),
            attribute=fields.get("attribute", ""),
            content=fields.get("content", ""),
            comment=fields.get("comment", ""),
            label_list=parsed_labels,
        )

    def execute_quick_button(self, button_template: dict) -> BaseTask | None:
        """快捷按钮触发。preset 中可预填 label_list 等字段。"""
        preset = button_template.get("preset", {})
        from util.date_utils import today_str
        fields = {
            "date": today_str() if preset.get("use_default_date") else preset.get("date", today_str()),
            "attribute": preset.get("attribute", ""),
            "content": preset.get("content", ""),
            "comment": preset.get("comment", ""),
            "label_list": preset.get("label_list", []),
        }
        if not fields["content"]:
            return None
        return self.create_task(fields)

    def mark_dirty(self, segment_filename: str) -> None:
        self.dirty_segments.add(segment_filename)
```

## 3. __init__.py — 注册

```python
from core.extension_registry import ExtensionRegistry
from .label_task import LabelTask
from .label_tasker import LabelTasker

# 注册 Task / Tasker 类型
ExtensionRegistry.register_task_type("label", LabelTask)
ExtensionRegistry.register_tasker_type("label", LabelTasker)

# 注册图表页面（预留）
ExtensionRegistry.register_chart_page("label_count", "extensions/label/charts/label_count.html")
```

## 4. 依赖关系

```
extensions/label/
├── label_task.py          # 依赖 core.abstract.BaseTask + collections.OrderedDict
├── label_tasker.py        # 依赖 core.abstract.BaseTasker + core.types.QuickButtonDef
└── __init__.py            # 依赖 core.extension_registry.ExtensionRegistry
```

## 5. 数据流

### 5.1 按标签过滤

```
用户输入: "filter priority high"
  │
  ▼
LabelTasker.filter_by_label("priority", "high")
  │
  ├─ 遍历 task_list
  ├─ 对每个 LabelTask 调用 task.has_label("priority", "high")
  │   └─ 遍历 label_list，匹配 key="priority" 且 value="high"
  │
  └─ 返回 [index, ...] —— 匹配的 task 索引列表
       │
       ├─ 空列表 → UI: "无匹配结果"
       └─ 有结果 → UI: 在表格中仅展示匹配索引对应的行
```

### 5.2 标签搜索

```
用户输入: "search urgent"
  │
  ▼
LabelTasker 遍历 task_list → 每个 LabelTask.matches_search("urgent")
  │
  ├─ date, attribute, content, comment 字段匹配
  └─ label_list 中任意 key 或 value 匹配
       │
       └─ 例如 label_list = [("priority", "urgent")]
          → "urgent" 命中 key="priority"(否) 和 value="urgent"(是) → 返回 True
```

### 5.3 创建带标签的 Task

```
用户输入: "new #priority=high #project=Task 完成登录模块"
  │
  ▼
InputParser 解析 content="完成登录模块"，提取标签:
  label_list = [("priority", "high"), ("project", "Task")]
  │
  ▼
LabelTasker.create_task({
    "date": today_str(),
    "attribute": "",
    "content": "完成登录模块",
    "comment": "",
    "label_list": [("priority", "high"), ("project", "Task")],
})
  │
  ▼
LabelTask 实例:
  date="2026_07_11"
  content="完成登录模块"
  label_list=[("priority", "high"), ("project", "Task")]
```

## 6. label_list 存储格式

label_list 在 segment JSON 中的存储形式为二维数组:

```json
{
  "type": "label",
  "version": "1.0",
  "date": "2026_07_11",
  "attribute": "",
  "content": "完成登录模块",
  "comment": "",
  "label_list": [
    ["priority", "high"],
    ["project", "Task"],
    ["reviewed", ""]
  ]
}
```

- 每条标签为 `[key, value]`，value 可以为空字符串 `""`
- 空 label_list 写为 `[]`
- to_dict() 将 `list[tuple[str, str]]` 转为 `list[list[str, str]]` 后写入 JSON
- from_dict() 将 `list[list[str, str]]` 解析回 `list[tuple[str, str]]`
