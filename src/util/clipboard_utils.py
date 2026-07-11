"""剪贴板操作——使用 pyperclip 实现跨平台剪贴板读写。"""


def copy_to_clipboard(text: str) -> None:
    """将文本复制到系统剪贴板。

    Args:
        text: 要复制的文本
    """
    try:
        import pyperclip
        pyperclip.copy(text)
    except ImportError:
        import subprocess
        import sys
        if sys.platform == "win32":
            subprocess.run(["clip"], input=text, text=True, shell=True)
        else:
            print(f"[clipboard] {text}")


def get_clipboard_text() -> str:
    """获取系统剪贴板中的文本。

    Returns:
        str: 剪贴板内容，获取失败返回空字符串
    """
    try:
        import pyperclip
        return pyperclip.paste()
    except ImportError:
        return ""
