"""跨层数据类型——用于各层间传递数据而不依赖具体类"""

from typing import TypedDict


class QuickButtonDef(TypedDict):
    """快捷按钮模板定义"""
    command: str
    label: str
    preset: 'PresetFields'


class PresetFields(TypedDict, total=False):
    """快捷按钮预设字段"""
    date: str
    attribute: str
    content: str
    comment: str
    use_default_date: bool


class TaskerSummary(TypedDict):
    """Tasker 简要信息"""
    id: str
    type: str
    label: str
    description: str
    folder: str
    quick_buttons: list[QuickButtonDef]


class SearchQuery(TypedDict, total=False):
    """搜索查询参数"""
    tasker_id: str
    text: str
    attr_filter: str | None
    date_from: str | None
    date_to: str | None


class AnalysisParams(TypedDict, total=False):
    """分析查询参数"""
    tasker_id: str
    year: int
    month: int
    attr_filter: str | None
    top_n: int
