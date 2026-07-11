# SPEC: analysis — 分析引擎

> 对应源码路径: `src/analysis/`
> 独立于 UI 的纯数据计算层。每个分析器从存储层读取数据、执行聚合计算、返回结构化结果。分析器通过 HTTP API (`/api/analysis/{analyzer_name}`) 暴露给图表页面。

## 1. analysis_engine.py — 分析引擎门面

```python
from typing import Type
from core.abstract import BaseAnalyzer
from core.extension_registry import ExtensionRegistry


class AnalysisEngine:
    """分析引擎门面 —— 按需加载分析器，协调数据查询。

    分析器通过 ExtensionRegistry 注册（扩展模块在 __init__.py 中调用
    register_analyzer）。AnalysisEngine 本身不硬编码任何具体分析器。

    使用方式:
        engine = AnalysisEngine(storage)
        result = engine.analyze("attr_count", {"tasker_id": "abc123"})
    """

    def __init__(self, storage: 'StorageManager') -> None:
        """
        Args:
            storage: StorageManager 实例，分析器通过它读取全量或部分数据
        """
        self._storage = storage
        self._analyzer_cache: dict[str, BaseAnalyzer] = {}

    def get_analyzer(self, name: str) -> BaseAnalyzer:
        """按名称获取分析器实例（带缓存）。

        第一次调用时通过 ExtensionRegistry 创建实例并缓存；
        后续调用返回缓存的同一实例（分析器本身无状态，缓存仅为减少重复构造）。

        Args:
            name: 分析器注册名 ("attr_count", "monthly_count", "duration", "heatmap")

        Returns:
            BaseAnalyzer 实例

        Raises:
            KeyError: name 未在 ExtensionRegistry 中注册
        """
        if name not in self._analyzer_cache:
            analyzer_cls = ExtensionRegistry.get_analyzer_cls(name)
            self._analyzer_cache[name] = analyzer_cls()
        return self._analyzer_cache[name]

    def analyze(self, name: str, params: dict) -> dict:
        """执行指定分析器，返回结构化结果。

        等价于 self.get_analyzer(name).analyze(params)，一次便捷调用。

        Args:
            name:   分析器注册名
            params: 分析参数 (tasker_id, year, month, attr_filter, top_n 等)

        Returns:
            分析结果 dict，格式由各分析器定义
        """
        return self.get_analyzer(name).analyze(params)

    def list_analyzers(self) -> list[str]:
        """返回所有已注册的分析器名称列表。"""
        return ExtensionRegistry.list_analyzer_names()
```

## 2. BaseAnalyzer — 抽象基类

> 已在 `core/abstract.py` 中定义，此处复述以保持 SPEC 自足。

```python
from abc import ABC, abstractmethod


class BaseAnalyzer(ABC):
    """分析器抽象基类。每个具体分析器实现 analyze() 方法，
    从存储层读取数据、聚合计算、返回 dict 供图表页面消费。

    分析器本身无持久状态 —— 每次 analyze() 调用都是独立的只读查询。
    """

    analyzer_name: str = ""  # 注册名 ("attr_count", "monthly_count", ...)

    @abstractmethod
    def analyze(self, params: dict) -> dict:
        """执行分析，返回结构化结果。

        params 可能包含:
            - tasker_id: str        (必填) 目标 Tasker ID
            - year: int             (可选) 筛选年份
            - month: int            (可选) 筛选月份 (1-12)
            - attr_filter: str|None (可选) 按属性筛选
            - top_n: int            (可选) 取前 N 项，默认全部

        返回 dict 格式供 ECharts 页面直接消费，具体结构由各分析器定义。
        """
        ...
```

## 3. attribute_counter.py — 属性计数分析器

```python
from core.abstract import BaseAnalyzer
from core.storage.storage_manager import StorageManager
from collections import Counter


class AttributeCounter(BaseAnalyzer):
    """按属性统计 Task 数量，返回饼图/柱状图所需的数据格式。

    注册名: "attr_count"

    输入 params:
        - tasker_id: str    (必填)
        - year: int         (可选) 筛选年份
        - month: int        (可选) 筛选月份
        - attr_filter: str  (可选) 仅统计指定属性的 Task，跳过聚合直接计数
        - top_n: int        (可选) 取前 N 个属性，默认全部

    输出:
        {
            "labels": ["编程", "阅读", "运动", ...],   # 属性名列表
            "values": [12, 8, 5, ...],                # 对应计数
            "total": 25                                 # 符合条件的总记录数
        }
    """

    analyzer_name: str = "attr_count"

    def __init__(self) -> None:
        self._storage: StorageManager | None = None

    def set_storage(self, storage: StorageManager) -> None:
        """注入存储管理器（由 AnalysisEngine 在首次加载时调用）。"""
        self._storage = storage

    def analyze(self, params: dict) -> dict:
        """统计指定 Tasker 中各属性的 Task 数量。

        流程:
        1. 从 storage 加载指定 Tasker 的全量 task_list
        2. 按 year/month 筛选（如提供）
        3. 提取每条 Task 的 attribute 字段
        4. Counter 聚合
        5. 按值降序排列，取前 top_n 项
        6. 分离为 labels / values 两个平行列表

        Returns:
            {"labels": [str], "values": [int], "total": int}
        """
        ...
```

## 4. monthly_counter.py — 月度趋势分析器

```python
from core.abstract import BaseAnalyzer
from core.storage.storage_manager import StorageManager
from collections import defaultdict


class MonthlyCounter(BaseAnalyzer):
    """按月份统计 Task 数量趋势，返回折线图/柱状图所需的数据格式。

    注册名: "monthly_count"

    输入 params:
        - tasker_id: str    (必填)
        - year: int         (可选) 筛选年份，默认全部年份
        - attr_filter: str  (可选) 按属性筛选

    输出:
        {
            "months": ["2026-01", "2026-02", "2026-03", ...],  # 月份标签
            "values": [35, 42, 28, ...],                        # 各月计数
            "total": 105                                          # 总计数
        }
    """

    analyzer_name: str = "monthly_count"

    def __init__(self) -> None:
        self._storage: StorageManager | None = None

    def set_storage(self, storage: StorageManager) -> None:
        self._storage = storage

    def analyze(self, params: dict) -> dict:
        """统计指定 Tasker 中按月份的 Task 数量趋势。

        流程:
        1. 从 storage 加载全量 task_list
        2. 按 attr_filter 筛选（如提供）
        3. 提取每条 Task 的 date 字段，取 "YYYY_MM" 部分
        4. 按 year 参数过滤（如提供）
        5. defaultdict 按月累积计数
        6. 按时间顺序排列月份
        7. 分离为 months / values 两个平行列表

        Returns:
            {"months": [str], "values": [int], "total": int}
        """
        ...
```

## 5. duration_analyzer.py — 时长分析器

```python
from core.abstract import BaseAnalyzer
from core.storage.storage_manager import StorageManager
from extensions.timer.timer_task import TimerTask


class DurationAnalyzer(BaseAnalyzer):
    """Timer Task 时长统计，按属性分组或按月份分组，返回柱状图数据。

    注册名: "duration"

    输入 params:
        - tasker_id: str     (必填) 仅对 timer 类型的 Tasker 有效
        - group_by: str      (必填) 分组维度: "attribute" | "month"
        - year: int          (可选) 筛选年份
        - month: int         (可选) 筛选月份（group_by="attribute" 时用于限定范围）
        - attr_filter: str   (可选) 按属性筛选（group_by="month" 时用于限定范围）

    输出 (group_by="attribute"):
        {
            "labels": ["编程", "阅读", "运动", ...],          # 属性名
            "durations_min": [480, 320, 150, ...],           # 总时长（分钟）
            "formatted": [" 8h  0m", " 5h 20m", " 2h 30m", ...],  # 格式化
            "total_min": 950
        }

    输出 (group_by="month"):
        {
            "labels": ["2026-01", "2026-02", ...],           # 月份
            "durations_min": [1200, 980, ...],               # 总时长（分钟）
            "formatted": ["20h  0m", "16h 20m", ...],        # 格式化
            "total_min": 2180
        }
    """

    analyzer_name: str = "duration"

    def __init__(self) -> None:
        self._storage: StorageManager | None = None

    def set_storage(self, storage: StorageManager) -> None:
        self._storage = storage

    def analyze(self, params: dict) -> dict:
        """统计 Timer Task 的时长分布。

        流程:
        1. 从 storage 加载全量 task_list
        2. 筛选类型为 TimerTask 的记录
        3. 过滤进行中的任务（end_time 为空）
        4. 按 group_by 维度聚合:
           - group_by="attribute": 按 Task 的 attribute 字段分组
           - group_by="month":     按 date 字段取 "YYYY_MM" 分组
        5. 对每组累加 duration_minutes
        6. 按总时长降序排列
        7. 使用 DurationCalculator.format_duration() 生成可读格式

        Returns:
            {"labels": [str], "durations_min": [int], "formatted": [str], "total_min": int}
        """
        ...

    def _group_by_attribute(
        self, tasks: list[TimerTask], year: int | None, month: int | None
    ) -> dict:
        """按属性聚合时长。"""
        ...

    def _group_by_month(
        self, tasks: list[TimerTask], attr_filter: str | None, year: int | None
    ) -> dict:
        """按月份聚合时长。"""
        ...
```

## 6. heatmap_builder.py — 热力图构建器

```python
from core.abstract import BaseAnalyzer
from core.storage.storage_manager import StorageManager
from collections import defaultdict


class HeatmapBuilder(BaseAnalyzer):
    """日期 × 属性热力图矩阵构建，返回 ECharts heatmap 所需的数据格式。

    注册名: "heatmap"

    输入 params:
        - tasker_id: str    (必填)
        - year: int         (必填) 目标年份
        - attr_filter: str  (可选) 限制属性范围（逗号分隔多个属性）
        - top_n: int        (可选) 取前 N 个活跃属性，默认 10

    输出:
        {
            "dates": ["01-01", "01-02", "01-03", ...],       # X 轴: 当年所有日期 "MM_DD"
            "attrs": ["编程", "阅读", "运动", ...],          # Y 轴: 属性名列表
            "matrix": [                                       # Z 值: 每个 (日期, 属性) 的 Task 数
                [0, 2, 0, ...],   # 01-01 各属性计数
                [1, 0, 3, ...],   # 01-02 各属性计数
                ...
            ]
        }

    说明:
        - matrix 为 list[list[int]]，外层按 dates 顺序，内层按 attrs 顺序
        - matrix[i][j] = dates[i] 那一天 attr[j] 的 Task 数量
        - 不含零值行（某一日期无任何 Task 时仍保留该行，保持矩阵完整）
    """

    analyzer_name: str = "heatmap"

    def __init__(self) -> None:
        self._storage: StorageManager | None = None

    def set_storage(self, storage: StorageManager) -> None:
        self._storage = storage

    def analyze(self, params: dict) -> dict:
        """构建日期 × 属性热力图矩阵。

        流程:
        1. 从 storage 加载全量 task_list
        2. 筛选 target year 的记录
        3. 按属性聚合计数，取 top_n 个最活跃属性
        4. 构建完整的日期序列（当年所有日期，从 01-01 到 12-31）
        5. 遍历日期序列，对每个日期构建属性计数行
        6. 组装 matrix

        Returns:
            {"dates": [str], "attrs": [str], "matrix": list[list[int]]}
        """
        ...

    def _build_date_range(self, year: int) -> list[str]:
        """生成当年所有日期的 "MM_DD" 列表。

        >>> self._build_date_range(2026)
        ["01-01", "01-02", ..., "12-31"]
        """
        ...

    def _to_matrix(
        self,
        date_attr_counts: dict[str, dict[str, int]],
        dates: list[str],
        attrs: list[str],
    ) -> list[list[int]]:
        """将 {date: {attr: count}} 转换为二维矩阵。"""
        ...
```

## 7. 数据流

```
浏览器图表页面 (fetch)
       │
       ▼
ChartHttpServer  /api/analysis/{name}?params=...
       │
       ▼
AnalysisEngine.analyze(name, params)
       │
       ├── get_analyzer(name) → 从缓存取 / ExtensionRegistry 创建
       │
       ▼
BaseAnalyzer.analyze(params)
       │
       ├── storage.load_all_segments(folder)  → 全量 task_list
       ├── 筛选 (year, month, attr_filter)
       ├── 聚合 (Counter / defaultdict)
       ├── 排序 / top_n
       │
       ▼
返回 dict → JSON → 浏览器渲染 ECharts
```

## 8. 注册方式

各扩展模块在 `__init__.py` 中注册其分析器。示例（extensions/default/__init__.py）:

```python
from core.extension_registry import ExtensionRegistry
from analysis.attribute_counter import AttributeCounter
from analysis.monthly_counter import MonthlyCounter

ExtensionRegistry.register_analyzer("attr_count", AttributeCounter)
ExtensionRegistry.register_analyzer("monthly_count", MonthlyCounter)
```

扩展模块自行决定注册哪些分析器。分析器实现文件放在 `src/analysis/` 下，属于分析引擎包，不属于扩展模块包。

## 9. 依赖关系

```
analysis/
├── analysis_engine.py      # 依赖 core.abstract.BaseAnalyzer, core.extension_registry, core.storage
├── attribute_counter.py    # 依赖 core.abstract.BaseAnalyzer, core.storage
├── monthly_counter.py      # 依赖 core.abstract.BaseAnalyzer, core.storage
├── duration_analyzer.py    # 依赖 core.abstract.BaseAnalyzer, core.storage, extensions.timer.TimerTask, util.date_utils.DurationCalculator
├── heatmap_builder.py      # 依赖 core.abstract.BaseAnalyzer, core.storage
└── __init__.py
```

**核心原则:**
- 分析器仅做只读查询，不修改数据
- 分析器通过 StorageManager 读取数据，不直接操作文件
- 分析器无内部状态，每次 analyze() 是独立调用
- 返回的 dict 结构直接面向 ECharts 页面消费
