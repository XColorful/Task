"""Timer Task — 计时器记录。包含起止时间和时长计算。"""

from collections import OrderedDict
from datetime import datetime
from core.abstract import BaseTask


class TimerTask(BaseTask):
    """计时器记录 Task。"""

    start_time: str = ""
    end_time: str = ""

    def __init__(self, date: str = "", attribute: str = "",
                 content: str = "", comment: str = "",
                 create_date: str = "",
                 start_time: str = "", end_time: str = ""):
        super().__init__()
        self.type = "timer"
        self.version = "timer"
        self.create_date = create_date
        self.date = date
        self.attribute = attribute
        self.content = content
        self.comment = comment
        self.start_time = start_time
        self.end_time = end_time

    @property
    def is_running(self) -> bool:
        return self.end_time == ""

    @property
    def duration_minutes(self) -> int | None:
        if self.is_running:
            return None
        fmt = "%Y_%m_%d-%H:%M"
        try:
            t1 = datetime.strptime(self.start_time, fmt)
            t2 = datetime.strptime(self.end_time, fmt)
            return int((t2 - t1).total_seconds() / 60)
        except ValueError:
            return 0

    def to_dict(self) -> OrderedDict:
        return OrderedDict([
            ("type", self.type),
            ("version", self.version),
            ("create_date", self.create_date),
            ("date", self.date),
            ("attribute", self.attribute),
            ("content", self.content),
            ("comment", self.comment),
            ("start_time", self.start_time),
            ("end_time", self.end_time),
        ])

    @classmethod
    def from_dict(cls, data: dict) -> 'TimerTask':
        return cls(
            date=data.get("date", ""),
            attribute=data.get("attribute", ""),
            content=data.get("content", ""),
            comment=data.get("comment", ""),
            create_date=data.get("create_date", ""),
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
        )

    def matches_search(self, query: str) -> bool:
        q = query.lower()
        fields = [
            self.date, self.attribute, self.content, self.comment,
            self.start_time, self.end_time,
        ]
        return any(q in str(f).lower() for f in fields)

    def __str__(self) -> str:
        return f"{self.start_time}|{self.end_time}|{self.attribute}|{self.content}"
