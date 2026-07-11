"""剪贴板操作——密码复制与定时清除。"""

import threading


class PasswordClipboard:
    """剪贴板密码管理。复制后定时清除。"""

    _timer: threading.Timer | None = None
    _default_timeout: int = 30

    @classmethod
    def copy(cls, password: str, timeout_seconds: int | None = None) -> None:
        """复制密码到剪贴板，定时清除。

        Args:
            password: 密码明文
            timeout_seconds: 清除等待秒数，默认 30
        """
        from util.clipboard_utils import copy_to_clipboard
        copy_to_clipboard(password)
        cls._schedule_clear(timeout_seconds or cls._default_timeout)

    @classmethod
    def clear(cls) -> None:
        """立即清除剪贴板。"""
        from util.clipboard_utils import copy_to_clipboard
        copy_to_clipboard("")
        if cls._timer:
            cls._timer.cancel()
            cls._timer = None

    @classmethod
    def extend(cls, extra_seconds: int = 30) -> None:
        """延长清除计时。"""
        cls._schedule_clear(extra_seconds)

    @classmethod
    def set_default_timeout(cls, seconds: int) -> None:
        cls._default_timeout = seconds

    @classmethod
    def _schedule_clear(cls, seconds: int) -> None:
        if cls._timer:
            cls._timer.cancel()
        cls._timer = threading.Timer(seconds, cls.clear)
        cls._timer.daemon = True
        cls._timer.start()
