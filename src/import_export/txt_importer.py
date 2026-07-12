"""TxtImporter -- parse old backup txt files with |||| separators."""

import os
from collections import OrderedDict
from util.json_utils import JsonUtils
from util.file_utils import ensure_dir


class TxtImporter:

    def __init__(self, txt_path, data_dir):
        self._txt_path = txt_path
        self._data_dir = data_dir

    def import_data(self):
        if not os.path.exists(self._txt_path):
            raise FileNotFoundError("File not found: " + self._txt_path)
        with open(self._txt_path, encoding="utf-8") as f:
            lines = f.readlines()
        tasker_list = []
        current_tasks = []
        current_tasker = None
        task_count = 0
        for line in lines:
            line = line.rstrip('\n')
            if not line or line.startswith("/end"):
                if current_tasker:
                    self._save_tasker(current_tasker, current_tasks, tasker_list)
                    task_count += len(current_tasks)
                current_tasker = None
                current_tasks = []
                if line.startswith("/end"):
                    break
                continue
            if line.startswith("\t"):
                task_line = line[1:]
                if current_tasker is not None:
                    task_dict = self._parse_task_line(task_line)
                    if task_dict:
                        current_tasks.append(task_dict)
            else:
                if current_tasker:
                    self._save_tasker(current_tasker, current_tasks, tasker_list)
                    task_count += len(current_tasks)
                parts = line.split("||||")
                if len(parts) >= 7:
                    old_type = parts[0].lower()
                    version = parts[1]
                    if old_type == "extra" and version in ("timer", "account", "label"):
                        mapped_type = version
                    elif old_type == "default":
                        mapped_type = "default"
                    else:
                        mapped_type = old_type
                    current_tasker = {
                        "type": mapped_type,
                        "version": version,
                        "label": parts[2],
                        "create_date": parts[3],
                        "description": parts[6],
                    }
                    current_tasks = []
        if current_tasker:
            self._save_tasker(current_tasker, current_tasks, tasker_list)
            task_count += len(current_tasks)
        JsonUtils.save_json(
            os.path.join(self._data_dir, "taskers.json"),
            OrderedDict([("taskers", tasker_list)]),
            atomic=True,
        )
        return len(tasker_list), task_count

    def _parse_task_line(self, line):
        parts = line.split("||||")
        if len(parts) < 7:
            return None

        ttype = parts[0].lower()
        version = parts[1]

        if (ttype == "extra" or ttype == "timer") and version == "timer" and len(parts) >= 8:
            return OrderedDict([
                ("type", "timer"),
                ("version", "timer"),
                ("create_date", parts[2]),
                ("date", ""),
                ("start_time", parts[3]),
                ("end_time", parts[4]),
                ("attribute", parts[5]),
                ("content", parts[6]),
                ("comment", parts[7]),
            ])
        else:
            return OrderedDict([
                ("type", "default"),
                ("version", parts[1]),
                ("create_date", parts[2]),
                ("date", parts[3]),
                ("attribute", parts[4]),
                ("content", parts[5]),
                ("comment", parts[6]),
            ])

    def _save_tasker(self, info, tasks, tasker_list):
        import uuid
        tasker_id = uuid.uuid4().hex[:12]
        label = info["label"]
        folder = label + "_" + tasker_id
        seg_dir = os.path.join(self._data_dir, folder)
        ensure_dir(seg_dir)
        max_seg = 500
        seg_idx = 0
        for i in range(0, len(tasks), max_seg):
            seg_idx += 1
            chunk = tasks[i:i + max_seg]
            JsonUtils.save_json(
                os.path.join(seg_dir, "segment_" + str(seg_idx).zfill(4) + ".json"),
                OrderedDict([("tasks", chunk)]),
                atomic=True,
            )
        tasker_list.append(OrderedDict([
            ("id", tasker_id),
            ("type", info["type"]),
            ("label", label),
            ("description", info.get("description", "")),
            ("folder", folder),
            ("quick_buttons", []),
        ]))
