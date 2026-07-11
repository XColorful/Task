"""输入预处理链——维护一组有序的预处理步骤。

输入在交给解析器之前，依次经过预处理链中的每个步骤。
"""

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

    @classmethod
    def clear(cls) -> None:
        """清空所有步骤（测试用）。"""
        cls._steps.clear()


# ================================================================
# 内置预处理步骤
# ================================================================

def step_plus_to_search(raw: str) -> str:
    """'+xxx' → 'search xxx'
    如果输入以 '+' 开头，替换为 'search ' + 原始输入[1:]。
    否则原样返回。
    """
    if raw.startswith('+'):
        return 'search ' + raw[1:]
    return raw
