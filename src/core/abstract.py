"""抽象基类——所有扩展模块的继承根。

定义 BaseTask, BaseTasker, BaseAnalyzer 三个抽象基类。
core 包不包含任何具体记录类型的业务逻辑。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ============================================================
# BaseTask —— 单条记录的抽象基类
# ============================================================

@dataclass
class BaseTask(ABC):
    """单条记录的抽象基类。扩展模块必须继承此类。"""

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
        """序列化为字典，保持字段插入顺序。用于 JSON 写入。"""
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'BaseTask':
        """从字典反序列化。data 是从 segment JSON 读取的单条记录 dict。"""
        ...

    @abstractmethod
    def matches_search(self, query: str) -> bool:
        """判断此 Task 是否匹配搜索词。
        各扩展模块自行决定搜索范围（如 default 搜索 date/attribute/content/comment，
        timer 额外搜索 start_time/end_time）。
        """
        ...


# ============================================================
# BaseTasker —— 记录容器的抽象基类
# ============================================================

@dataclass
class BaseTasker(ABC):
    """记录容器的抽象基类。"""

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
        """返回此 Tasker 支持的所有指令名列表（用于 UI 常驻区显示）。"""
        ...

    @abstractmethod
    def create_task(self, fields: dict) -> BaseTask:
        """根据字段字典创建一条新 Task（由扩展模块实现具体字段映射）。
        fields 包含 date, attribute, content, comment 及各模块扩展字段。
        """
        ...

    @abstractmethod
    def execute_quick_button(self, button_template: dict) -> BaseTask | None:
        """从外部（主界面快捷按钮）触发一次快捷按钮操作。
        button_template 为 QuickButtonDef 格式的 dict。
        返回创建的 Task 或 None（取消/失败）。
        此方法不依赖 UI 信号机制——主界面直接调用。
        """
        ...

    @abstractmethod
    def mark_dirty(self, segment_filename: str) -> None:
        """标记某个 segment 为脏（被修改过）。"""
        ...


# ============================================================
# BaseAnalyzer —— 分析器抽象基类
# ============================================================

@dataclass
class BaseAnalyzer(ABC):
    """分析器抽象基类。"""

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
