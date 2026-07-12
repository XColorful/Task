# SPEC: extensions/account — 账号密码管理模块

> 对应源码路径: `src/extensions/account/`
> 管理各类平台的账号、密码及补充信息。提供密码查询、展示、复制到剪贴板及定时清除功能。

## 1. account_task.py

```python
from core.abstract import BaseTask
from collections import OrderedDict


class AccountTask(BaseTask):
    """账号密码记录 Task。

    额外字段:
        account_type: 账号平台类型 ("email", "game", "social", "bank", ...)
        label:        搜索别名，默认取 account_type
        password:     密码明文（存储时按需加密）
        supplementary: 补充信息字典，info_key → list[str]

    supplementary 的已知 key:
        description, login_name, verified_phone, verified_email,
        linked_account, secure_question, other_info, password_history
    """

    account_type: str = ""
    label: str = ""
    password: str = ""
    supplementary: dict[str, list[str]]

    def __init__(
        self,
        date: str = "",
        attribute: str = "",
        content: str = "",
        comment: str = "",
        account_type: str = "",
        label: str = "",
        password: str = "",
        supplementary: dict[str, list[str]] | None = None,
    ):
        super().__init__()
        self.type = "account"
        self.version = "1.0"
        self.date = date
        self.attribute = attribute
        self.content = content
        self.comment = comment
        self.account_type = account_type
        self.label = label or account_type
        self.password = password
        self.supplementary = supplementary or {}

    # ------------------------------------------------------------------
    # 便利访问器 —— 按搜索优先级排列的检索属性列表
    # ------------------------------------------------------------------

    @property
    def search_keys(self) -> list[str]:
        """搜索匹配的候选字段，按优先级排列:
        label > index(同content) > account_type > linked_account
        """
        keys = [
            self.label,
            self.content,          # index —— 与旧项目兼容的搜索名
            self.account_type,
        ]
        linked = self.supplementary.get("linked_account", [])
        if linked:
            keys.extend(linked)
        return keys

    @property
    def linked_account(self) -> list[str]:
        """快捷获取关联账号列表。"""
        return self.supplementary.get("linked_account", [])

    @property
    def login_name(self) -> list[str]:
        return self.supplementary.get("login_name", [])

    @property
    def verified_phone(self) -> list[str]:
        return self.supplementary.get("verified_phone", [])

    @property
    def verified_email(self) -> list[str]:
        return self.supplementary.get("verified_email", [])

    @property
    def secure_question(self) -> list[str]:
        return self.supplementary.get("secure_question", [])

    @property
    def password_history(self) -> list[str]:
        return self.supplementary.get("password_history", [])

    # ------------------------------------------------------------------
    # 序列化
    # ------------------------------------------------------------------

    def to_dict(self) -> OrderedDict:
        """序列化 —— 字段顺序:
        type, version, date, attribute, content, comment,
        account_type, label, password, supplementary
        """
        return OrderedDict([
            ("type", self.type),
            ("version", self.version),
            ("date", self.date),
            ("attribute", self.attribute),
            ("content", self.content),
            ("comment", self.comment),
            ("account_type", self.account_type),
            ("label", self.label),
            ("password", self.password),
            ("supplementary", self.supplementary),
        ])

    @classmethod
    def from_dict(cls, data: dict) -> 'AccountTask':
        """从字典反序列化。supplementary 为空时默认使用空 dict。"""
        return cls(
            date=data.get("date", ""),
            attribute=data.get("attribute", ""),
            content=data.get("content", ""),
            comment=data.get("comment", ""),
            account_type=data.get("account_type", ""),
            label=data.get("label", ""),
            password=data.get("password", ""),
            supplementary=data.get("supplementary", {}),
        )

    # ------------------------------------------------------------------
    # 搜索
    # ------------------------------------------------------------------

    def matches_search(self, query: str) -> bool:
        """搜索范围: date, attribute, content, comment,
        account_type, label, 以及 supplementary 中所有字段的展开值。

        搜索优先级由 search_keys 定义；此处为全文匹配不排序。
        """
        q = query.lower()
        candidates = [
            self.date, self.attribute, self.content, self.comment,
            self.account_type, self.label,
        ]
        # 展开 supplementary 全部值
        for values in self.supplementary.values():
            candidates.extend(values)
        return any(q in str(f).lower() for f in candidates if f)

    def __str__(self) -> str:
        return f"{self.account_type}|{self.label}|{self.content}"
```

## 2. account_tasker.py

```python
from core.abstract import BaseTasker, BaseTask
from core.types import QuickButtonDef


class AccountTasker(BaseTasker):
    """账号管理 Tasker。提供密码查询与复制功能。

    搜索行为:
        - get 指令按 search_keys 优先级排序结果
        - 唯一匹配时自动将密码复制到剪贴板
        - 多条匹配时展示列表供用户选择
    """

    def __init__(
        self,
        tasker_id: str = "",
        label: str = "",
        description: str = "",
        folder: str = "",
        quick_buttons: list[QuickButtonDef] | None = None,
    ):
        super().__init__()
        self.type = "account"
        self.version = "1.0"
        self.tasker_id = tasker_id
        self.label = label
        self.description = description
        self.folder = folder
        self._quick_buttons: list[QuickButtonDef] = quick_buttons or []

    # ------------------------------------------------------------------
    # 指令集
    # ------------------------------------------------------------------

    def get_commands(self) -> list[str]:
        return ["get", "new", "edit", "delete", "search", "copy", "list", "backup"]

    # ------------------------------------------------------------------
    # 密码查询核心逻辑
    # ------------------------------------------------------------------

    def query_password(self, query: str) -> list[tuple[int, 'AccountTask']]:
        """按 search_keys 优先级搜索并返回排序后的匹配列表。

        排序规则:
            1. label 精确匹配最高
            2. label 部分匹配次之
            3. content (index) 匹配
            4. account_type 匹配
            5. linked_account 匹配

        Returns:
            list[tuple[int, AccountTask]]: (task_list 索引, Task) 按优先级排序
        """
        from .account_task import AccountTask

        results: list[tuple[int, int, AccountTask]] = []  # (index, priority, task)

        for idx, task in enumerate(self.task_list):
            if not isinstance(task, AccountTask):
                continue
            if not task.matches_search(query):
                continue

            # 计算优先级 (越小越靠前)
            q = query.lower()
            priority = 99
            if q == task.label.lower():
                priority = 0
            elif q in task.label.lower():
                priority = 1
            elif q in task.content.lower():
                priority = 2
            elif q in task.account_type.lower():
                priority = 3
            elif any(q in la.lower() for la in task.linked_account):
                priority = 4
            results.append((idx, priority, task))

        results.sort(key=lambda x: x[1])
        return [(idx, task) for idx, _, task in results]

    def get_and_copy(self, query: str) -> 'AccountTask | None':
        """查询并自动复制密码。

        - 无匹配 → 返回 None
        - 唯一匹配 → 复制密码到剪贴板，返回该 Task
        - 多条匹配 → 返回 None（由调用方展示列表供用户选择）

        Returns:
            唯一匹配的 AccountTask，或 None
        """
        matches = self.query_password(query)
        if len(matches) == 1:
            _, task = matches[0]
            if task.password:
                from .password_clipboard import PasswordClipboard
                PasswordClipboard.copy(task.password)
            return task
        return None  # 0 或多条匹配由调用方处理

    # ------------------------------------------------------------------
    # Task 生命周期
    # ------------------------------------------------------------------

    def create_task(self, fields: dict) -> BaseTask:
        """从字段 dict 创建 AccountTask。

        fields 可包含:
            date, attribute, content, comment (继承自 BaseTask)
            account_type, label, password,
            supplementary (dict[str, list[str]])
        """
        from .account_task import AccountTask
        from util.date_utils import today_str

        return AccountTask(
            date=fields.get("date", today_str()),
            attribute=fields.get("attribute", ""),
            content=fields.get("content", ""),
            comment=fields.get("comment", ""),
            account_type=fields.get("account_type", ""),
            label=fields.get("label", ""),
            password=fields.get("password", ""),
            supplementary=fields.get("supplementary", {}),
        )

    def execute_quick_button(self, button_template: dict) -> BaseTask | None:
        """快捷按钮触发。preset 中可预填 account_type 等字段。"""
        preset = button_template.get("preset", {})
        from util.date_utils import today_str
        fields = {
            "date": today_str() if preset.get("use_default_date") else preset.get("date", today_str()),
            "attribute": preset.get("attribute", ""),
            "content": preset.get("content", ""),
            "comment": preset.get("comment", ""),
            "account_type": preset.get("account_type", ""),
            "label": preset.get("label", ""),
            "password": preset.get("password", ""),
            "supplementary": preset.get("supplementary", {}),
        }
        if not fields["content"] and not fields["label"]:
            return None
        return self.create_task(fields)

    def mark_dirty(self, segment_filename: str) -> None:
        self.dirty_segments.add(segment_filename)
```

## 3. password_clipboard.py

```python
import threading
from util.clipboard_utils import ClipboardUtils


class PasswordClipboard:
    """剪贴板操作 —— 复制密码并定时清除。

    使用方式:
        PasswordClipboard.copy("my_password")          # 复制，默认 30s 后清除
        PasswordClipboard.copy("my_password", 60)      # 复制，60s 后清除
        PasswordClipboard.clear()                      # 立即清除
    """

    _timer: threading.Timer | None = None
    _default_timeout: int = 30  # 默认超时秒数

    @classmethod
    def copy(cls, password: str, timeout_seconds: int | None = None) -> None:
        """将密码复制到系统剪贴板，并启动定时器自动清除。

        Args:
            password: 要复制的密码字符串
            timeout_seconds: 超时秒数。None 使用默认值 30s，0 表示不清除
        """
        ClipboardUtils.set_text(password)

        timeout = timeout_seconds if timeout_seconds is not None else cls._default_timeout
        if timeout <= 0:
            return

        # 取消已有定时器（防重复）
        cls._cancel_timer()

        cls._timer = threading.Timer(timeout, cls._on_timeout)
        cls._timer.daemon = True
        cls._timer.start()

    @classmethod
    def clear(cls) -> None:
        """立即清除剪贴板中的密码内容（如果剪贴板仍为之前复制的密码）。"""
        cls._cancel_timer()
        ClipboardUtils.clear()

    @classmethod
    def extend(cls, extra_seconds: int = 30) -> None:
        """延长当前密码在剪贴板的保留时间。无活跃定时器时不操作。"""
        if cls._timer is None:
            return
        cls._timer.cancel()
        cls._timer = threading.Timer(extra_seconds, cls._on_timeout)
        cls._timer.daemon = True
        cls._timer.start()

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    @classmethod
    def _on_timeout(cls) -> None:
        """定时器回调 —— 清除剪贴板。"""
        ClipboardUtils.clear()
        cls._timer = None

    @classmethod
    def _cancel_timer(cls) -> None:
        """取消活跃定时器（如有）。"""
        if cls._timer is not None:
            cls._timer.cancel()
            cls._timer = None

    @classmethod
    def set_default_timeout(cls, seconds: int) -> None:
        """修改全局默认超时时间（秒）。"""
        cls._default_timeout = max(0, seconds)
```

## 4. __init__.py — 注册

```python
from core.extension_registry import ExtensionRegistry
from .account_task import AccountTask
from .account_tasker import AccountTasker

# 注册 Task / Tasker 类型
ExtensionRegistry.register_task_type("account", AccountTask)
ExtensionRegistry.register_tasker_type("account", AccountTasker)

# 注册图表页面（预留）
ExtensionRegistry.register_chart_page("account_type_count", "extensions/account/charts/account_type_count.html")
ExtensionRegistry.register_chart_page("password_age", "extensions/account/charts/password_age.html")
```

## 5. 依赖关系

```
extensions/account/
├── account_task.py          # 依赖 core.abstract.BaseTask + collections.OrderedDict
├── account_tasker.py        # 依赖 core.abstract.BaseTasker + core.types.QuickButtonDef
├── password_clipboard.py    # 依赖 util.clipboard_utils + threading
└── __init__.py              # 依赖 core.extension_registry.ExtensionRegistry
```

## 6. 数据流 —— get 指令完整流程

```
用户输入: "get gmail"
  │
  ▼
AccountTasker.query_password("gmail")
  │
  ├─ 遍历 task_list，调用 task.matches_search("gmail")
  │   └─ 搜索 date, attribute, content, comment, account_type, label, supplementary 全部值
  │
  ├─ 对匹配项按 search_keys 优先级排序:
  │   label精确 > label部分 > content(index) > account_type > linked_account
  │
  └─ 返回 [(index, AccountTask), ...]
       │
       ├─ len == 0  → UI: "未找到匹配账号"
       ├─ len == 1  → AccountTasker.get_and_copy() → PasswordClipboard.copy(password)
       │              └─ UI: 展示账号信息 + "密码已复制 (30s 后自动清除)"
       └─ len >  1  → UI: 展示匹配列表供用户点选
                        └─ 用户选择后 → PasswordClipboard.copy(selected.password)
```

## 7. 补充信息字典 —— supplementary 结构示例

```json
{
  "description": ["主邮箱账号"],
  "login_name": ["user@gmail.com"],
  "verified_phone": ["+1-555-0123"],
  "verified_email": ["recovery@outlook.com"],
  "linked_account": ["youtube", "google-drive"],
  "secure_question": ["第一只宠物名字", "母亲 maiden name"],
  "other_info": ["注册于 2019 年", "已开启两步验证"],
  "password_history": ["old_pass_1", "old_pass_2"]
}
```

所有 value 均为 `list[str]`，单值字段也包装为列表。
