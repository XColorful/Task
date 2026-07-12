# SPEC: core — 核心抽象层

> 对应源码路径: `src/core/`
> 本目录定义系统所有抽象基类、注册机制和跨层数据类型。**不包含任何具体记录类型的业务逻辑。**

## 1. abstract.py — 抽象基类

### 1.1 BaseTask

所有 Task 的抽象父类。扩展模块必须继承此类。

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class BaseTask(ABC):
    """单条记录的抽象基类"""

    # --- 核心字段（所有 Task 共有）---
    type: str = ""          # 记录类型标识 ("default", "timer", "account", ...)
    version: str = ""       # 版本号
    date: str = ""          # 事件日期 "YYYY_MM_DD"
    attribute: str = ""     # 属性/分类
    content: str = ""       # 内容文本
    comment: str = ""       # 注释

    # --- 抽象方法（扩展模块必须实现）---
    @abstractmethod
    def to_dict(self) -> dict:
        """序列化为字典，保持字段插入顺序。用于 JSON 写入"""
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'BaseTask':
        """从字典反序列化。data 是从 segment JSON 读取的单条记录 dict"""
        ...

    @abstractmethod
    def matches_search(self, query: str) -> bool:
        """判断此 Task 是否匹配搜索词。
        各扩展模块自行决定搜索范围（如 default 搜索 date/attribute/content/comment，
        timer 额外搜索 start_time/end_time）"""
        ...
```

### 1.2 BaseTasker

所有 Tasker（记录容器）的抽象父类。

```python
@dataclass
class BaseTasker(ABC):
    """记录容器的抽象基类"""

    # --- 元数据 ---
    tasker_id: str = ""         # 唯一标识
    type: str = ""              # Tasker 类型标识
    version: str = ""           # 版本号
    label: str = ""             # 显示标签
    description: str = ""       # 描述文本
    folder: str = ""            # 对应存储文件夹名

    # --- 数据 ---
    task_list: list[BaseTask] = field(default_factory=list)

    # --- 脏数据追踪（存储层使用）---
    loaded_segments: set[str] = field(default_factory=set)
    dirty_segments: set[str] = field(default_factory=set)

    # --- 抽象方法 ---
    @abstractmethod
    def get_commands(self) -> list[str]:
        """返回此 Tasker 支持的所有指令名列表（用于 UI 常驻区显示）"""
        ...

    @abstractmethod
    def create_task(self, fields: dict) -> BaseTask:
        """根据字段字典创建一条新 Task（由扩展模块实现具体字段映射）"""
        ...

    @abstractmethod
    def execute_quick_button(self, button_template: dict) -> BaseTask | None:
        """从外部（主界面快捷按钮）触发一次快捷按钮操作。
        返回创建的 Task 或 None（取消/失败）。
        此方法不依赖 UI 信号机制——主界面直接调用。"""
        ...

    @abstractmethod
    def mark_dirty(self, segment_filename: str) -> None:
        """标记某个 segment 为脏（被修改过）"""
        ...
```

### 1.3 BaseAnalyzer

分析器的抽象基类。

```python
@dataclass
class BaseAnalyzer(ABC):
    """分析器抽象基类"""

    analyzer_name: str = ""     # 注册名 ("attr_count", "monthly_count", ...)

    @abstractmethod
    def analyze(self, params: dict) -> dict:
        """执行分析，返回结构化结果。

        params 可能包含:
            - tasker_id: str
            - year: int
            - month: int
            - attr_filter: str | None
            - ... (各分析器自定义)

        返回 dict 格式供 ECharts 页面消费，具体结构由分析器定义。
        """
        ...
```

## 2. extension_registry.py — 扩展注册表

全局单例。扩展模块通过此类注册自身，core 通过此类 lookup 具体实现。

```python
from typing import Type

class ExtensionRegistry:
    """扩展注册表（单例）。core 不导入扩展，扩展导入 core 并调用 register。"""

    # 类变量（全局注册表）
    _task_types: dict[str, Type[BaseTask]] = {}
    _tasker_types: dict[str, Type[BaseTasker]] = {}
    _analyzers: dict[str, Type[BaseAnalyzer]] = {}
    _chart_pages: dict[str, str] = {}  # "attr_count" → "extensions/default/charts/attr_count.html"

    @classmethod
    def register_task_type(cls, name: str, task_cls: Type[BaseTask]) -> None:
        """注册 Task 类型。name 如 "default", "timer", "account"."""
        cls._task_types[name] = task_cls

    @classmethod
    def register_tasker_type(cls, name: str, tasker_cls: Type[BaseTasker]) -> None:
        """注册 Tasker 类型。"""
        cls._tasker_types[name] = tasker_cls

    @classmethod
    def register_analyzer(cls, name: str, analyzer_cls: Type[BaseAnalyzer]) -> None:
        """注册分析器。"""
        cls._analyzers[name] = analyzer_cls

    @classmethod
    def register_chart_page(cls, name: str, html_path: str) -> None:
        """注册图表 HTML 页面路径（相对于 extensions/）。"""
        cls._chart_pages[name] = html_path

    @classmethod
    def create_task(cls, type_name: str, **kwargs) -> BaseTask:
        """根据类型名创建 Task 实例。"""
        return cls._task_types[type_name](**kwargs)

    @classmethod
    def create_tasker(cls, type_name: str, **kwargs) -> BaseTasker:
        """根据类型名创建 Tasker 实例。"""
        return cls._tasker_types[type_name](**kwargs)

    @classmethod
    def get_analyzer(cls, name: str) -> BaseAnalyzer:
        """获取分析器实例。"""
        return cls._analyzers[name]()

    @classmethod
    def get_chart_page(cls, name: str) -> str:
        """获取图表 HTML 页面路径。"""
        return cls._chart_pages[name]

    @classmethod
    def list_task_types(cls) -> list[str]:
        return list(cls._task_types.keys())

    @classmethod
    def list_analyzer_names(cls) -> list[str]:
        return list(cls._analyzers.keys())
```

## 3. base_service.py — 服务抽象接口

```python
from abc import ABC, abstractmethod
from typing import Any

class BaseTaskerService(ABC):
    """Tasker 管理的抽象接口"""

    @abstractmethod
    def list_taskers(self) -> list[dict]:
        """返回所有 Tasker 的简要信息列表（id, type, label, description, folder）"""
        ...

    @abstractmethod
    def create_tasker(self, tasker_data: dict) -> dict:
        """创建新 Tasker。tasker_data 含 type, label, description。
        返回新 Tasker 的摘要 dict。"""
        ...

    @abstractmethod
    def delete_tasker(self, tasker_id: str) -> bool:
        """删除 Tasker 及其所有数据。返回是否成功。"""
        ...

    @abstractmethod
    def update_tasker(self, tasker_id: str, updates: dict) -> dict | None:
        """更新 Tasker 的 label/description。返回更新后的摘要或 None。"""
        ...

    @abstractmethod
    def get_tasker(self, tasker_id: str) -> BaseTasker | None:
        """获取完整的 Tasker 对象（含 task_list）。"""
        ...


class BaseTaskService(ABC):
    """Task 管理的抽象接口"""

    @abstractmethod
    def get_tasks(self, tasker_id: str, offset: int = 0, limit: int = 50) -> list[BaseTask]:
        """获取 Tasker 中指定范围的 Task 列表。负数 offset 表示从末尾倒序。"""
        ...

    @abstractmethod
    def create_task(self, tasker_id: str, fields: dict) -> BaseTask:
        """在指定 Tasker 中创建新 Task。fields 包含 date, attribute, content, comment 等。"""
        ...

    @abstractmethod
    def update_task(self, tasker_id: str, task_index: int, updates: dict) -> BaseTask | None:
        """更新指定索引的 Task。"""
        ...

    @abstractmethod
    def delete_task(self, tasker_id: str, task_index: int) -> bool:
        """删除指定索引的 Task。"""
        ...

    @abstractmethod
    def search_tasks(self, tasker_id: str, query: str) -> list[tuple[int, BaseTask]]:
        """搜索 Tasker 中匹配 query 的 Task。返回 (索引, Task) 列表。"""
        ...
```

## 4. types.py — 跨层数据类型

```python
from typing import TypedDict, NotRequired

class TaskerSummary(TypedDict):
    """Tasker 简要信息（用于列表展示和 taskers.json 读写）"""
    id: str
    type: str
    label: str
    description: str
    folder: str
    quick_buttons: list['QuickButtonDef']

class QuickButtonDef(TypedDict):
    """快捷按钮模板定义"""
    command: str            # 自定义指令名
    label: str              # 按钮显示文本
    preset: 'PresetFields'  # 预设字段

class PresetFields(TypedDict, total=False):
    """快捷按钮预设字段"""
    date: str               # 固定日期（use_default_date=true 时忽略此值）
    attribute: str
    content: str
    comment: str
    use_default_date: bool  # True → 自动取当天日期

class SearchQuery(TypedDict):
    """搜索查询参数"""
    tasker_id: str
    text: str               # 搜索文本
    attr_filter: str | None # 按属性筛选（可选）
    date_from: str | None   # 日期范围起始 "YYYY_MM_DD"
    date_to: str | None     # 日期范围结束

class AnalysisParams(TypedDict, total=False):
    """分析查询参数"""
    tasker_id: str
    year: int
    month: int
    attr_filter: str | None
    top_n: int              # 取前 N 项（默认全部）
```

## 5. input_processor.py — 输入预处理链

```python
from typing import Callable

# 预处理步骤类型：接收原始字符串，返回处理后的字符串
PreprocessStep = Callable[[str], str]


class InputPreprocessor:
    """输入预处理链。维护一组有序的预处理步骤，在输入交给解析器之前依次执行。"""

    _steps: list[PreprocessStep] = []

    @classmethod
    def register_step(cls, step: PreprocessStep) -> None:
        """注册一个预处理步骤。步骤按注册顺序执行。"""
        cls._steps.append(step)

    @classmethod
    def process(cls, raw_input: str) -> str:
        """依次执行所有预处理步骤，返回最终字符串。"""
        result = raw_input
        for step in cls._steps:
            result = step(result)
        return result


# --- 内置预处理步骤 ---

def step_plus_to_search(raw: str) -> str:
    """'+xxx' → 'search xxx'"""
    if raw.startswith('+'):
        return 'search ' + raw[1:]
    return raw
```

## 6. 依赖关系

```
core/
├── abstract.py          # 定义 BaseTask, BaseTasker, BaseAnalyzer —— 无外部依赖
├── extension_registry.py # 依赖 abstract.py (类型标注)
├── base_service.py       # 依赖 abstract.py (BaseTask, BaseTasker)
├── types.py              # 无外部依赖 (仅 TypedDict)
├── input_processor.py    # 无外部依赖
└── __init__.py            # 导出所有公共 API
```

**不要在此目录创建任何具体 Task/Tasker 实现。所有实现放入 src/extensions/。**
