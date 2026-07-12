# SPEC: core/storage — 存储层

> 对应源码路径: `src/core/storage/`
> 负责 JSON 文件的分段读写、索引维护、原子写入、自动保存。

## 1. storage_manager.py — 存储门面

```python
from core.storage.tasker_index_manager import TaskerIndexManager
from core.storage.segment_manager import SegmentManager
from core.storage.auto_save_manager import AutoSaveManager

class StorageManager:
    """存储门面（全能易用门面）。对外提供统一的存储操作入口。"""

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

    # --- 委托给 SegmentManager ---
    def load_recent_segments(self, folder: str, count: int = 2) -> list[dict]:
        """加载指定 Tasker 文件夹下最后 count 个 segment 的 Task 列表。
        进入 Tasker 时调用（两段懒加载）。

        Args:
            folder: Tasker 文件夹名（如 "班级_a1b2c3d4"）
            count: 加载的 segment 数量（默认 2）

        Returns:
            list[dict]: 合并后的 Task 字典列表
        """
        return self.segment.load_last(folder, count)

    def load_all_segments(self, folder: str) -> list[dict]:
        """加载指定 Tasker 文件夹下全部 segment 并拼接为完整列表。
        正数索引触发全量加载时调用。

        Returns:
            list[dict]: 所有 Task 字典列表（保持 segment 内顺序和 segment 间顺序）
        """
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

        写入逻辑：
        1. 仅 dirty 中的 segment 需要写回
        2. 扩容：最新段满 max_per_segment → 创建新 segment
        3. 缩容：段内记录全删 → 跳过该文件
        4. 中间段脏：重新计算该段的记录范围并写入
        5. 原子写入分段：先写 .tmp 再 rename
        """
        self.segment.save(folder, all_tasks, loaded, dirty, max_per_segment)

    def list_segment_files(self, folder: str) -> list[str]:
        """列出指定 Tasker 文件夹下的所有 segment 文件名（排序后）。"""
        return self.segment.list_files(folder)

    # --- 委托给 AutoSaveManager ---
    def schedule_save(self, callback, delay_ms: int = 500) -> None:
        """调度一次延迟保存（防抖）。多次调用时重置计时器。"""
        self.auto_save.schedule(callback, delay_ms)

    def flush_save(self) -> None:
        """立即执行所有待保存的任务（如退出前）。"""
        self.auto_save.flush()

    # --- 备份 ---
    def backup_all(self, backup_dir: str) -> None:
        """遍历所有 Tasker 全量读取后写入备份文件夹。不是直接复制文件。"""
        ...

    def reload_from_backup(self, backup_dir: str) -> None:
        """先检查 backup_dir/taskers.json 存在 → 读取全部到临时结构 →
        对比 → 用户确认 → 替换当前存储目录。"""
        ...
```

## 2. tasker_index_manager.py — Tasker 索引管理

```python
import json
import os
from collections import OrderedDict

class TaskerIndexManager:
    """管理 taskers.json 的读写。"""

    def __init__(self, data_dir: str):
        self._path = os.path.join(data_dir, 'taskers.json')

    def load(self) -> list[dict]:
        """读取 taskers.json，返回 Tasker 列表（保持 JSON 数组顺序）。

        Returns:
            list[dict]: 每个 dict 包含 id, type, label, description, folder, quick_buttons

        Raises:
            FileNotFoundError: 文件不存在时返回空列表
        """
        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                data = json.load(f, object_pairs_hook=OrderedDict)
                return data.get('taskers', [])
        except FileNotFoundError:
            return []

    def save(self, taskers: list[dict]) -> None:
        """写入 taskers.json（原子写入）。

        Args:
            taskers: Tasker 列表，顺序即为文件中的数组顺序
        """
        data = OrderedDict()
        data['taskers'] = taskers
        tmp_path = self._path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self._path)  # 原子 rename
```

## 3. segment_manager.py — 分段读写管理

```python
import json
import os
import glob
from collections import OrderedDict

class SegmentManager:
    """管理单个 Tasker 文件夹内的 segment JSON 文件读写。"""

    def __init__(self, data_dir: str):
        self._data_dir = data_dir

    def _segment_dir(self, folder: str) -> str:
        return os.path.join(self._data_dir, folder)

    def list_files(self, folder: str) -> list[str]:
        """列出并排序 segment 文件。seg_dir 不存在时返回空列表。"""
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
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f, object_pairs_hook=OrderedDict)
            return data.get('tasks', [])

    def save(self, folder: str, all_tasks: list[dict],
             loaded: set[str], dirty: set[str],
             max_per_segment: int = 500) -> None:
        """写入策略：

        1. 将 all_tasks 按 max_per_segment 分组为片段
        2. 对比现有 segment 文件列表
        3. 只对 dirty 段或新增/删除的段执行写入
        4. 原子写入（tmp → rename）
        5. 清理多余文件（缩容产生的空段文件）

        Args:
            all_tasks: 完整 Task 列表（内存数据）
            loaded: loaded_segments 集合
            dirty: dirty_segments 集合
            max_per_segment: 每段最大记录数
        """
        seg_dir = self._segment_dir(folder)
        os.makedirs(seg_dir, exist_ok=True)

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
        tmp_path = path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
```

## 4. auto_save_manager.py — 自动保存调度

```python
import threading

class AutoSaveManager:
    """防抖自动保存调度器。"""

    def __init__(self):
        self._timer: threading.Timer | None = None
        self._pending_callbacks: list = []

    def schedule(self, callback, delay_ms: int = 500) -> None:
        """调度一次延迟保存。如果在延迟期间再次调用，重置计时器（防抖）。"""
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
```

## 5. index_builder.py — 索引重建

```python
class IndexBuilder:
    """数据恢复工具——扫描磁盘上的 Tasker 文件夹重建 taskers.json。"""

    @staticmethod
    def rebuild(data_dir: str) -> list[dict]:
        """扫描 data_dir 下的所有文件夹，重建 Tasker 列表。

        每个子文件夹必须有有效的 segment 文件才被识别为 Tasker。
        恢复的 Tasker 信息从最早 segment 的第一条记录推断（可能不完整）。

        Returns:
            list[dict]: 重建的 Tasker 列表
        """
        # 由具体实现补充
        ...
```

## 6. 依赖关系

```
core/storage/
├── storage_manager.py     # 门面 —— 依赖本目录下所有模块 + core/types.py
├── tasker_index_manager.py # 独立 —— 依赖 json, os + collections.OrderedDict
├── segment_manager.py      # 独立 —— 依赖 json, os, glob + collections.OrderedDict
├── auto_save_manager.py    # 独立 —— 依赖 threading
├── index_builder.py        # 独立 —— 依赖 os, glob
└── __init__.py
```
