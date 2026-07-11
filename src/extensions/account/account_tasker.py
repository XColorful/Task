"""Account Tasker — 账号管理容器。支持密码查询与自动复制。"""

from core.abstract import BaseTasker, BaseTask


class AccountTasker(BaseTasker):
    """账号管理 Tasker。"""

    def __init__(self, tasker_id: str = "", label: str = "",
                 description: str = "", folder: str = ""):
        super().__init__()
        self.type = "account"
        self.version = "account"
        self.tasker_id = tasker_id
        self.label = label
        self.description = description
        self.folder = folder

    def get_commands(self) -> list[str]:
        return ["get", "new", "edit", "delete", "search", "copy", "list", "backup"]

    def query_password(self, query: str) -> list[tuple[int, 'AccountTask']]:
        """搜索密码。按 label_alias > account_type 优先级排序。
        label 完全匹配优先于部分匹配。
        """
        from .account_task import AccountTask

        exact_label = []
        partial_label = []
        exact_type = []
        partial_type = []
        other = []

        for i, t in enumerate(self.task_list):
            if not isinstance(t, AccountTask):
                continue
            q = query.lower()

            if q == t.label_alias.lower():
                exact_label.append((i, t))
            elif q in t.label_alias.lower():
                partial_label.append((i, t))
            elif q == t.account_type.lower():
                exact_type.append((i, t))
            elif q in t.account_type.lower():
                partial_type.append((i, t))
            elif t.matches_search(query):
                other.append((i, t))

        return exact_label + partial_label + exact_type + partial_type + other

    def get_and_copy(self, query: str) -> 'AccountTask | None':
        """搜索并自动复制密码到剪贴板。唯一匹配时复制。"""
        results = self.query_password(query)
        if len(results) == 1:
            _, task = results[0]
            from util.clipboard_utils import copy_to_clipboard
            if task.password:
                copy_to_clipboard(task.password)
            return task
        return None

    def create_task(self, fields: dict) -> BaseTask:
        from .account_task import AccountTask
        return AccountTask(
            date=fields.get("date", ""),
            attribute=fields.get("attribute", ""),
            content=fields.get("content", ""),
            comment=fields.get("comment", ""),
            account_type=fields.get("account_type", ""),
            label_alias=fields.get("label_alias", fields.get("account_type", "")),
            password=fields.get("password", ""),
            supplementary=fields.get("supplementary", {}),
        )

    def execute_quick_button(self, button_template: dict) -> BaseTask | None:
        preset = button_template.get("preset", {})
        from util.date_utils import today_str
        fields = {
            "date": today_str() if preset.get("use_default_date") else preset.get("date", today_str()),
            "attribute": preset.get("attribute", ""),
            "content": preset.get("content", ""),
            "comment": preset.get("comment", ""),
            "account_type": preset.get("attribute", ""),
            "label_alias": preset.get("content", ""),
            "password": "",
            "supplementary": {},
        }
        if not fields["account_type"]:
            return None
        return self.create_task(fields)

    def mark_dirty(self, segment_filename: str) -> None:
        self.dirty_segments.add(segment_filename)
