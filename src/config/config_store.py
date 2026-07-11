"""配置持久化——config.json 文件的读写。"""

from util.json_utils import JsonUtils


class ConfigStore:
    """配置存储——读写 config.json。"""

    @staticmethod
    def load_defaults() -> dict:
        """返回所有配置项的默认值字典。"""
        from config.app_config import AppConfig
        return AppConfig().to_dict()

    @staticmethod
    def load(config_path: str) -> dict:
        """读取配置文件，缺失项用默认值补齐。

        Args:
            config_path: config.json 文件路径

        Returns:
            dict: 合并后的配置字典
        """
        defaults = ConfigStore.load_defaults()
        try:
            file_data = JsonUtils.load_json(config_path)
            if isinstance(file_data, dict):
                defaults.update(file_data)
        except (FileNotFoundError, ValueError):
            pass
        return defaults

    @staticmethod
    def save(config_path: str, data: dict) -> None:
        """写入配置文件（原子写入）。

        Args:
            config_path: config.json 文件路径
            data: 配置字典
        """
        JsonUtils.save_json(config_path, data, atomic=True)
