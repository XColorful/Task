"""日期字符串工具——格式化、解析、比较"""

from datetime import datetime, timedelta


def today_str() -> str:
    """返回今天的日期字符串 'YYYY_MM_DD'"""
    return datetime.now().strftime("%Y_%m_%d")


def now_str() -> str:
    """返回当前的日期时间字符串 'YYYY_MM_DD-HH:MM'"""
    return datetime.now().strftime("%Y_%m_%d-%H:%M")


def parse_date(s: str) -> datetime | None:
    """解析多种日期格式为 datetime 对象。
    支持: 'YYYY_MM_DD', 'YYYY_MM_DD-HH:MM', 'YYYY_MM_DD - HH-MM-SS'
    解析失败返回 None。
    """
    formats = [
        "%Y_%m_%d",
        "%Y_%m_%d-%H:%M",
        "%Y_%m_%d - %H-%M-%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def is_valid_date(s: str) -> bool:
    """判断字符串是否为有效日期 'YYYY_MM_DD'"""
    return parse_date(s) is not None


def format_duration(minutes: int) -> str:
    """格式化分钟数为可读字符串。
    >>> format_duration(3255)
    ' 2d  6h 15m'
    """
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


def convert_to_int(s: str):
    """尝试将字符串转换为 int，失败返回 None。"""
    try:
        return int(s)
    except (ValueError, TypeError):
        return None
