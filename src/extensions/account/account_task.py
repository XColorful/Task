"""Account Task — 账号管理记录。额外字段：account_type, password, 补充信息 dict。"""

from collections import OrderedDict
from core.abstract import BaseTask


class AccountTask(BaseTask):
    """账号管理 Task。"""

    account_type: str = ""
    label_alias: str = ""
    password: str = ""
    supplementary: dict[str, list[str]] = {}

    def __init__(self, date: str = "", attribute: str = "",
                 content: str = "", comment: str = "",
                 create_date: str = "",
                 account_type: str = "", label_alias: str = "",
                 password: str = "",
                 supplementary: dict[str, list[str]] | None = None):
        super().__init__()
        self.type = "account"
        self.version = "account"
        self.create_date = create_date
        self.date = date
        self.attribute = attribute
        self.content = content
        self.comment = comment
        self.account_type = account_type
        self.label_alias = label_alias or account_type
        self.password = password
        self.supplementary = supplementary or {}

    @property
    def search_label(self) -> str:
        return self.label_alias

    def to_dict(self) -> OrderedDict:
        return OrderedDict([
            ("type", self.type),
            ("version", self.version),
            ("create_date", self.create_date),
            ("date", self.date),
            ("attribute", self.attribute),
            ("content", self.content),
            ("comment", self.comment),
            ("account_type", self.account_type),
            ("label_alias", self.label_alias),
            ("password", self.password),
            ("supplementary", self.supplementary),
        ])

    @classmethod
    def from_dict(cls, data: dict) -> 'AccountTask':
        return cls(
            date=data.get("date", ""),
            attribute=data.get("attribute", ""),
            content=data.get("content", ""),
            comment=data.get("comment", ""),
            create_date=data.get("create_date", ""),
            account_type=data.get("account_type", ""),
            label_alias=data.get("label_alias", data.get("account_type", "")),
            password=data.get("password", ""),
            supplementary=data.get("supplementary", {}),
        )

    def matches_search(self, query: str) -> bool:
        q = query.lower()
        # 搜索 label_alias, account_type, content, comment, 和 supplementary 所有值
        if any(q in str(f).lower() for f in [
            self.label_alias, self.account_type, self.content, self.comment
        ]):
            return True
        for values in self.supplementary.values():
            for v in values:
                if q in v.lower():
                    return True
        return False

    def __str__(self) -> str:
        alias = f" ({self.label_alias})" if self.label_alias != self.account_type else ""
        return f"{self.account_type}{alias}"
