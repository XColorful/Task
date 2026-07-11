"""字符串解析工具——content 字段约定格式解析。"""


def parse_semicolon_content(content: str) -> list[str]:
    """按 '; ' 分隔 content 字段，返回各项列表。

    Args:
        content: 原始内容字符串

    Returns:
        list[str]: 分隔后的各项（去除空白项）
    """
    if not content:
        return []
    parts = content.split("; ")
    return [p.strip() for p in parts if p.strip()]


def extract_key_value(content: str, key: str) -> str | None:
    """从 content 中提取指定 key 对应的 value。

    支持格式: "key:value", "key: value", "key：value"（中文冒号）

    Args:
        content: 原始内容字符串
        key: 要查找的键名

    Returns:
        str | None: 找到则返回 value 字符串，未找到返回 None
    """
    import re
    pattern = re.compile(
        re.escape(key) + r"\s*[：:]\s*([^;]+)"
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else None


def extract_jpg_references(content: str) -> list[str]:
    """从 content 中提取所有 'jpg:xxx' 或 'png:xxx' 引用。

    Args:
        content: 原始内容字符串

    Returns:
        list[str]: 文件名列表（不含 'jpg:' 和 'png:' 前缀）
    """
    import re
    matches = re.findall(r'(?:jpg|png):([^;]+)', content)
    return [m.strip() for m in matches]
