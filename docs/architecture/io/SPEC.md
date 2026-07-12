# SPEC: io — 数据导入导出

> 对应源码路径: `src/io/`
> 负责将 Task 数据导出为人类可读文本，以及从旧项目格式（.pkl / .txt）迁移导入。

## 1. export_service.py — 导出门面

```python
from util.date_utils import DateUtils
from util.string_utils import StringUtils

class ExportService:
    """导出门面。协调 TxtExporter 完成文本格式导出。"""

    def __init__(self) -> None:
        self._exporter = TxtExporter()

    def export(self, tasker_list: list, sort_mode: str = "date",
               output_path: str | None = None) -> str:
        """导出一个或多个 Tasker 的全部记录为可读文本。

        Args:
            tasker_list: Tasker 列表，每个 Tasker 含 label 和 task_list
            sort_mode: 排序方式
                - "date"      → 按 date 字段排序，同日期内按 Tasker 分组
                - "tasker"    → 按 Tasker 分组，组内按 date 排序
                - "create_date" → 按创建日期分组（需从 segment 文件名推断）
            output_path: 输出文件路径。None 时仅返回字符串不写文件。

        Returns:
            str: 格式化后的完整文本内容
        """
        lines = self._exporter.export(tasker_list, sort_mode)
        text = "\n".join(lines)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
        return text
```

## 2. txt_exporter.py — 文本格式导出

```python
from collections import defaultdict
from util.date_utils import DateUtils

class TxtExporter:
    """将 Task 列表格式化为人类可读的纯文本，兼容旧项目 'txt' 命令输出风格。"""

    def export(self, tasker_list: list, sort_mode: str = "date") -> list[str]:
        """生成格式化的文本行列表。

        输出格式示例（sort_mode="date"）:
            === 2026_07_11 ===
            [TaskerName1]
            content_line_1
            content_line_2
            [TaskerName2]
            content_line_3
            === 2026_07_10 ===
            ...

        Args:
            tasker_list: Tasker 列表（每个含 label、task_list）
            sort_mode: 排序模式（"date" / "tasker" / "create_date"）

        Returns:
            list[str]: 格式化后的行列表，调用方用 "\n".join() 拼接
        """
        if sort_mode == "date":
            return self._export_by_date(tasker_list)
        elif sort_mode == "tasker":
            return self._export_by_tasker(tasker_list)
        elif sort_mode == "create_date":
            return self._export_by_create_date(tasker_list)
        else:
            raise ValueError(f"Unknown sort_mode: {sort_mode}")

    def _export_by_date(self, tasker_list: list) -> list[str]:
        """按 date 字段分组，同日期内按 Tasker 分组。

        算法:
        1. 遍历所有 Tasker 的所有 Task，按 date 分组到 {date: {tasker_label: [task, ...]}}
        2. 按 date 排序（降序: 最新日期在前）
        3. 每个日期先输出 "=== YYYY_MM_DD ===" 分隔行
        4. 日期内按 Tasker label 排序，每个 Tasker 输出 "[label]" 标题行
        5. 每个 Task 输出其 __str__() 表示
        """
        ...

    def _export_by_tasker(self, tasker_list: list) -> list[str]:
        """按 Tasker 分组，组内按 date 排序。

        算法:
        1. 遍历每个 Tasker，按 date 排序其 task_list
        2. 输出 "[TaskerLabel]" 标题行
        3. 输出该 Tasker 所有 Task 的 __str__()
        4. Tasker 间空行分隔
        """
        ...

    def _export_by_create_date(self, tasker_list: list) -> list[str]:
        """按创建日期分组（从 segment 文件名映射，或 fallback 到 date 字段）。

        segment 文件名格式: segment_0001.json，创建日期从文件系统的修改时间推断。
        Fallback: 使用 Task 的 date 字段。
        """
        ...

    def _format_task_line(self, task) -> str:
        """格式化单条 Task 为一行文本。

        对 DefaultTask: "date | attribute | content"
        对 TimerTask:  "start_time | end_time | attribute | content"
        其他类型调用 task.__str__()
        """
        return str(task)
```

## 3. import_service.py — 导入门面

```python
from io.pkl_migrator import PklMigrator
from io.txt_importer import TxtImporter

class ImportService:
    """导入门面。协调 PklMigrator 和 TxtImporter 完成数据导入。"""

    def __init__(self) -> None:
        self._pkl_migrator = PklMigrator()
        self._txt_importer = TxtImporter()

    def migrate_from_pkl(self, pkl_path: str, output_dir: str) -> "MigrationReport":
        """从旧项目 .pkl 文件迁移到新 JSON 格式。

        Args:
            pkl_path: 旧项目 .pkl 文件路径
            output_dir: 输出目录（写入 segment JSON 和 taskers.json）

        Returns:
            MigrationReport: 含 success/skip/error 计数和详细信息
        """
        return self._pkl_migrator.migrate(pkl_path, output_dir)

    def import_from_txt(self, txt_path: str, tasker_id: str) -> list[dict]:
        """从旧备份 .txt 文件解析记录并返回 Task 字典列表。

        Args:
            txt_path: 旧备份 .txt 文件路径
            tasker_id: 目标 Tasker 的 id

        Returns:
            list[dict]: 解析出的 Task 字段字典列表，由调用方通过 TaskService 创建
        """
        return self._txt_importer.parse(txt_path)
```

## 4. pkl_migrator.py — 旧项目 .pkl 迁移

```python
import pickle
import os

class MigrationReport:
    """迁移结果报告。"""

    def __init__(self) -> None:
        self.success_count: int = 0
        self.skip_count: int = 0
        self.error_count: int = 0
        self.errors: list[str] = []        # 错误详情（文件路径 + 原因）
        self.warnings: list[str] = []      # 跳过原因
        self.migrated_taskers: list[str] = []  # 成功迁移的 Tasker label 列表

    def __str__(self) -> str:
        return (
            f"迁移完成: {self.success_count} 成功, "
            f"{self.skip_count} 跳过, {self.error_count} 错误"
        )


class PklMigrator:
    """读取旧项目 .pkl 文件，转换为新 JSON 格式。

    旧项目 .pkl 结构（预期）:
        {
            "label": str,
            "description": str,
            "data": [
                {
                    "date": "2026_07_11",
                    "attribute": "编程",
                    "content": "写代码",
                    "comment": ""
                },
                ...
            ]
        }
    """

    def migrate(self, pkl_path: str, output_dir: str) -> MigrationReport:
        """迁移单个 .pkl 文件到新格式。

        流程:
        1. 读取 .pkl 文件（pickle.load）
        2. 校验顶层结构（label、description、data）
        3. 遍历 data 列表:
           a. 校验每条记录的字段（date、attribute、content、comment）
           b. 对缺失字段填入默认值，对格式不合法的字段记录 skip
           c. 将有效记录转为 DefaultTask 字典
        4. 在 output_dir 下创建 Tasker 文件夹（label + uuid8）
        5. 将 Task 列表按 max_segment_size 拆分写入 segment_0001.json 等
        6. 更新 taskers.json 索引

        Args:
            pkl_path: 旧项目 .pkl 文件路径
            output_dir: 输出根目录（如 data/）

        Returns:
            MigrationReport: 迁移结果报告
        """
        report = MigrationReport()
        try:
            with open(pkl_path, "rb") as f:
                old_data = pickle.load(f)
        except (pickle.UnpicklingError, EOFError, FileNotFoundError) as e:
            report.error_count += 1
            report.errors.append(f"无法读取 {pkl_path}: {e}")
            return report

        # 校验顶层结构
        if not isinstance(old_data, dict):
            report.error_count += 1
            report.errors.append(f"{pkl_path}: 根结构不是 dict")
            return report

        label = old_data.get("label", "未命名")
        if not label:
            report.warnings.append("label 为空，使用默认名称")
            label = "未命名"

        data_list = old_data.get("data", [])
        if not isinstance(data_list, list):
            report.error_count += 1
            report.errors.append(f"{pkl_path}: data 字段不是列表")
            return report

        # 逐条转换
        tasks = []
        for idx, item in enumerate(data_list):
            if not isinstance(item, dict):
                report.skip_count += 1
                report.warnings.append(f"记录 #{idx} 不是 dict，跳过")
                continue

            task_dict = self._convert_record(item, idx, report)
            if task_dict:
                tasks.append(task_dict)
                report.success_count += 1

        # 写入新格式
        if tasks:
            self._write_tasker(output_dir, label, tasks)
            report.migrated_taskers.append(label)

        return report

    def _convert_record(self, item: dict, idx: int,
                        report: MigrationReport) -> dict | None:
        """转换单条记录。不可恢复的错误返回 None，可恢复的填入默认值。

        校验规则:
        - date: 必须满足 YYYY_MM_DD 格式，否则尝试推断
        - attribute: 可为空，默认 "N/A"
        - content: 可为空字符串
        - comment: 可为空字符串
        """
        from collections import OrderedDict
        date = item.get("date", "")
        # 校验 date 格式
        if date and not self._is_valid_date(date):
            report.warnings.append(f"记录 #{idx}: date '{date}' 格式不合法，使用空字符串")
            date = ""

        return OrderedDict([
            ("type", "default"),
            ("version", "1.0"),
            ("date", date),
            ("attribute", item.get("attribute", "N/A")),
            ("content", item.get("content", "")),
            ("comment", item.get("comment", "")),
        ])

    def _is_valid_date(self, date_str: str) -> bool:
        """校验是否为 YYYY_MM_DD 格式。"""
        from util.date_utils import DateUtils
        return DateUtils.is_valid_date(date_str)

    def _write_tasker(self, output_dir: str, label: str,
                      tasks: list[dict]) -> None:
        """在 output_dir 下创建 Tasker 文件夹并写入 segment JSON。"""
        import uuid
        folder_name = f"{label}_{uuid.uuid4().hex[:8]}"
        tasker_dir = os.path.join(output_dir, folder_name)
        os.makedirs(tasker_dir, exist_ok=True)

        from util.file_utils import FileUtils
        from util.json_utils import JsonUtils

        # 将 tasks 按 max_segment_size 拆分
        max_segment_size = 500
        for seg_idx in range(0, len(tasks), max_segment_size):
            seg_name = f"segment_{seg_idx // max_segment_size + 1:04d}.json"
            seg_tasks = tasks[seg_idx:seg_idx + max_segment_size]
            seg_path = os.path.join(tasker_dir, seg_name)
            JsonUtils.save_json(seg_path, {"tasks": seg_tasks}, atomic=True)
```

## 5. txt_importer.py — 旧备份 .txt 解析

```python
import re

class TxtImporter:
    """解析旧项目 `txt` 命令导出的 .txt 备份文件。

    旧备份格式示例:
        === 2026_07_11 ===
        [TaskerName]
        date|attribute|content
        date|attribute|content|comment
    """

    def parse(self, txt_path: str) -> list[dict]:
        """解析 .txt 备份文件，返回 Task 字段字典列表。

        解析规则:
        1. "=== YYYY_MM_DD ===" 行 → 设置当前日期上下文
        2. "[TaskerName]" 行 → 设置当前 Tasker 上下文（记录但不由本方法使用）
        3. 数据行 "date|attr|content" 或 "date|attr|content|comment"
           - 若数据行中的 date 字段缺失或无效，使用当前日期上下文补全
        4. 空行 → 忽略

        Args:
            txt_path: .txt 文件路径

        Returns:
            list[dict]: Task 字段字典（type, version, date, attribute, content, comment）

        Raises:
            FileNotFoundError: 文件不存在
        """
        tasks = []
        current_date = ""
        current_pattern = re.compile(r"^=== (.+) ===$")

        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # 匹配日期分隔行
                m = current_pattern.match(line)
                if m:
                    current_date = m.group(1)
                    continue

                # 跳过 Tasker 标题行
                if line.startswith("[") and line.endswith("]"):
                    continue

                # 解析数据行
                task_dict = self._parse_data_line(line, current_date)
                if task_dict:
                    tasks.append(task_dict)

        return tasks

    def _parse_data_line(self, line: str, fallback_date: str) -> dict | None:
        """解析单行数据。

        支持格式:
        - date | attribute | content
        - date | attribute | content | comment

        date 字段为空或明显无效时使用 fallback_date。
        """
        from collections import OrderedDict
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            return None  # 不是合法数据行

        date = parts[0] if parts[0] else fallback_date
        attribute = parts[1] if len(parts) > 1 else "N/A"
        content = parts[2] if len(parts) > 2 else ""
        comment = parts[3] if len(parts) > 3 else ""

        return OrderedDict([
            ("type", "default"),
            ("version", "1.0"),
            ("date", date),
            ("attribute", attribute),
            ("content", content),
            ("comment", comment),
        ])
```

## 6. 依赖关系

```
io/
├── export_service.py      # 依赖: txt_exporter.py, util/date_utils.py, util/string_utils.py
├── txt_exporter.py         # 依赖: util/date_utils.py (无其他内部依赖)
├── import_service.py       # 依赖: pkl_migrator.py, txt_importer.py
├── pkl_migrator.py         # 依赖: util/date_utils.py, util/json_utils.py, util/file_utils.py
├── txt_importer.py         # 依赖: util/date_utils.py (无其他内部依赖)
└── __init__.py
```
