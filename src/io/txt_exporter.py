"""TxtExporter -- export tasks as human-readable text (old project style)."""


class TxtExporter:
    """Format task lists as readable plain text."""

    def export(self, tasker_list, sort_mode="date"):
        """Export tasks from taskers in specified sort mode.

        Args:
            tasker_list: list of tasker objects with .label and .task_list
            sort_mode: 'date', 'tasker', or 'create_date'

        Returns:
            list of lines
        """
        lines = []
        lines.append(f"Task Export — sort: {sort_mode}")
        lines.append("=" * 50)

        if sort_mode == "tasker":
            self._export_by_tasker(tasker_list, lines)
        elif sort_mode == "date":
            self._export_by_date(tasker_list, lines)
        else:
            self._export_by_tasker(tasker_list, lines)

        return lines

    def _export_by_tasker(self, tasker_list, lines):
        for tasker in tasker_list:
            lines.append(f"\nTasker: {tasker.label}")
            lines.append(f"  Description: {tasker.description}")
            lines.append(f"  Tasks: {len(tasker.task_list)}")
            lines.append("  " + "-" * 40)
            for i, task in enumerate(tasker.task_list):
                comment = f" | {task.comment}" if task.comment else ""
                lines.append(f"  [{i}] {task.date}|<{task.attribute}>|{task.content}{comment}")

    def _export_by_date(self, tasker_list, lines):
        all_tasks = []
        for tasker in tasker_list:
            for task in tasker.task_list:
                all_tasks.append((task.date, tasker.label, task))

        all_tasks.sort(key=lambda x: x[0])
        current_date = None
        for date, label, task in all_tasks:
            if date != current_date:
                current_date = date
                lines.append(f"\nDate: {date}")
            comment = f" | {task.comment}" if task.comment else ""
            lines.append(f"  [{label}] {task.date}|<{task.attribute}>|{task.content}{comment}")
