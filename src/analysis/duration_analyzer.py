"""DurationAnalyzer -- analyze Timer Task durations."""

from .base_analyzer import BaseAnalyzer


class DurationAnalyzer(BaseAnalyzer):
    analyzer_name = "duration"

    def analyze(self, params):
        storage = params.get('_storage')
        tasker_id = params.get('tasker_id')
        group_by = params.get('group_by', 'attribute')

        if not storage or not tasker_id:
            return {"labels": [], "values": []}

        from core.service.default_tasker_service import DefaultTaskerService
        svc = DefaultTaskerService(storage)
        tasker = svc.get_tasker(tasker_id)
        if not tasker:
            return {"labels": [], "values": []}
        all_tasks = storage.segment.load_all(tasker.folder)
        tasker.task_list = [svc._create_task_from_dict(td, tasker.type) for td in all_tasks]

        groups = {}
        for t in tasker.task_list:
            if getattr(t, 'type', '') != 'timer':
                continue
            dur = getattr(t, 'duration_minutes', None)
            if dur is None:
                continue
            if group_by == 'month':
                key = t.date[:7] if len(t.date) >= 7 else t.date
            else:
                key = t.attribute or "N/A"
            groups[key] = groups.get(key, 0) + dur

        items = sorted(groups.items(), key=lambda x: x[1], reverse=True)
        total_hours = [round(v / 60.0, 1) for k, v in items]
        return {
            "labels": [k for k, v in items],
            "values": total_hours,
            "unit": "hours",
        }
