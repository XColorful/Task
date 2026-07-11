"""MonthlyCounter -- count tasks grouped by month."""

from .base_analyzer import BaseAnalyzer


class MonthlyCounter(BaseAnalyzer):
    analyzer_name = "monthly_count"

    def analyze(self, params):
        storage = params.get('_storage')
        tasker_id = params.get('tasker_id')
        if not storage or not tasker_id:
            return {"labels": [], "values": []}

        from core.service.default_tasker_service import DefaultTaskerService
        svc = DefaultTaskerService(storage)
        tasker = svc.get_tasker(tasker_id)
        if not tasker:
            return {"labels": [], "values": []}
        all_tasks = storage.segment.load_all(tasker.folder)
        tasker.task_list = [svc._create_task_from_dict(td, tasker.type) for td in all_tasks]

        counts = {}
        for t in tasker.task_list:
            month = t.date[:7] if len(t.date) >= 7 else t.date
            if month:
                counts[month] = counts.get(month, 0) + 1

        items = sorted(counts.items())
        return {
            "labels": [k for k, v in items],
            "values": [v for k, v in items],
        }
