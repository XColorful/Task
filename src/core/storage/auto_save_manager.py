"""防抖自动保存调度器——延迟保存，多次调用时重置计时器。"""

import threading


class AutoSaveManager:
    """防抖自动保存调度器。"""

    def __init__(self):
        self._timer: threading.Timer | None = None
        self._pending_callbacks: list = []

    def schedule(self, callback, delay_ms: int = 500) -> None:
        """调度一次延迟保存。如果在延迟期间再次调用，重置计时器（防抖）。

        Args:
            callback: 要执行的回调函数
            delay_ms: 延迟毫秒数
        """
        if self._timer:
            self._timer.cancel()
        self._pending_callbacks.append(callback)
        self._timer = threading.Timer(delay_ms / 1000.0, self._execute)
        self._timer.start()

    def _execute(self) -> None:
        callbacks = self._pending_callbacks[:]
        self._pending_callbacks.clear()
        for cb in callbacks:
            try:
                cb()
            except Exception:
                pass

    def flush(self) -> None:
        """立即执行所有待保存任务。"""
        if self._timer:
            self._timer.cancel()
            self._timer = None
        self._execute()

    def cancel(self) -> None:
        """取消所有待保存任务。"""
        if self._timer:
            self._timer.cancel()
            self._timer = None
        self._pending_callbacks.clear()
