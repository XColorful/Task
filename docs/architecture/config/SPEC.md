# SPEC: config — 配置管理

> 对应源码路径: `src/config/`
> 负责应用配置的单例持有、持久化读写、默认值管理。

## 1. app_config.py — 配置单例

```python
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AppConfig:
    """应用配置单例。持有全部可配置项，提供读写接口。

    配置项通过 ConfigStore 持久化到 config.json。
    启动时加载一次，运行时直接读写内存字段，仅在用户主动保存或退出时写回磁盘。

    单例模式——全局唯一实例（模块级变量或显式 singleton 管理）。
    """

    # --- 数据存储 ---
    data_dir: str = "./data"
    """数据根目录路径。所有 Tasker 文件夹和 taskers.json 存放在此目录下。"""

    # --- 快捷键 ---
    hotkey_combo: str = "Ctrl+Alt+T"
    """全局热键组合（用于唤起/隐藏主窗口）。格式参考 keyboard 库文档。"""

    # --- 窗口 ---
    window_size: tuple[int, int] = (900, 600)
    """窗口大小 (width, height)，单位像素。关闭窗口时自动保存当前值。"""

    window_position: tuple[int, int] = (100, 100)
    """窗口左上角位置 (x, y)，单位像素。关闭窗口时自动保存当前值。"""

    # --- HTTP 服务 ---
    http_port: int = 19527
    """图表模式下的本地 HTTP 服务端口。默认 19527。"""

    # --- 自动保存 ---
    auto_save_interval_ms: int = 500
    """自动保存防抖间隔（毫秒）。每次数据变更后重置计时器。"""

    # --- 分段存储 ---
    max_segment_size: int = 500
    """每个 segment JSON 文件的最大记录数。超出后新建 segment_{n+1}.json。"""

    # --- UI ---
    recent_task_count: int = 20
    """进入 Tasker 界面时默认显示的最近记录数（两段懒加载的初始数量）。"""

    # ================================================================
    # 单例管理
    # ================================================================

    _instance: 'AppConfig | None' = None

    @classmethod
    def get_instance(cls) -> 'AppConfig':
        """获取全局唯一实例。首次调用时创建默认实例。"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def initialize(cls, config_path: str) -> 'AppConfig':
        """从 config.json 加载配置并设为首例。

        Args:
            config_path: config.json 文件路径

        Returns:
            AppConfig: 加载后的实例
        """
        store = ConfigStore(config_path)
        defaults = store.load_defaults()
        merged = store.load()  # 文件值覆盖默认值
        cls._instance = cls(**merged)
        return cls._instance

    # ================================================================
    # 批量读写
    # ================================================================

    def to_dict(self) -> dict:
        """将所有配置项序列化为字典（用于写入 config.json）。

        Returns:
            dict: 配置字典，key 为配置项名，value 为当前值
        """
        return {
            "data_dir": self.data_dir,
            "hotkey_combo": self.hotkey_combo,
            "window_size": list(self.window_size),
            "window_position": list(self.window_position),
            "http_port": self.http_port,
            "auto_save_interval_ms": self.auto_save_interval_ms,
            "max_segment_size": self.max_segment_size,
            "recent_task_count": self.recent_task_count,
        }

    def update_from_dict(self, data: dict) -> None:
        """从字典批量更新配置项。仅更新字典中存在的 key。

        Args:
            data: 配置字典（如从 config.json 加载的内容）
        """
        for key, value in data.items():
            if hasattr(self, key):
                if key in ("window_size", "window_position"):
                    setattr(self, key, tuple(value))
                else:
                    setattr(self, key, value)
```

## 2. config_store.py — 配置持久化

```python
import os
from collections import OrderedDict

class ConfigStore:
    """管理 config.json 的读写。启动时加载，设置保存时写入。

    原子写入策略: 先写 .tmp 再 os.replace()，保证写入过程不会损坏已有文件。
    """

    def __init__(self, config_path: str) -> None:
        """
        Args:
            config_path: config.json 的完整路径（如 "./config.json"）
        """
        self._path = config_path

    def load_defaults(self) -> dict:
        """返回所有配置项的默认值字典。

        Returns:
            dict: 完整的默认配置
        """
        return {
            "data_dir": "./data",
            "hotkey_combo": "Ctrl+Alt+T",
            "window_size": [900, 600],
            "window_position": [100, 100],
            "http_port": 19527,
            "auto_save_interval_ms": 500,
            "max_segment_size": 500,
            "recent_task_count": 20,
        }

    def load(self) -> dict:
        """从 config.json 读取配置，以默认值为基底，文件值覆盖。

        行为:
        1. 获取完整默认值字典
        2. 如果 config.json 不存在 → 返回默认值（不创建文件）
        3. 如果存在 → 读取 JSON → 用文件中的 key 覆盖默认值中的对应项
           （仅覆盖文件中存在的 key，不支持删除配置项）

        Returns:
            dict: 合并后的配置字典
        """
        defaults = self.load_defaults()
        if not os.path.isfile(self._path):
            return defaults

        try:
            from util.json_utils import JsonUtils
            file_data = JsonUtils.load_json(self._path)
            if isinstance(file_data, dict):
                # 仅覆盖存在的 key，忽略文件中多余的未知 key
                for key in defaults:
                    if key in file_data:
                        defaults[key] = file_data[key]
        except (ValueError, OSError):
            # 文件损坏时 fallback 到默认值，不崩溃
            pass

        return defaults

    def save(self, config_dict: dict) -> None:
        """将配置字典写入 config.json（原子写入）。

        Args:
            config_dict: 完整配置字典（来自 AppConfig.to_dict()）
        """
        from util.json_utils import JsonUtils
        JsonUtils.save_json(self._path, config_dict, atomic=True)

    def exists(self) -> bool:
        """检查 config.json 是否已存在。"""
        return os.path.isfile(self._path)
```

## 3. 依赖关系

```
config/
├── app_config.py    # 依赖: config_store.py, dataclasses
├── config_store.py  # 依赖: util/json_utils.py
└── __init__.py
```
