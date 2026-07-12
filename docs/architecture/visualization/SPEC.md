# SPEC: visualization — 3D 可视化数据构建

> 对应源码路径: `src/visualization/`
> 将 Timer Task 组织为 ECharts GL bar3D 所需的 `(x, z, y, color)` 格式。渲染由外部浏览器中的 ECharts GL 完成，本包仅负责数据构建。

## 1. monthly_3d_builder.py — 月度 3D 网格构建器

```python
from typing import TypedDict
from extensions.timer.timer_task import TimerTask


class Monthly3DResult(TypedDict):
    """Monthly3DBuilder.build() 的返回类型。"""
    data: list[list]          # [[x, z, y, color_id], ...]
    labels: list[str]         # X 轴标签 (周日 ~ 周六)
    months: list[str]         # 各行的月份标签列表，与 z 轴对应
    color_map: dict[str, str] # {"attr1": "#5470c6", "attr2": "#91cc75", ...}


class Monthly3DBuilder:
    """3D 月度网格柱状图的数据构建器。

    将一批 Timer Task 转换为 ECharts GL bar3D 所需的 [[x, z, y, color_id], ...] 格式。
    所有方法均为类方法/静态方法——Builder 无内部状态，每次 build() 是纯计算。

    核心布局规则:
    - 7 列一行（周一 ~ 周日，x = 0~6）
    - 每月从 z=0 开始，新月份 z 递进一次后置零
    - 跨月时强制换行（即使当月不满 7 列也切断，下月从 z=0 重新起行）
    - bar 高度 = duration_minutes
    - bar 颜色 = attribute → color_id

    使用方式:
        result = Monthly3DBuilder.build(timer_tasks, year=2026, month=7)
        # result["data"] → [[x, z, y, color_id], ...]
        # result["labels"] → ["周一", "周二", ...]
        # result["months"] → ["7月", ...]
        # result["color_map"] → {"编程": "#5470c6", ...}
    """

    # ---- 类常量 ----
    DAY_LABELS: list[str] = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    DEFAULT_COLORS: list[str] = [
        "#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de",
        "#3ba272", "#fc8452", "#9a60b4", "#ea7ccc", "#48b8d0",
    ]

    @classmethod
    def build(
        cls,
        tasks: list[TimerTask],
        year: int,
        month: int,
    ) -> Monthly3DResult:
        """构建指定年月的 3D 柱状图数据。

        Args:
            tasks: TimerTask 列表（应已过滤掉进行中的任务）
            year:  目标年份 (如 2026)
            month: 目标月份 (1-12)

        Returns:
            Monthly3DResult:
                data:      [[x, z, y, color_id], ...] — 每个元素是一个柱子的 4 元组
                labels:    ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                months:    ["7月"] 或跨月时多个月份标签
                color_map: {"编程": "#5470c6", "运动": "#91cc75", ...}

        流程:
        1. 筛选 tasks 中属于 year-month 的记录（按 date 字段 "YYYY_MM_DD" 匹配）
        2. 收集所有不重复的 attribute 值，分配颜色
        3. 按 date → attribute 聚合每天每属性的 duration_minutes 总和
        4. 生成该月所有日期列表
        5. 按布局规则展开为 bar3D 坐标:
           - 计算每个日期的星期几 (周一=0, 周日=6)
           - date 作为 x (0-6)
           - z 累进: 同一月内每 7 天占一行，z 递增；跨月时 z 重置为 0
           - y 为该日期该属性的 duration_minutes
           - color_id 为该属性在 attr_list 中的序号
        6. 组装 Monthly3DResult
        """
        ...

    # ---- 内部方法 ----

    @classmethod
    def _filter_tasks_by_month(
        cls, tasks: list[TimerTask], year: int, month: int
    ) -> list[TimerTask]:
        """筛选指定年月的 Task（date 前缀匹配 "YYYY_MM"）。

        Args:
            tasks: 全量 TimerTask 列表
            year:  目标年份
            month: 目标月份 (1-12)

        Returns:
            过滤后的 TimerTask 列表（已完成、date 匹配的）
        """
        prefix = f"{year}_{month:02d}"
        return [
            t for t in tasks
            if t.date.startswith(prefix) and not t.is_running
        ]

    @classmethod
    def _collect_attributes(cls, tasks: list[TimerTask]) -> list[str]:
        """收集所有不重复的 attribute 值，保持首次出现顺序。

        Returns:
            有序的去重 attribute 列表
        """
        seen: set[str] = set()
        attrs: list[str] = []
        for t in tasks:
            if t.attribute not in seen:
                seen.add(t.attribute)
                attrs.append(t.attribute)
        return attrs

    @classmethod
    def _assign_colors(cls, attrs: list[str]) -> dict[str, str]:
        """为每个属性分配颜色。颜色循环使用 DEFAULT_COLORS。

        Args:
            attrs: 属性名列表

        Returns:
            {"编程": "#5470c6", "阅读": "#91cc75", ...}
        """
        color_map: dict[str, str] = {}
        for i, attr in enumerate(attrs):
            color_map[attr] = cls.DEFAULT_COLORS[i % len(cls.DEFAULT_COLORS)]
        return color_map

    @classmethod
    def _aggregate_by_date_and_attr(
        cls, tasks: list[TimerTask]
    ) -> dict[str, dict[str, int]]:
        """按日期和属性聚合时长。

        Returns:
            {"2026_07_01": {"编程": 120, "阅读": 60}, "2026_07_02": {...}, ...}
            值为 duration_minutes（同一天同一属性有多条时累加）。
        """
        from collections import defaultdict

        result: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for t in tasks:
            minutes = t.duration_minutes or 0
            if minutes > 0:
                result[t.date][t.attribute] += minutes
        return dict(result)

    @classmethod
    def _get_dates_in_month(cls, year: int, month: int) -> list[str]:
        """生成指定月份的所有日期字符串 "YYYY_MM_DD"。

        Args:
            year:  年份
            month: 月份 (1-12)

        Returns:
            ["2026_07_01", "2026_07_02", ..., "2026_07_31"]
        """
        import calendar
        from datetime import date

        days_in_month = calendar.monthrange(year, month)[1]
        return [
            date(year, month, d).strftime("%Y_%m_%d")
            for d in range(1, days_in_month + 1)
        ]

    @classmethod
    def _date_to_weekday(cls, date_str: str) -> int:
        """将 "YYYY_MM_DD" 转为星期索引（周一=0, 周日=6）。

        Args:
            date_str: "2026_07_11"

        Returns:
            0-6 的整数，周一为 0
        """
        from datetime import datetime

        dt = datetime.strptime(date_str, "%Y_%m_%d")
        # Python: Monday=0, Sunday=6
        return dt.weekday()

    @classmethod
    def _build_bars(
        cls,
        dates: list[str],
        aggregated: dict[str, dict[str, int]],
        attr_list: list[str],
    ) -> tuple[list[list], list[str]]:
        """按布局规则展开为 bar3D 坐标列表。

        布局规则:
        - x = 星期索引 (0=周一 ~ 6=周日)
        - z = 行号，从 0 开始
        - 同一自然月内：每 7 天一行，满一周 z 递增一次
        - 跨月边界：z 重置为 0，强制换行（即使当月最后一行不满 7 天）
        - 换行发生在周一之前（即遇到周一且不是本月第一天时 z+1）

        Args:
            dates:       该月所有日期字符串 ["2026_07_01", ...]
            aggregated:  {date: {attr: minutes}}
            attr_list:   属性名列表（决定 color_id 的序号）

        Returns:
            (data, months_labels):
                data:   [[x, z, y, color_id], ...]
                months: 每行对应的月份标签 ["7月", "7月", "8月", ...]

        说明:
            - 同一天同一个属性只有一条柱（聚合后的分钟数）
            - color_id 是 attr 在 attr_list 中的索引
            - 跨月时 months 标签反映该行所有日期的月份（同一天不可能跨月，
              但同一行可能跨两个月份——此时取该行的起始月份或标注为 "7-8月"）
        """
        z: int = 0
        current_month: int | None = None
        data: list[list] = []
        months: list[str] = []

        for i, date_str in enumerate(dates):
            from datetime import datetime
            dt = datetime.strptime(date_str, "%Y_%m_%d")
            mon = dt.month
            wd = dt.weekday()  # 0=周一

            # 跨月检测：月份变化时 z+1（跳到下一行）
            if current_month is not None and mon != current_month:
                # 换行：z+1，下个月从新行开始
                z += 1
                # 如果当前日期是周一，说明自然对齐了新月份的第一天就是周一
                # 不需要额外处理

            current_month = mon

            # 同一月内：遇到周一（且不是该月的第一条）→ z+1
            if i > 0 and wd == 0 and current_month == mon:
                # 检查是否真跨周（不是连续两个周一之间隔了自然换月）
                prev_dt = datetime.strptime(dates[i - 1], "%Y_%m_%d")
                if prev_dt.month == mon:
                    z += 1

            # 为该日期的每个属性生成柱
            attr_counts = aggregated.get(date_str, {})
            for attr_idx, attr in enumerate(attr_list):
                minutes = attr_counts.get(attr, 0)
                if minutes > 0:
                    data.append([wd, z, minutes, attr_idx])

            # 追踪每行的月份标签
            while len(months) <= z:
                months.append("")
            if months[z] == "":
                months[z] = f"{mon}月"

        return data, months
```

## 2. 输出格式详解

### 2.1 data 字段

`list[list]` — 每个内层列表为 `[x, z, y, color_id]`（均为 int/float）:

| 字段 | 含义 | 取值范围 |
|------|------|----------|
| x | 列 (星期) | 0=周一 ~ 6=周日 |
| z | 行号 (周) | 0, 1, 2, ... 每月从 0 开始 |
| y | 柱高 (时长) | duration_minutes，≥ 0 |
| color_id | 颜色序号 | 0 ~ len(attr_list)-1，对应 color_map |

### 2.2 labels 字段

X 轴标签: `["周一", "周二", "周三", "周四", "周五", "周六", "周日"]`

### 2.3 months 字段

行标签列表，与 z 轴一一对应: `["7月", "7月", "8月", "8月", ...]`
跨月时同一行取该行首个日期的月份。

### 2.4 color_map 字段

属性名到 hex 颜色的映射: `{"编程": "#5470c6", "阅读": "#91cc75", ...}`
颜色从 DEFAULT_COLORS 循环分配。

## 3. 布局示例

以 2026 年 7 月为例（7 月 1 日是周三）:

```
z=0:  [三] [四] [五] [六] [日]                          ← 7月1-5日 (x=2,3,4,5,6)
z=1:  [一] [二] [三] [四] [五] [六] [日]                ← 7月6-12日
z=2:  [一] [二] [三] [四] [五] [六] [日]                ← 7月13-19日
z=3:  [一] [二] [三] [四] [五] [六] [日]                ← 7月20-26日
z=4:  [一] [二] [三] [四] [五]                           ← 7月27-31日

每个格子内: 该日期下各属性的柱依次排列（柱高 = 时长分钟数，颜色 = 属性色）
```

如果 7 月 31 日是周五，8 月 1 日是周六，则 7 月 z=4 行后接 8 月 z=0 行:

```
z=4 (7月):  [一] [二] [三] [四] [五]
z=0 (8月):                                       [六] [日] [一] [二] ...
```

8 月从新的 z=0 开始，强制换行。

## 4. HTTP API 对接

Monthly3DBuilder 由分析引擎通过 HTTP API 暴露给浏览器:

```
GET /api/analysis/3d_monthly?tasker_id=xxx&year=2026&month=7

响应 JSON:
{
    "data": [[2,0,120,0], [3,0,60,1], ...],
    "labels": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
    "months": ["7月", "7月", "7月", "7月", "7月"],
    "color_map": {"编程": "#5470c6", "阅读": "#91cc75", ...}
}
```

浏览器端 ECharts GL 配置片段:

```javascript
const result = await fetch('/api/analysis/3d_monthly?tasker_id=xxx&year=2026&month=7').then(r => r.json());

const option = {
    visualMap: {
        pieces: result.attr_list.map((attr, i) => ({
            label: attr,
            color: result.color_map[attr],
        })),
    },
    series: [{
        type: 'bar3D',
        data: result.data,              // [[x, z, y, colorId], ...]
        shading: 'color',
        // ...
    }],
};
```

## 5. 依赖关系

```
visualization/
├── monthly_3d_builder.py   # 依赖 extensions.timer.TimerTask (类型标注)
└── __init__.py

无内部状态 —— 所有方法为类方法/静态方法。
纯数据计算 —— 不读写磁盘，不依赖 StorageManager。
输入 TimerTask 列表由调用方（HTTP 服务/分析引擎）从存储层获取后传入。
```

## 6. 注册方式

分析器在对应扩展模块的 `__init__.py` 中注册:

```python
# extensions/timer/__init__.py
from core.extension_registry import ExtensionRegistry
from analysis.duration_analyzer import DurationAnalyzer
from visualization.monthly_3d_builder import Monthly3DBuilder

ExtensionRegistry.register_analyzer("duration", DurationAnalyzer)

# Monthly3DBuilder 也可注册为分析器 —— 它遵循相同的 analyze(params) → dict 契约
# 或者直接由 HTTP 路由调用 build(tasks, year, month)
ExtensionRegistry.register_chart_page("3d_monthly", "extensions/timer/charts/3d_monthly.html")
```
