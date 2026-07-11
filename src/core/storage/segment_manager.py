"""分段读写管理——单个 Tasker 文件夹内的 segment JSON 读写。

两段懒加载 + 脏数据追踪 + 原子写入 + 扩容/缩容。
"""

import os
import glob
from collections import OrderedDict
from util.json_utils import JsonUtils
from util.file_utils import ensure_dir


class SegmentManager:
    """管理单个 Tasker 文件夹内的 segment JSON 文件读写。"""

    def __init__(self, data_dir: str):
        self._data_dir = data_dir

    def _segment_dir(self, folder: str) -> str:
        return os.path.join(self._data_dir, folder)

    def list_files(self, folder: str) -> list[str]:
        """列出并排序 segment 文件。目录不存在返回空列表。"""
        seg_dir = self._segment_dir(folder)
        if not os.path.isdir(seg_dir):
            return []
        files = glob.glob(os.path.join(seg_dir, 'segment_*.json'))
        files.sort()
        return [os.path.basename(f) for f in files]

    def load_last(self, folder: str, count: int = 2) -> list[dict]:
        """加载最后 count 个 segment 并合并为 Task 列表。

        Returns:
            list[dict]: 每条 Task 为 OrderedDict，保持 JSON 顺序
        """
        files = self.list_files(folder)
        target_files = files[-count:] if len(files) >= count else files
        tasks = []
        for fname in target_files:
            tasks.extend(self._read_segment(folder, fname))
        return tasks

    def load_all(self, folder: str) -> list[dict]:
        """加载全部 segment 并拼接。"""
        files = self.list_files(folder)
        tasks = []
        for fname in files:
            tasks.extend(self._read_segment(folder, fname))
        return tasks

    def _read_segment(self, folder: str, filename: str) -> list[dict]:
        path = os.path.join(self._segment_dir(folder), filename)
        try:
            data = JsonUtils.load_json(path)
            return data.get('tasks', [])
        except FileNotFoundError:
            return []

    def save(self, folder: str, all_tasks: list[dict],
             loaded: set[str], dirty: set[str],
             max_per_segment: int = 500) -> None:
        """写入策略：

        1. 将 all_tasks 按 max_per_segment 分组为片段
        2. 只对 dirty 段或新增/删除的段执行写入
        3. 原子写入（tmp → rename）
        4. 清理多余文件（缩容产生的空段文件）

        Args:
            folder: Tasker 文件夹名
            all_tasks: 完整 Task 列表（内存数据）
            loaded: loaded_segments 集合
            dirty: dirty_segments 集合
            max_per_segment: 每段最大记录数
        """
        seg_dir = self._segment_dir(folder)
        ensure_dir(seg_dir)

        # 分组
        segments = []
        for i in range(0, len(all_tasks), max_per_segment):
            segments.append(all_tasks[i:i + max_per_segment])

        existing = self.list_files(folder)
        new_filenames = [f'segment_{j+1:04d}.json' for j in range(len(segments))]

        # 写入
        for idx, (fname, tasks) in enumerate(zip(new_filenames, segments)):
            need_write = False
            if fname in dirty:
                need_write = True
            elif fname not in existing:
                need_write = True  # 新增 segment
            # loaded 但未 dirty 的段不写（非脏不写）
            if fname in loaded and fname not in dirty:
                need_write = False

            if need_write:
                self._write_segment(folder, fname, tasks)

        # 删除多余文件（缩容后多余的旧段）
        for old_fname in existing:
            if old_fname not in new_filenames:
                old_path = os.path.join(seg_dir, old_fname)
                try:
                    os.remove(old_path)
                except OSError:
                    pass

    def _write_segment(self, folder: str, filename: str, tasks: list[dict]) -> None:
        data = OrderedDict()
        data['tasks'] = tasks
        path = os.path.join(self._segment_dir(folder), filename)
        JsonUtils.save_json(path, data, atomic=True)

    def count_tasks(self, folder: str) -> int:
        """统计 Tasker 下的总 Task 数（遍历所有 segment）。"""
        files = self.list_files(folder)
        total = 0
        for fname in files:
            tasks = self._read_segment(folder, fname)
            total += len(tasks)
        return total
