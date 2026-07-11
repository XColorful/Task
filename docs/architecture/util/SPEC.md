# SPEC: util — 工具类

> 对应源码路径: `src/util/`
> 提供 JSON 读写、日期格式化、字符串解析、文件操作、剪贴板等通用工具。所有类均为纯静态方法集合，无状态、无依赖注入。

## 1. json_utils.py — JSON 文件读写

```python
import json
import os
from collections import OrderedDict


class JsonUtils:
    """JSON 文件读写工具。统一使用 OrderedDict 保持字段顺序。"""

    @staticmethod
    def load_json(path: str) -> dict | list:
        """从文件读取 JSON，返回 OrderedDict（保持插入顺序）。

        Args:
            path: JSON 文件路径

        Returns:
            dict | list: 解析结果（对象返回 OrderedDict，数组返回 list）

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: JSON 解析失败（如格式错误、编码问题）
        """
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f, object_pairs_hook=OrderedDict)

    @staticmethod
    def save_json(path: str, data, atomic: bool = True) -> None:
        """将数据写入 JSON 文件。atomic=True 时使用临时文件 + rename 保证原子性。

        Args:
            path: 目标文件路径
            data: 待序列化对象（dict 或 list）
            atomic: 是否原子写入（默认 True）
                - True: 写到 path.tmp → os.replace(tmp, path)
                - False: 直接覆盖写入

        序列化参数:
        - ensure_ascii=False（保留中文）
        - indent=2（可读缩进）
        - default=str（fallback 序列化）
        """
        json_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        if atomic:
            tmp_path = path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            os.replace(tmp_path, path)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)
```

## 2. date_utils.py — 日期时间工具

```python
from datetime import datetime
import re


class DateUtils:
    """日期时间格式化与校验工具。全部静态方法。"""

    # 日期格式常量
    DATE_FORMAT = "%Y_%m_%d"           # "YYYY_MM_DD"
    DATETIME_FORMAT = "%Y_%m_%d-%H:%M"  # "YYYY_MM_DD-HH:MM"

    @staticmethod
    def today_str() -> str:
        """返回今天日期字符串。

        Returns:
            str: 格式 "YYYY_MM_DD"（如 "2026_07_11"）
        """
        return datetime.now().strftime(DateUtils.DATE_FORMAT)

    @staticmethod
    def now_str() -> str:
        """返回当前日期时间字符串。

        Returns:
            str: 格式 "YYYY_MM_DD-HH:MM"（如 "2026_07_11-14:30"）
        """
        return datetime.now().strftime(DateUtils.DATETIME_FORMAT)

    @staticmethod
    def parse_date(date_str: str) -> datetime | None:
        """解析日期字符串为 datetime 对象。

        支持的格式（按优先级尝试）:
        - "YYYY_MM_DD"            → datetime
        - "YYYY_MM_DD-HH:MM"     → datetime
        - "YYYY-MM-DD"           → datetime（兼容破折号）
        - "YYYY/MM/DD"           → datetime（兼容斜杠）

        Args:
            date_str: 日期字符串

        Returns:
            datetime | None: 解析成功返回 datetime，失败返回 None
        """
        if not date_str:
            return None
        formats = [
            "%Y_%m_%d",
            "%Y_%m_%d-%H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def format_duration(minutes: int) -> str:
        """格式化分钟数为可读时长字符串。

        >>> DateUtils.format_duration(0)
        '0m'
        >>> DateUtils.format_duration(3255)
        '2d 6h 15m'
        >>> DateUtils.format_duration(-1)
        'Error'

        Args:
            minutes: 分钟数（非负整数）

        Returns:
            str: 格式化后的时长字符串。负数返回 "Error"。
        """
        if minutes < 0:
            return "Error"
        days, remainder = divmod(minutes, 1440)
        hours, mins = divmod(remainder, 60)
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if mins > 0:
            parts.append(f"{mins}m")
        return " ".join(parts) if parts else "0m"

    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """校验字符串是否为合法的 YYYY_MM_DD 格式日期。

        Args:
            date_str: 待校验字符串

        Returns:
            bool: 格式合法且为真实日期返回 True
        """
        if not date_str:
            return False
        # 格式校验
        if not re.match(r"^\d{4}_\d{2}_\d{2}$", date_str):
            return False
        # 真实性校验（排除 2026_02_30 等非法日期）
        try:
            datetime.strptime(date_str, DateUtils.DATE_FORMAT)
            return True
        except ValueError:
            return False
```

## 3. string_utils.py — 字符串解析工具

```python
class StringUtils:
    """字符串内容解析工具。用于处理用户输入的复合内容格式。"""

    @staticmethod
    def parse_semicolon_content(content: str) -> list[str]:
        """按 "; " 分割内容字符串为多条目列表。

        用于解析 content 字段中的多条记录（如 "事项A; 事项B; 事项C"）。

        Args:
            content: 待分割的原始字符串

        Returns:
            list[str]: 去空白后的条目列表。空字符串返回空列表。

        >>> StringUtils.parse_semicolon_content("a; b; c")
        ['a', 'b', 'c']
        >>> StringUtils.parse_semicolon_content("only one")
        ['only one']
        >>> StringUtils.parse_semicolon_content("")
        []
        """
        if not content or not content.strip():
            return []
        return [part.strip() for part in content.split("; ") if part.strip()]

    @staticmethod
    def extract_key_value(content: str, key: str) -> str | None:
        """从内容字符串中提取 key=value 格式的值。

        用于解析 content 中的参数化信息。
        匹配模式: "{key}=<value>"，其中 <value> 延续到下一个 "; " 或行尾。

        Args:
            content: 原始内容字符串
            key: 要查找的键名

        Returns:
            str | None: 匹配到的值（已去空白），未找到返回 None

        >>> StringUtils.extract_key_value("priority=high; tag=urgent", "priority")
        'high'
        >>> StringUtils.extract_key_value("priority=high; tag=urgent", "tag")
        'urgent'
        >>> StringUtils.extract_key_value("no key here", "priority")
        None
        """
        if not content or not key:
            return None
        import re
        pattern = re.escape(key) + r"=([^;]*)"
        m = re.search(pattern, content)
        if m:
            return m.group(1).strip()
        return None
```

## 4. file_utils.py — 文件操作工具

```python
import os


class FileUtils:
    """文件系统操作工具。全部静态方法。"""

    @staticmethod
    def atomic_write(path: str, data: str | bytes,
                     serializer=None) -> None:
        """原子写入文件——先写 .tmp 再 os.replace()。

        Args:
            path: 目标文件路径
            data: 待写入内容（str 或 bytes）
            serializer: 可选的序列化函数 callable(data, path) → None。
                       为 None 时直接以文本模式写入 data。
        """
        if serializer:
            # 委托给 serializer（如 json.dump），由它处理写入
            tmp_path = path + ".tmp"
            serializer(data, tmp_path)
            os.replace(tmp_path, path)
            return

        # 默认行为: 文本写入
        tmp_path = path + ".tmp"
        mode = "wb" if isinstance(data, bytes) else "w"
        encoding = None if isinstance(data, bytes) else "utf-8"
        with open(tmp_path, mode, encoding=encoding) as f:
            f.write(data)
        os.replace(tmp_path, path)

    @staticmethod
    def safe_join(base: str, *parts: str) -> str:
        """安全路径拼接——防止路径穿越攻击。

        将 parts 中的 ".." 和绝对路径成分规范化后拼接，
        并验证结果仍在 base 之下。

        Args:
            base: 基准目录
            *parts: 要拼接的路径组件

        Returns:
            str: 安全拼接后的绝对路径

        Raises:
            ValueError: 拼接结果超出 base 目录范围（路径穿越）
        """
        full = os.path.normpath(os.path.join(base, *parts))
        if not full.startswith(os.path.normpath(base)):
            raise ValueError(
                f"路径穿越检测: {full} 超出基础目录 {base}"
            )
        return full

    @staticmethod
    def ensure_dir(path: str) -> None:
        """确保目录存在，不存在则递归创建。

        Args:
            path: 目录路径
        """
        os.makedirs(path, exist_ok=True)
```

## 5. clipboard_utils.py — 剪贴板工具

```python
class ClipboardUtils:
    """系统剪贴板读写工具。封装 pyperclip 库。"""

    @staticmethod
    def copy_to_clipboard(text: str) -> None:
        """将文本复制到系统剪贴板。

        Args:
            text: 要复制的文本

        Raises:
            RuntimeError: pyperclip 不可用或系统剪贴板访问失败
        """
        import pyperclip
        pyperclip.copy(text)

    @staticmethod
    def get_clipboard_text() -> str:
        """从系统剪贴板获取文本内容。

        Returns:
            str: 剪贴板中的文本。剪贴板为空返回 ""。

        Raises:
            RuntimeError: pyperclip 不可用或系统剪贴板访问失败
        """
        import pyperclip
        return pyperclip.paste() or ""
```

## 6. 依赖关系

```
util/
├── json_utils.py        # 依赖: json, os, collections.OrderedDict
├── date_utils.py        # 依赖: datetime, re
├── string_utils.py      # 依赖: re (纯 Python)
├── file_utils.py        # 依赖: os
├── clipboard_utils.py   # 依赖: pyperclip (第三方)
└── __init__.py
```

### 设计原则

1. **全静态方法**: 所有工具类不维护实例状态，不持有资源句柄。每次调用独立、可重入。
2. **无依赖注入**: 工具类不依赖核心层或 UI 层，仅依赖标准库或轻量第三方库（pyperclip）。
3. **失败不崩溃**: 解析/格式化方法在输入不合法时返回 None 或合理默认值，不抛异常。仅在文件 I/O 层（JsonUtils.load_json, FileUtils.atomic_write）保留异常传播。
4. **OrderedDict 一致**: 所有 JSON 读写使用 `object_pairs_hook=OrderedDict`，保持字段插入顺序与写入顺序一致。
