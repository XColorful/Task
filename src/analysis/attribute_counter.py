"""AttributeCounter -- count tasks grouped by attribute."""

from collections import OrderedDict
from .base_analyzer import BaseAnalyzer


class AttributeCounter(BaseAnalyzer):
    analyzer_name = "attr_count"

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

        counts = OrderedDict()
        for t in tasker.task_list:
            attr = t.attribute or "N/A"
            counts[attr] = counts.get(attr, 0) + 1

        items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        top = params.get('top_n', 0)
        if top and top > 0:
            items = items[:top]

        return {
            "labels": [k for k, v in items],
            "values": [v for k, v in items],
        }
