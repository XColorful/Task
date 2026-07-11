"""扩展注册表——全局单例。

扩展模块通过此类注册自身，core 通过此类 lookup 具体实现。
core 绝不导入扩展模块——扩展导入 core 并调用 register。
"""

from typing import Type


class ExtensionRegistry:
    """扩展注册表（单例）。"""

    # 类变量（全局注册表）
    _task_types: dict[str, Type] = {}
    _tasker_types: dict[str, Type] = {}
    _analyzers: dict[str, Type] = {}
    _chart_pages: dict[str, str] = {}  # "attr_count" → "extensions/default/charts/attr_count.html"

    # ================================================================
    # 注册方法
    # ================================================================

    @classmethod
    def register_task_type(cls, name: str, task_cls: Type) -> None:
        """注册 Task 类型。name 如 "default", "timer", "account"。

        扩展模块在 __init__.py 中调用。
        """
        cls._task_types[name] = task_cls

    @classmethod
    def register_tasker_type(cls, name: str, tasker_cls: Type) -> None:
        """注册 Tasker 类型。"""
        cls._tasker_types[name] = tasker_cls

    @classmethod
    def register_analyzer(cls, name: str, analyzer_cls: Type) -> None:
        """注册分析器。"""
        cls._analyzers[name] = analyzer_cls

    @classmethod
    def register_chart_page(cls, name: str, html_path: str) -> None:
        """注册图表 HTML 页面路径（相对于 extensions/）。"""
        cls._chart_pages[name] = html_path

    # ================================================================
    # 查找/创建方法
    # ================================================================

    @classmethod
    def create_task(cls, type_name: str, **kwargs):
        """根据类型名创建 Task 实例。

        Raises:
            KeyError: 类型名未注册
        """
        return cls._task_types[type_name](**kwargs)

    @classmethod
    def create_tasker(cls, type_name: str, **kwargs):
        """根据类型名创建 Tasker 实例。

        Raises:
            KeyError: 类型名未注册
        """
        return cls._tasker_types[type_name](**kwargs)

    @classmethod
    def get_analyzer(cls, name: str):
        """获取分析器实例。

        Raises:
            KeyError: 分析器名未注册
        """
        return cls._analyzers[name]()

    @classmethod
    def get_chart_page(cls, name: str) -> str:
        """获取图表 HTML 页面路径。

        Raises:
            KeyError: 图表页面名未注册
        """
        return cls._chart_pages[name]

    @classmethod
    def list_task_types(cls) -> list[str]:
        """返回所有已注册的 Task 类型名。"""
        return list(cls._task_types.keys())

    @classmethod
    def list_tasker_types(cls) -> list[str]:
        """返回所有已注册的 Tasker 类型名。"""
        return list(cls._tasker_types.keys())

    @classmethod
    def list_analyzer_names(cls) -> list[str]:
        """返回所有已注册的分析器名。"""
        return list(cls._analyzers.keys())

    @classmethod
    def list_chart_page_names(cls) -> list[str]:
        """返回所有已注册的图表页面名。"""
        return list(cls._chart_pages.keys())
