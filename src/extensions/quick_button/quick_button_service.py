"""QuickButton Service — 快捷按钮触发逻辑。模板数据存储在 taskers.json 中。"""

from core.abstract import BaseTasker, BaseTask
from core.types import QuickButtonDef


class QuickButtonService:
    """快捷按钮服务——触发按钮 → 读模板 → 自动填日期/判定默认值 → 调用 Task 创建流程。"""

    @staticmethod
    def trigger(tasker: BaseTasker, button_def: QuickButtonDef) -> BaseTask | None:
        """触发快捷按钮。委托给 tasker.execute_quick_button。

        Args:
            tasker: 目标 Tasker 实例
            button_def: QuickButtonDef 格式的按钮定义

        Returns:
            创建的 Task，或 None（content 为空需用户补充）
        """
        result = tasker.execute_quick_button(button_def)
        if result is not None:
            QuickButtonService.increment_count(button_def)
        return result

    @staticmethod
    def increment_count(button_def: dict) -> None:
        """递增使用计数（直接修改 dict）。"""
        button_def['usage_count'] = button_def.get('usage_count', 0) + 1

    @staticmethod
    def sort_by_usage(buttons: list[dict]) -> list[dict]:
        """按使用频率降序排序。usage_count 缺失视为 0。"""
        return sorted(buttons, key=lambda b: b.get('usage_count', 0), reverse=True)
