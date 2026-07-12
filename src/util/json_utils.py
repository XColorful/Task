"""JSON 文件读写工具——统一使用 OrderedDict 保持字段顺序。"""

import json
import os
from collections import OrderedDict


class JsonUtils:
    """JSON 文件读写工具。全部静态方法。"""

    @staticmethod
    def load_json(path: str) -> dict | list:
        """从文件读取 JSON，返回 OrderedDict（保持插入顺序）。

        Args:
            path: JSON 文件路径

        Returns:
            dict | list: 解析结果

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: JSON 解析失败
        """
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f, object_pairs_hook=OrderedDict)

    @staticmethod
    def save_json(path: str, data, atomic: bool = True) -> None:
        """将数据写入 JSON 文件。atomic=True 时使用临时文件 + rename 保证原子性。

        Args:
            path: 目标文件路径
            data: 待序列化对象
            atomic: 是否原子写入（默认 True）
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
