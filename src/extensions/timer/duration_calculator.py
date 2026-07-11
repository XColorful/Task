"""时长计算工具——格式化时长和跨日天数统计。"""

from datetime import datetime


class DurationCalculator:
    """纯计算工具。"""

    @staticmethod
    def format_duration(minutes: int) -> str:
        if minutes < 0:
            return "Error"
        if minutes == 0:
            return " 0m"
        days, remainder = divmod(minutes, 1440)
        hours, minutes = divmod(remainder, 60)
        parts = []
        if days > 0:
            parts.append(f"{days:>2}d")
        if hours > 0:
            parts.append(f"{hours:>2}h")
        if minutes > 0:
            parts.append(f"{minutes:>2}m")
        return " ".join(parts)

    @staticmethod
    def get_days_list(start_time: str, end_time: str | None = None) -> list[str]:
        fmt = "%Y_%m_%d-%H:%M"
        t1 = datetime.strptime(start_time, fmt)
        t2 = datetime.strptime(end_time, fmt) if end_time else datetime.now()
        days = []
        from datetime import timedelta
        cur = t1
        while cur.date() <= t2.date():
            days.append(cur.strftime("%Y_%m_%d"))
            cur += timedelta(days=1)
        return days
