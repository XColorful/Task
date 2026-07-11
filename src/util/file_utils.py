"""文件操作工具——原子写入、安全路径拼接、目录创建。"""

import os


def atomic_write(path: str, content: str) -> None:
    """原子写入文件：先写到 path.tmp，再 rename 到目标路径。

    Args:
        path: 目标文件路径
        content: 文件内容字符串
    """
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp_path, path)


def safe_join(base: str, *parts: str) -> str:
    """安全地拼接路径，拒绝路径遍历（如 '..' 跳出 base）。

    Args:
        base: 基础目录路径
        *parts: 要拼接的子路径组件

    Returns:
        str: 拼接后的绝对路径

    Raises:
        ValueError: 拼接结果不在 base 之下（存在路径遍历攻击）
    """
    result = os.path.abspath(os.path.join(base, *parts))
    base_abs = os.path.abspath(base)
    if not result.startswith(base_abs + os.sep) and result != base_abs:
        raise ValueError(f"Path traversal detected: {result} not under {base_abs}")
    return result


def ensure_dir(path: str) -> None:
    """确保目录存在，不存在则递归创建。

    Args:
        path: 目录路径
    """
    os.makedirs(path, exist_ok=True)
