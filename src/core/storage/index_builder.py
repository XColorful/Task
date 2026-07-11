"""索引重建——数据恢复工具。扫描磁盘上的 Tasker 文件夹重建 taskers.json。"""

import os
import json
from collections import OrderedDict


class IndexBuilder:
    """数据恢复工具——扫描磁盘上的 Tasker 文件夹重建 taskers.json。"""

    @staticmethod
    def rebuild(data_dir: str) -> list[dict]:
        """扫描 data_dir 下的所有文件夹，重建 Tasker 列表。

        每个子文件夹必须有有效的 segment 文件才被识别为 Tasker。
        恢复的 Tasker 信息从 segment 数据推断。

        Args:
            data_dir: 数据根目录路径

        Returns:
            list[dict]: 重建的 Tasker 列表
        """
        taskers = []
        if not os.path.isdir(data_dir):
            return taskers

        for folder_name in sorted(os.listdir(data_dir)):
            folder_path = os.path.join(data_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue

            # 检查是否有 segment 文件
            segment_files = [f for f in os.listdir(folder_path)
                             if f.startswith('segment_') and f.endswith('.json')]
            if not segment_files:
                continue

            # 从第一个 segment 的第一条 Task 推断类型
            segment_files.sort()
            first_seg = os.path.join(folder_path, segment_files[0])
            try:
                with open(first_seg, 'r', encoding='utf-8') as f:
                    data = json.load(f, object_pairs_hook=OrderedDict)
                tasks = data.get('tasks', [])
                task_type = tasks[0].get('type', 'default') if tasks else 'default'
            except (FileNotFoundError, json.JSONDecodeError, IndexError, KeyError):
                task_type = 'default'

            # 从文件夹名提取 label 和 id
            # 格式: "{label}_{id前8位}"
            parts = folder_name.rsplit('_', 1)
            label = parts[0] if len(parts) == 2 else folder_name
            tasker_id = parts[1] if len(parts) == 2 else folder_name

            taskers.append(OrderedDict([
                ('id', tasker_id),
                ('type', task_type),
                ('label', label),
                ('description', ''),
                ('folder', folder_name),
                ('quick_buttons', []),
            ]))

        return taskers
