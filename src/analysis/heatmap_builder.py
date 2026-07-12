"""HeatmapBuilder -- build date x attribute matrix."""

from .base_analyzer import BaseAnalyzer


class HeatmapBuilder(BaseAnalyzer):
    analyzer_name = "heatmap"

    def analyze(self, params):
        storage = params.get('_storage')
        tasker_id = params.get('tasker_id')
        if not storage or not tasker_id:
            return {"x_labels": [], "y_labels": [], "data": []}

        from core.service.default_tasker_service import DefaultTaskerService
        svc = DefaultTaskerService(storage)
        tasker = svc.get_tasker(tasker_id)
        if not tasker:
            return {"x_labels": [], "y_labels": [], "data": []}
        all_tasks = storage.segment.load_all(tasker.folder)
        tasker.task_list = [svc._create_task_from_dict(td, tasker.type) for td in all_tasks]

        pairs = {}
        all_attrs = set()
        for t in tasker.task_list:
            date_key = t.date[:7] if len(t.date) >= 7 else t.date
            attr = t.attribute or "N/A"
            all_attrs.add(attr)
            key = (date_key, attr)
            pairs[key] = pairs.get(key, 0) + 1

        dates = sorted(set(k[0] for k in pairs.keys()))
        attrs = sorted(all_attrs)

        data = []
        for di, date in enumerate(dates):
            for ai, attr in enumerate(attrs):
                v = pairs.get((date, attr), 0)
                if v > 0:
                    data.append([di, ai, v])

        return {
            "x_labels": dates,
            "y_labels": attrs,
            "data": data,
        }
