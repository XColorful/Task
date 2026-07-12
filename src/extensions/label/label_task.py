"""Label Task — 标签记录。额外字段：label_list（键值对列表）。"""

from collections import OrderedDict
from core.abstract import BaseTask


class LabelTask(BaseTask):
    """标签 Task。支持自定义键值对标签。"""

    label_list: list[tuple[str, str]] = []

    def __init__(self, date: str = "", attribute: str = "",
                 content: str = "", comment: str = "",
                 create_date: str = "",
                 label_list: list[tuple[str, str]] | None = None):
        super().__init__()
        self.type = "label"
        self.version = "label"
        self.create_date = create_date
        self.date = date
        self.attribute = attribute
        self.content = content
        self.comment = comment
        self.label_list = label_list or []

    def to_dict(self) -> OrderedDict:
        return OrderedDict([
            ("type", self.type),
            ("version", self.version),
            ("create_date", self.create_date),
            ("date", self.date),
            ("attribute", self.attribute),
            ("content", self.content),
            ("comment", self.comment),
            ("label_list", [list(pair) for pair in self.label_list]),
        ])

    @classmethod
    def from_dict(cls, data: dict) -> 'LabelTask':
        raw = data.get("label_list", [])
        pairs = [(item[0], item[1]) if isinstance(item, list) and len(item) >= 2 else ("", "")
                 for item in raw]
        return cls(
            date=data.get("date", ""),
            attribute=data.get("attribute", ""),
            content=data.get("content", ""),
            comment=data.get("comment", ""),
            create_date=data.get("create_date", ""),
            label_list=pairs,
        )

    def matches_search(self, query: str) -> bool:
        q = query.lower()
        if any(q in str(f).lower() for f in [
            self.date, self.attribute, self.content, self.comment
        ]):
            return True
        for key, value in self.label_list:
            if q in key.lower() or q in value.lower():
                return True
        return False

    def __str__(self) -> str:
        labels = ", ".join(f"{k}={v}" for k, v in self.label_list)
        return f"{self.date}|{self.attribute}|{self.content} [{labels}]"
