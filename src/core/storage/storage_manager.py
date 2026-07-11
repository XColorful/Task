"""存储门面——对外提供统一的存储操作入口。

委托给 TaskerIndexManager, SegmentManager, AutoSaveManager。
"""

import os
from core.storage.tasker_index_manager import TaskerIndexManager
from core.storage.segment_manager import SegmentManager
from core.storage.auto_save_manager import AutoSaveManager


class StorageManager:
    """存储门面（全能易用门面）。"""

    def __init__(self, data_dir: str):
        """
        Args:
            data_dir: 数据根目录路径（如 "./data" 或用户自定义路径）
        """
        self.tasker_index = TaskerIndexManager(data_dir)
        self.segment = SegmentManager(data_dir)
        self.auto_save = AutoSaveManager()
        self._data_dir = data_dir

    # --- 委托给 TaskerIndexManager ---

    def load_tasker_list(self) -> list[dict]:
        """读取 taskers.json 返回 Tasker 简要信息列表（保持 JSON 顺序）。启动时调用。"""
        return self.tasker_index.load()

    def save_tasker_list(self, taskers: list[dict]) -> None:
        """写入 taskers.json。仅在创建/删除/重命名 Tasker、编辑快捷按钮时调用。"""
        self.tasker_index.save(taskers)

    @property
    def data_dir(self) -> str:
        return self._data_dir

    @property
    def taskers_path(self) -> str:
        return self.tasker_index.path

    # --- 委托给 SegmentManager ---

    def load_recent_segments(self, folder: str, count: int = 2) -> list[dict]:
        """加载指定 Tasker 文件夹下最后 count 个 segment 的 Task 列表。

        Args:
            folder: Tasker 文件夹名
            count: 加载的 segment 数量（默认 2）

        Returns:
            list[dict]: 合并后的 Task 字典列表
        """
        return self.segment.load_last(folder, count)

    def load_all_segments(self, folder: str) -> list[dict]:
        """加载指定 Tasker 文件夹下全部 segment 并拼接为完整列表。"""
        return self.segment.load_all(folder)

    def save_segments(self, folder: str, all_tasks: list[dict],
                      loaded: set[str], dirty: set[str],
                      max_per_segment: int = 500) -> None:
        """将 Task 列表写回 segment 文件。

        Args:
            folder: Tasker 文件夹名
            all_tasks: 完整的 Task 列表（内存中数据）
            loaded: loaded_segments —— 本次会话读过的 segment 文件名集合
            dirty: dirty_segments —— 被修改过的 segment 文件名集合
            max_per_segment: 每段最大记录数
        """
        self.segment.save(folder, all_tasks, loaded, dirty, max_per_segment)

    def list_segment_files(self, folder: str) -> list[str]:
        """列出指定 Tasker 文件夹下的所有 segment 文件名（排序后）。"""
        return self.segment.list_files(folder)

    def count_tasks(self, folder: str) -> int:
        """统计 Tasker 下的总 Task 数。"""
        return self.segment.count_tasks(folder)

    # --- 委托给 AutoSaveManager ---

    def schedule_save(self, callback, delay_ms: int = 500) -> None:
        """调度一次延迟保存（防抖）。"""
        self.auto_save.schedule(callback, delay_ms)

    def flush_save(self) -> None:
        """立即执行所有待保存的任务。"""
        self.auto_save.flush()

    def cancel_save(self) -> None:
        """取消所有待保存任务。"""
        self.auto_save.cancel()

    # --- 备份操作 ---

    def backup_all(self, backup_dir: str) -> None:
        """遍历所有 Tasker 全量读取后写入备份文件夹。不是直接复制文件。

        Args:
            backup_dir: 备份目标目录
        """
        import shutil
        from util.file_utils import ensure_dir
        ensure_dir(backup_dir)

        taskers = self.load_tasker_list()
        # 备份 taskers.json
        self.tasker_index.save(taskers)
        shutil.copy2(self.taskers_path,
                     os.path.join(backup_dir, 'taskers.json'))

        # 逐个 Tasker 全量读取并写入备份
        for t in taskers:
            folder = t['folder']
            src_dir = os.path.join(self._data_dir, folder)
            dst_dir = os.path.join(backup_dir, folder)
            if os.path.isdir(src_dir):
                shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

    def reload_from_backup(self, backup_dir: str) -> list[dict] | None:
        """读取备份文件夹中的全部数据到临时结构。
        先检查 backup_dir/taskers.json 存在 → 读取全部 → 不替换当前数据。

        Args:
            backup_dir: 备份文件夹路径

        Returns:
            list[dict] | None: 备份中的 Tasker 列表，无效备份返回 None
        """
        backup_taskers_path = os.path.join(backup_dir, 'taskers.json')
        if not os.path.exists(backup_taskers_path):
            return None

        from util.json_utils import JsonUtils
        data = JsonUtils.load_json(backup_taskers_path)
        taskers = data.get('taskers', [])

        # 读取每个 Tasker 的全部 segment
        result = []
        for t in taskers:
            folder = t['folder']
            seg_dir = os.path.join(backup_dir, folder)
            tasks = []
            if os.path.isdir(seg_dir):
                seg_files = sorted([f for f in os.listdir(seg_dir)
                                    if f.startswith('segment_') and f.endswith('.json')])
                for sf in seg_files:
                    seg_data = JsonUtils.load_json(os.path.join(seg_dir, sf))
                    tasks.extend(seg_data.get('tasks', []))
            t_copy = dict(t)
            t_copy['_tasks'] = tasks
            result.append(t_copy)

        return result

    def apply_backup(self, backup_dir: str) -> None:
        """将备份文件夹中的内容替换当前存储目录。

        Args:
            backup_dir: 备份文件夹路径
        """
        import shutil
        # 替换 taskers.json
        shutil.copy2(os.path.join(backup_dir, 'taskers.json'), self.taskers_path)
        # 清空旧 Tasker 文件夹
        taskers = self.load_tasker_list()
        for t in taskers:
            old_dir = os.path.join(self._data_dir, t['folder'])
            if os.path.isdir(old_dir):
                shutil.rmtree(old_dir)
        # 复制备份中的 Tasker 文件夹
        for t in taskers:
            src_dir = os.path.join(backup_dir, t['folder'])
            dst_dir = os.path.join(self._data_dir, t['folder'])
            if os.path.isdir(src_dir):
                shutil.copytree(src_dir, dst_dir)
