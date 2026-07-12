"""PklMigrator -- migrate old project pkl data to new JSON format."""

import os
import pickle
from collections import OrderedDict


class PklMigrator:
    """Read old Tasker_list.pkl and write to new taskers.json + segment files."""

    def __init__(self, pkl_path, data_dir):
        self._pkl_path = pkl_path
        self._data_dir = data_dir

    def migrate(self):
        """Execute migration. Returns (tasker_count, task_count)."""
        if not os.path.exists(self._pkl_path):
            raise FileNotFoundError(f"pkl file not found: {self._pkl_path}")

        with open(self._pkl_path, 'rb') as f:
            old_taskers = pickle.load(f)

        tasker_count = 0
        task_count = 0

        tasker_list = []
        for old in old_taskers:
            tasker_id = getattr(old, 'tasker_id', None)
            if not tasker_id:
                import uuid
                tasker_id = uuid.uuid4().hex[:12]

            label = getattr(old, 'tasker_label', getattr(old, 'label', 'unnamed'))
            ttype = getattr(old, 'type', 'default')
            desc = getattr(old, 'description', '')
            folder = f"{label}_{tasker_id}"

            tasks = self._convert_tasks(old, ttype)
            task_count += len(tasks)
            tasker_count += 1

            # Write segments
            seg_dir = os.path.join(self._data_dir, folder)
            os.makedirs(seg_dir, exist_ok=True)

            from util.json_utils import JsonUtils
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
                ('type', ttype),
                ('label', label),
                ('description', desc),
                ('folder', folder),
                ('quick_buttons', []),
            ]))

        # Write taskers.json
        from util.json_utils import JsonUtils
        JsonUtils.save_json(
            os.path.join(self._data_dir, 'taskers.json'),
            OrderedDict([('taskers', tasker_list)]),
            atomic=True,
        )

        return tasker_count, task_count

    def _convert_tasks(self, old, ttype):
        tasks = []
        task_list = getattr(old, 'task_list', [])
        for t in task_list:
            d = OrderedDict()
            d['type'] = getattr(t, 'type', ttype)
            d['version'] = getattr(t, 'version', '1.0')
            d['date'] = getattr(t, 'date', '')
            d['attribute'] = getattr(t, 'attribute', 'N/A')
            d['content'] = getattr(t, 'content', '')
            d['comment'] = getattr(t, 'comment', '')
            # Timer extra fields
            if hasattr(t, 'start_time'):
                d['start_time'] = getattr(t, 'start_time', '')
            if hasattr(t, 'end_time'):
                d['end_time'] = getattr(t, 'end_time', '')
            # Account extra fields
            if hasattr(t, 'account_type'):
                d['account_type'] = getattr(t, 'account_type', '')
                d['label_alias'] = getattr(t, 'label', '')
                d['password'] = getattr(t, 'password', '')
                d['supplementary'] = getattr(t, 'dict', {})
            tasks.append(d)
        return tasks
