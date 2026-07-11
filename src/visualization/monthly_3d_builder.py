"""Monthly3DBuilder -- organize Timer Tasks into ECharts GL bar3D format.

Layout: 7 columns per row (Mon-Sun), new month forces line break.
x = column (0-6), z = row index, y = duration in hours, color = attribute group.
"""


class Monthly3DBuilder:
    """Builds 3D bar chart data from Timer Tasks."""

    COLOR_PALETTE = [
        "#5470c6", "#91cc75", "#fac858", "#ee6666",
        "#73c0de", "#3ba272", "#fc8452", "#9a60b4",
        "#ea7ccc", "#48b8d0",
    ]

    @staticmethod
    def build(tasks, year=None, month=None):
        """Build 3D data for the given tasks, optionally filtered by year/month.

        Args:
            tasks: list of TimerTask instances
            year: optional int year filter
            month: optional int month filter

        Returns:
            dict: {data: [[x, z, y, color_idx], ...], labels: [str], months: [str], color_map: {attr: hex}}
        """
        # Filter
        filtered = []
        for t in tasks:
            if getattr(t, 'type', '') != 'timer':
                continue
            dur = getattr(t, 'duration_minutes', None)
            if dur is None:
                continue
            date = getattr(t, 'date', '')
            if year and (not date.startswith(str(year))):
                continue
            if month and (not date[5:7] == f"{month:02d}"):
                continue
            filtered.append(t)

        # Sort by date (and start_time)
        filtered.sort(key=lambda t: (t.date, getattr(t, 'start_time', '')))

        # Group by month, then lay out in 7-column grid
        attr_set = set()
        month_groups = {}
        for t in filtered:
            m = t.date[:7] if len(t.date) >= 7 else "unknown"
            if m not in month_groups:
                month_groups[m] = []
            month_groups[m].append(t)
            attr_set.add(t.attribute or "N/A")

        # Build color map
        attrs = sorted(attr_set)
        color_map = {}
        for i, a in enumerate(attrs):
            color_map[a] = Monthly3DBuilder.COLOR_PALETTE[i % len(Monthly3DBuilder.COLOR_PALETTE)]

        # Layout: 7 columns per row, new month forces break
        data = []
        months_labels = []
        z = 0
        labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        for m_name in sorted(month_groups.keys()):
            tasks_in_month = month_groups[m_name]
            for col_idx, t in enumerate(tasks_in_month):
                x = col_idx % 7
                if col_idx > 0 and x == 0:
                    # New row needed (not the very first task and wrap to column 0)
                    z += 1
                attr = t.attribute or "N/A"
                dur_hours = round(t.duration_minutes / 60.0, 1)
                color_idx = attrs.index(attr)
                data.append([x, z, dur_hours, color_idx])
                months_labels.append(m_name)
            # Force break at end of month
            z += 1

        return {
            "data": data,
            "labels": labels,
            "months": months_labels,
            "color_map": color_map,
            "attr_list": attrs,
        }
