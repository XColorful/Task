"""配置单例——持有全部可配置项，通过 ConfigStore 持久化。"""

from dataclasses import dataclass
from typing import Any


@dataclass
class AppConfig:
    """应用配置单例。启动时加载一次，运行时直接读写内存字段。"""

    # --- 数据存储 ---
    data_dir: str = "./data"
    hotkey_combo: str = "Ctrl+Alt+T"
    window_size: tuple[int, int] = (900, 600)
    window_position: tuple[int, int] = (100, 100)
    http_port: int = 19527
    auto_save_interval_ms: int = 500
    max_segment_size: int = 500
    recent_task_count: int = 20

    # --- 单例管理 ---
    _instance: 'AppConfig | None' = None

    @classmethod
    def get_instance(cls) -> 'AppConfig':
        """获取单例。首次调用时自动创建默认实例。"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def initialize(cls, config_path: str) -> 'AppConfig':
        """从配置文件初始化单例。如果文件不存在则使用默认值。

        Args:
            config_path: config.json 文件路径
        """
        from config.config_store import ConfigStore
        from util.json_utils import JsonUtils

        try:
            data = JsonUtils.load_json(config_path)
            cfg = cls(**data)
        except (FileNotFoundError, KeyError, TypeError):
            cfg = cls()

        # 从文件恢复 tuple 类型字段
        if isinstance(cfg.window_size, list):
            cfg.window_size = tuple(cfg.window_size)
        if isinstance(cfg.window_position, list):
            cfg.window_position = tuple(cfg.window_position)

        cfg._config_path = config_path
        cls._instance = cfg
        return cfg

    _config_path: str = "./config.json"

    def to_dict(self) -> dict:
        """转换为可序列化的 dict。"""
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
        """从 dict 批量更新配置字段。"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
