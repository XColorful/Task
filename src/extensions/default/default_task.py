"""Default Task — 四字段日常记录（date, attribute, content, comment）。"""

from collections import OrderedDict
from core.abstract import BaseTask


class DefaultTask(BaseTask):
    """四字段日常记录 Task。最基础且最常用的记录类型。"""

    def __init__(self, date: str = "", attribute: str = "N/A",
                 content: str = "", comment: str = ""):
        super().__init__()
        self.type = "default"
        self.version = "1.0"
        self.date = date
        self.attribute = attribute
        self.content = content
        self.comment = comment

    def to_dict(self) -> OrderedDict:
        return OrderedDict([
            ("type", self.type),
            ("version", self.version),
            ("date", self.date),
            ("attribute", self.attribute),
            ("content", self.content),
            ("comment", self.comment),
        ])

    @classmethod
    def from_dict(cls, data: dict) -> 'DefaultTask':
        return cls(
            date=data.get("date", ""),
            attribute=data.get("attribute", "N/A"),
            content=data.get("content", ""),
            comment=data.get("comment", ""),
        )

    def matches_search(self, query: str) -> bool:
        q = query.lower()
        return any(q in str(f).lower() for f in [
            self.date, self.attribute, self.content, self.comment
        ])

    def __str__(self) -> str:
        return f"{self.date}|{self.attribute}|{self.content}"
