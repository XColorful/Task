"""TxtImporter -- parse old project backup txt files (with |||| separators) into new JSON format."""

import os
from collections import OrderedDict
from util.json_utils import JsonUtils
from util.file_utils import ensure_dir


class TxtImporter:
    """Read old backup_*.txt and import into new JSON format."""

    def __init__(self, txt_path, data_dir):
        self._txt_path = txt_path
        self._data_dir = data_dir

    def import_data(self):
        """Parse the txt file and write to taskers.json + segment files.
        Returns (tasker_count, task_count).
        """
        if not os.path.exists(self._txt_path):
            raise FileNotFoundError(f"File not found: {self._txt_path}")

        with open(self._txt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        tasker_list = []
        current_tasks = []
        current_tasker = None
        task_count = 0

        for line in lines:
            line = line.rstrip('\n')
            if not line or line.startswith('/end'):
                # End of data section
                if current_tasker:
                    self._save_tasker(current_tasker, current_tasks, tasker_list)
                    task_count += len(current_tasks)
                current_tasker = None
                current_tasks = []
                if line.startswith('/end'):
                    break
                continue

            if line.startswith('\t'):
                # Task line
                task_line = line[1:]  # strip \t
                if current_tasker is not None:
                    parts = task_line.split('||||')
                    if len(parts) >= 7:
                        task_dict = OrderedDict([
                            ("type", parts[0].lower() if parts[0] == "Default" else parts[0]),
                            ("version", parts[1]),
                            ("create_date", parts[2]),
                            ("date", parts[3]),
                            ("attribute", parts[4]),
                            ("content", parts[5]),
                            ("comment", parts[6]),
                        ])
                        current_tasks.append(task_dict)
            else:
                # Tasker line — save previous one first
                if current_tasker:
                    self._save_tasker(current_tasker, current_tasks, tasker_list)
                    task_count += len(current_tasks)

                parts = line.split('||||')
                if len(parts) >= 7:
                    current_tasker = {
                        "type": parts[0].lower(),
                        "version": parts[1],
                        "label": parts[2],
                        "create_date": parts[3],
                        "description": parts[6],
                    }
                    current_tasks = []

        # Save last tasker if any
        if current_tasker:
            self._save_tasker(current_tasker, current_tasks, tasker_list)
            task_count += len(current_tasks)

        # Write taskers.json
        JsonUtils.save_json(
            os.path.join(self._data_dir, 'taskers.json'),
            OrderedDict([('taskers', tasker_list)]),
            atomic=True,
        )

        return len(tasker_list), task_count

    def _save_tasker(self, info, tasks, tasker_list):
        import uuid
        tasker_id = uuid.uuid4().hex[:12]
        label = info['label']
        folder = f"{label}_{tasker_id}"

        seg_dir = os.path.join(self._data_dir, folder)
        ensure_dir(seg_dir)

        max_seg = 500
        seg_idx = 0
        for i in range(0, len(tasks), max_seg):
            seg_idx += 1
            chunk = tasks[i:i + max_seg]
            JsonUtils.save_json(
                os.path.join(seg_dir, f'segment_{seg_idx:04d}.json'),
                OrderedDict([('tasks', chunk)]),
                atomic=True,
            )

        tasker_list.append(OrderedDict([
            ('id', tasker_id),
            ('type', info['type']),
            ('label', label),
            ('description', info.get('description', '')),
            ('folder', folder),
            ('quick_buttons', []),
        ]))
