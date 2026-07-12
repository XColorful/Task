# SPEC: ui/component — 通用 UI 组件

> 对应源码路径: `src/ui/component/`
> 可复用的 PySide6 UI 组件——统一风格按钮、轻量级反馈提示、确认对话框。供主窗口和扩展模块共用。

---

## 1. styled_button.py

### 1.1 StyledButton

```python
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QColor, QPalette


class StyledButton(QPushButton):
    """统一风格的按钮——支持图标、配色方案和键盘快捷键标注。

    提供预设的配色方案（主色/成功/危险/中性），统一的圆角+阴影样式，
    以及可选的键盘快捷键标签显示（如 "Ctrl+S"）。

    使用示例:
        btn = StyledButton("保存", color=StyledButton.Color.SUCCESS, shortcut="Ctrl+S")
        btn = StyledButton("删除", color=StyledButton.Color.DANGER, icon_path="icons/trash.svg")
    """

    # ── 预设配色方案 ──

    class Color:
        """配色枚举——每个值包含 (bg, hover_bg, text_color) 三元组。"""
        PRIMARY   = ("#4A90D9", "#3A7BC8", "#FFFFFF")   # 蓝色主色调
        SUCCESS   = ("#27AE60", "#219A52", "#FFFFFF")   # 绿色——新建/保存
        DANGER    = ("#E74C3C", "#C0392B", "#FFFFFF")   # 红色——删除/退出
        NEUTRAL   = ("#7F8C8D", "#6C7A7B", "#FFFFFF")   # 灰色——取消/返回
        GHOST     = ("transparent", "#3A3A3A", "#CCCCCC")  # 透明——次要操作

    # ── 尺寸预设 ──

    class Size:
        SMALL  = ("11px", 4, 10, 24)   # (font_size, radius, h_padding, min_height)
        NORMAL = ("13px", 5, 16, 32)
        LARGE  = ("15px", 6, 24, 40)

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        color: tuple[str, str, str] | None = None,
        size: tuple[str, int, int, int] | None = None,
        icon: QIcon | str | None = None,
        shortcut: str | None = None,
    ) -> None:
        """初始化统一风格按钮。

        Args:
            text: 按钮显示文本
            parent: 父控件
            color: 配色方案 (bg, hover_bg, text_color)。默认 Color.PRIMARY。
                   也可传入自定义 3 元组。
            size: 尺寸预设 (font_size, radius, h_padding, min_height)。默认 Size.NORMAL。
            icon: QIcon 实例或图标文件路径（如 "icons/save.svg"）。为 None 时不显示图标。
            shortcut: 键盘快捷键标注文本（如 "Ctrl+S"）。仅显示在按钮右侧作为提示，
                      不绑定实际快捷键——快捷键绑定由调用方在上级容器中处理。
        """
        super().__init__(text, parent)
        self._color = color or self.Color.PRIMARY
        self._size = size or self.Size.NORMAL
        self._icon = icon
        self._shortcut = shortcut

        self._apply_style()
        self._apply_icon()
        self._apply_shortcut()

        # 设置鼠标光标
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    # ── 公共方法 ──

    def set_color(self, color: tuple[str, str, str]) -> None:
        """动态切换配色方案。

        Args:
            color: (bg, hover_bg, text_color)
        """
        self._color = color
        self._apply_style()

    def set_shortcut_text(self, shortcut: str | None) -> None:
        """更新快捷键标注文本。"""
        self._shortcut = shortcut
        self._apply_shortcut()

    def set_loading(self, loading: bool) -> None:
        """设置按钮的加载状态。

        loading=True 时:
        - 按钮 disabled
        - 文本变为 "处理中…"（保存原文本以便恢复）
        - 样式变灰

        loading=False 时:
        - 恢复原文本
        - 恢复 enabled + 原样式
        """
        if loading:
            self._saved_text = self.text()
            self.setText("处理中…")
            self.setEnabled(False)
            self.setStyleSheet(self._disabled_style())
        else:
            self.setText(getattr(self, '_saved_text', self.text()))
            self.setEnabled(True)
            self._apply_style()

    # ── 内部样式 ──

    def _apply_style(self) -> None:
        """应用 CSS 样式。

        生成如下结构的 stylesheet:
        ```
        QPushButton {
            background-color: {bg};
            color: {text};
            border: none;
            border-radius: {radius}px;
            padding: 4px {h_padding}px;
            font-size: {font_size};
            font-weight: 500;
            min-height: {min_height}px;
        }
        QPushButton:hover {
            background-color: {hover_bg};
        }
        QPushButton:pressed {
            background-color: {pressed_bg};  /* hover_bg 暗化 10% */
        }
        QPushButton:disabled {
            background-color: #555;
            color: #999;
        }
        ```
        """
        font_size, radius, h_pad, min_h = self._size
        bg, hover_bg, text_color = self._color

        # 计算 pressed 色: 在 hover_bg 基础上暗化 (简单实现——减少各通道 10%)
        pressed_bg = self._darken(hover_bg, 0.10)

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border: none;
                border-radius: {radius}px;
                padding: 4px {h_pad}px;
                font-size: {font_size};
                font-weight: 500;
                min-height: {min_h}px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {pressed_bg};
            }}
            QPushButton:disabled {{
                background-color: #555555;
                color: #999999;
            }}
        """)

    def _apply_icon(self) -> None:
        """设置图标。

        - 如果 _icon 是 QIcon 实例 → 直接 setIcon()
        - 如果 _icon 是 str → 从文件路径加载 QIcon → setIcon()
        - 如果 _icon 为 None → 跳过

        图标尺寸: 18x18（自动缩放）。
        """
        if self._icon is None:
            return
        if isinstance(self._icon, str):
            self._icon = QIcon(self._icon)
        self.setIcon(self._icon)
        self.setIconSize(QSize(18, 18))

    def _apply_shortcut(self) -> None:
        """在按钮文本右侧追加快捷键标注。

        格式: "{原文本}  {shortcut}"
        - 快捷键用更浅的颜色和更小的字号显示
        - 由于 QPushButton 不支持富文本内联样式，简单拼接文本

        注: 若需富文本样式（如不同颜色/字号的快捷键标注），可改用 QLabel overlaid 方案。
        这里采用简单拼接以保持实现简洁。
        """
        if self._shortcut:
            base_text = self.text().rstrip()
            # 移除旧的快捷键标注（如果 set_shortcut_text 被多次调用）
            if "  " in base_text:
                base_text = base_text.split("  ")[0]
            self.setText(f"{base_text}  {self._shortcut}")

    def _disabled_style(self) -> str:
        """返回 disabled 状态的样式表。"""
        font_size, radius, h_pad, min_h = self._size
        return f"""
            QPushButton {{
                background-color: #555555;
                color: #999999;
                border: none;
                border-radius: {radius}px;
                padding: 4px {h_pad}px;
                font-size: {font_size};
                min-height: {min_h}px;
            }}
        """

    @staticmethod
    def _darken(hex_color: str, factor: float) -> str:
        """将 hex 颜色暗化指定比例。

        Args:
            hex_color: "#RRGGBB" 格式
            factor: 0.0-1.0，暗化比例

        Returns:
            "#RRGGBB" 格式的暗化颜色
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return hex_color
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02X}{g:02X}{b:02X}"
```

---

## 2. toast_notification.py

### 2.1 ToastNotification

```python
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve, Signal
from PySide6.QtGui import QColor, QPalette


class ToastNotification(QWidget):
    """轻量级操作反馈提示——2 秒自动消失，支持多个 Toast 堆叠显示。

    使用示例:
        ToastNotification.show_message(parent_window, "保存成功", ToastNotification.Level.SUCCESS)
        ToastNotification.show_message(parent_window, "删除失败", ToastNotification.Level.ERROR)

    特性:
    - 自动消失: 默认 2 秒后淡出
    - 堆叠显示: 多个 Toast 同时显示时垂直排列，不互相遮挡
    - 淡入动画: 出现时从透明渐变为不透明（200ms）
    - 非模态: 不阻塞用户操作
    """

    # ── 提示级别 ──

    class Level:
        """提示级别——预设颜色方案 (bg_color, icon_text)。"""
        SUCCESS = ("#27AE60", "✓")   # 绿色背景
        ERROR   = ("#E74C3C", "✗")   # 红色背景
        WARNING = ("#F39C12", "⚠")   # 橙色背景
        INFO    = ("#3498DB", "ℹ")   # 蓝色背景

    # 类变量——管理所有活跃的 Toast 实例（用于堆叠定位）
    _active_toasts: list['ToastNotification'] = []

    # 信号
    dismissed = Signal()

    def __init__(
        self,
        parent: QWidget | None,
        message: str,
        level: tuple[str, str] | None = None,
        duration_ms: int = 2000,
    ) -> None:
        """创建 Toast 通知。

        Args:
            parent: 父控件（建议传入 MainWindow 或顶层 QWidget）
            message: 提示文本
            level: 提示级别 (bg_color, icon_text)。默认 Level.INFO
            duration_ms: 显示时长（毫秒）。默认 2000（2 秒）
        """
        super().__init__(parent)
        self._message = message
        self._level = level or self.Level.INFO
        self._duration_ms = duration_ms

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)  # 消失后自动释放

        self._build_ui()
        self._setup_animation()

    # ── 静态工厂方法 ──

    @classmethod
    def show_message(
        cls,
        parent: QWidget | None,
        message: str,
        level: tuple[str, str] | None = None,
        duration_ms: int = 2000,
    ) -> 'ToastNotification':
        """创建并显示一个 Toast 通知（便捷方法）。

        Args:
            parent: 父控件
            message: 提示文本
            level: 提示级别
            duration_ms: 显示时长

        Returns:
            创建的 ToastNotification 实例（可忽略；Toast 自动管理生命周期）
        """
        toast = cls(parent, message, level, duration_ms)
        toast.show()
        return toast

    # ── 事件处理 ──

    def showEvent(self, event) -> None:
        """显示事件——注册到活跃列表 + 计算堆叠位置 + 启动淡入动画 + 设置消失定时器。

        堆叠定位规则:
        - 所有 Toast 相对于父控件的右下角定位
        - 第一个 Toast: bottom-right 偏移 (20, 20)
        - 后续 Toast: 依次向上偏移 (自身高度 + 8px gap)
        - 移除已关闭的 Toast 引用，防止死引用累积
        """
        # 清理列表中已关闭的 Toast
        self._active_toasts = [t for t in self._active_toasts if t.isVisible()]

        # 计算位置
        if self.parent():
            parent_rect = self.parent().rect()
            x = parent_rect.width() - self.width() - 20
            base_y = parent_rect.height() - self.height() - 20
        else:
            x, base_y = 0, 0

        # 计算堆叠偏移
        gap = 8
        for toast in self._active_toasts:
            base_y -= (toast.height() + gap)

        self.move(x, max(base_y, 0))

        # 注册
        self._active_toasts.append(self)

        # 启动淡入
        self._fade_in_anim.start()

        # 设置定时消失
        QTimer.singleShot(self._duration_ms, self._dismiss)

    def closeEvent(self, event) -> None:
        """关闭事件——发射 dismissed 信号。"""
        self.dismissed.emit()
        super().closeEvent(event)

    # ── 内部构建 ──

    def _build_ui(self) -> None:
        """构建 Toast 布局。

        结构:
        ```
        QWidget (this)
        └── QHBoxLayout
            ├── QLabel (icon) —— "✓" / "✗" / "⚠" / "ℹ"
            └── QLabel (message) —— 提示文本
        ```

        样式:
        - 背景色 = level[0] (bg_color)
        - 圆角 6px
        - 最大宽度 360px（文本过长自动换行）
        - 固定高度自适应内容
        """
        bg_color, icon_text = self._level

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(0)

        # 文本标签
        self._msg_label = QLabel(self._message)
        self._msg_label.setStyleSheet(f"""
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 400;
            background: transparent;
        """)
        self._msg_label.setWordWrap(True)
        self._msg_label.setMaximumWidth(360)

        layout.addWidget(self._msg_label)

        # 整体样式
        self.setStyleSheet(f"""
            ToastNotification {{
                background-color: {bg_color};
                border-radius: 6px;
            }}
        """)

        self.setFixedWidth(400)  # 含 padding 的总宽度
        self.adjustSize()

    def _setup_animation(self) -> None:
        """设置淡入淡出动画。

        - 淡入: QGraphicsOpacityEffect + QPropertyAnimation（opacity 0 → 1，200ms）
        - 消失时调用 _dismiss(): 先淡出（opacity 1 → 0，150ms）再 close()
        """
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        # 淡入动画
        self._fade_in_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_in_anim.setDuration(200)
        self._fade_in_anim.setStartValue(0.0)
        self._fade_in_anim.setEndValue(1.0)
        self._fade_in_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _dismiss(self) -> None:
        """开始消失动画——淡出后关闭。

        步骤:
        1. 创建淡出动画 (opacity 1.0 → 0.0, 150ms)
        2. 动画结束 → self.close()
        3. closeEvent → 发射 dismissed → WA_DeleteOnClose → 自动 delete
        """
        self._fade_out_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_out_anim.setDuration(150)
        self._fade_out_anim.setStartValue(self._opacity_effect.opacity())
        self._fade_out_anim.setEndValue(0.0)
        self._fade_out_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out_anim.finished.connect(self.close)
        self._fade_out_anim.start()
```

### 2.2 ToastManager

```python
class ToastManager:
    """Toast 通知的全局管理器（可选——用于统一管理 Toast 生命周期）。

    提供静态方法，简化调用方式:
        ToastManager.success(main_window, "保存成功")
        ToastManager.error(main_window, "删除失败")
        ToastManager.warning(main_window, "数据未保存")
        ToastManager.info(main_window, "正在加载…")

    内部使用 ToastNotification.show_message() 创建实例。
    """

    @staticmethod
    def success(parent: QWidget | None, message: str, duration_ms: int = 2000) -> 'ToastNotification':
        """成功提示（绿色）。"""
        return ToastNotification.show_message(parent, message, ToastNotification.Level.SUCCESS, duration_ms)

    @staticmethod
    def error(parent: QWidget | None, message: str, duration_ms: int = 3000) -> 'ToastNotification':
        """错误提示（红色，默认显示更久）。"""
        return ToastNotification.show_message(parent, message, ToastNotification.Level.ERROR, duration_ms)

    @staticmethod
    def warning(parent: QWidget | None, message: str, duration_ms: int = 2500) -> 'ToastNotification':
        """警告提示（橙色）。"""
        return ToastNotification.show_message(parent, message, ToastNotification.Level.WARNING, duration_ms)

    @staticmethod
    def info(parent: QWidget | None, message: str, duration_ms: int = 2000) -> 'ToastNotification':
        """信息提示（蓝色）。"""
        return ToastNotification.show_message(parent, message, ToastNotification.Level.INFO, duration_ms)
```

---

## 3. confirm_dialog.py

### 3.1 ConfirmDialog

```python
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class ConfirmDialog(QDialog):
    """确认对话框——带可选的"不再提醒"复选框。

    支持场景:
    - 简单确认: "确定要删除此 Tasker 吗？此操作不可撤销。"
    - 带不再提醒: "确定要退出应用吗？" + ☐ 下次不再询问
    - 自定义按钮: 可指定确认/取消按钮的文字

    使用示例:
        # 简单确认
        result = ConfirmDialog.confirm(self, "确定要删除此 Tasker 吗？", "此操作不可撤销。")
        if result == ConfirmDialog.Accepted:
            ...

        # 带不再提醒
        dialog = ConfirmDialog(
            self, "确认", "确定要退出应用吗？",
            show_dont_ask=True, dont_ask_key="exit_confirm"
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.is_dont_ask_checked():
                AppConfig.set(f"confirm.{dont_ask_key}", False)
            ...
    """

    # 便捷静态方法的结果常量
    Accepted = QDialog.DialogCode.Accepted
    Rejected = QDialog.DialogCode.Rejected

    def __init__(
        self,
        parent: QWidget | None = None,
        title: str = "确认操作",
        message: str = "",
        detail: str = "",
        accept_text: str = "确定",
        reject_text: str = "取消",
        show_dont_ask: bool = False,
        dont_ask_label: str = "下次不再询问",
        is_dangerous: bool = False,
    ) -> None:
        """初始化确认对话框。

        Args:
            parent: 父窗口
            title: 对话框标题
            message: 主提示信息（粗体）
            detail: 补充说明信息（灰色，普通字号，换行显示）
            accept_text: 确认按钮文字（默认 "确定"）
            reject_text: 取消按钮文字（默认 "取消"）
            show_dont_ask: 是否显示 "不再询问" 复选框
            dont_ask_label: 复选框标签文字
            is_dangerous: True 时确认按钮使用危险配色（红色文字）——用于删除等不可逆操作
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(360)
        self.setMaximumWidth(520)

        # 去除窗口的 ? 帮助按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._show_dont_ask = show_dont_ask
        self._build_ui(message, detail, accept_text, reject_text, dont_ask_label, is_dangerous)

    # ── 公共属性 ──

    def is_dont_ask_checked(self) -> bool:
        """返回 "不再询问" 复选框是否被勾选。

        仅在 show_dont_ask=True 时有效；否则返回 False。
        """
        if not self._show_dont_ask:
            return False
        return self._dont_ask_cb.isChecked()

    # ── 便捷静态方法 ──

    @staticmethod
    def confirm(
        parent: QWidget | None,
        message: str,
        detail: str = "",
        title: str = "确认操作",
        dangerous: bool = False,
    ) -> 'QDialog.DialogCode':
        """简单确认对话框（无 "不再询问" 选项）。

        便捷方法——一行调用即可:
            if ConfirmDialog.confirm(self, "确定删除？", "此操作不可撤销。"):
                do_delete()

        Args:
            parent: 父窗口
            message: 主提示信息
            detail: 补充说明
            title: 标题
            dangerous: 是否使用危险配色

        Returns:
            QDialog.DialogCode.Accepted 或 QDialog.DialogCode.Rejected
        """
        dlg = ConfirmDialog(
            parent=parent, title=title, message=message, detail=detail,
            is_dangerous=dangerous,
        )
        return dlg.exec()

    @staticmethod
    def confirm_with_dont_ask(
        parent: QWidget | None,
        message: str,
        detail: str = "",
        title: str = "确认操作",
        dont_ask_label: str = "下次不再询问",
    ) -> tuple['QDialog.DialogCode', bool]:
        """确认对话框（带 "不再询问" 选项）。

        Returns:
            (dialog_code, dont_ask_checked) 二元组
        """
        dlg = ConfirmDialog(
            parent=parent, title=title, message=message, detail=detail,
            show_dont_ask=True, dont_ask_label=dont_ask_label,
        )
        code = dlg.exec()
        return code, dlg.is_dont_ask_checked()

    # ── 内部构建 ──

    def _build_ui(
        self, message: str, detail: str,
        accept_text: str, reject_text: str,
        dont_ask_label: str, is_dangerous: bool,
    ) -> None:
        """构建对话框布局。

        结构:
        ```
        QVBoxLayout
        ├── QLabel (message)       —— 粗体 14px, 深色
        ├── QLabel (detail)        —— 普通 12px, 灰色（空则隐藏）
        ├── spacer 12px
        ├── QCheckBox (dont_ask)   —— 仅 show_dont_ask=True 时显示
        └── QDialogButtonBox [reject_text] [accept_text]
        ```
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ── 主提示信息 ──
        msg_label = QLabel(message)
        msg_font = QFont()
        msg_font.setPointSize(14)
        msg_font.setBold(True)
        msg_label.setFont(msg_font)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("color: #E0E0E0;")
        layout.addWidget(msg_label)

        # ── 补充说明 ──
        if detail:
            detail_label = QLabel(detail)
            detail_font = QFont()
            detail_font.setPointSize(12)
            detail_label.setFont(detail_font)
            detail_label.setWordWrap(True)
            detail_label.setStyleSheet("color: #999999;")
            layout.addWidget(detail_label)

        layout.addSpacing(12)

        # ── "不再询问" 复选框 ──
        if self._show_dont_ask:
            self._dont_ask_cb = QCheckBox(dont_ask_label)
            self._dont_ask_cb.setStyleSheet("color: #AAAAAA; font-size: 12px;")
            layout.addWidget(self._dont_ask_cb)
        else:
            self._dont_ask_cb = None

        # ── 按钮 ──
        button_box = QDialogButtonBox()
        self._reject_btn = button_box.addButton(reject_text, QDialogButtonBox.ButtonRole.RejectRole)
        self._accept_btn = button_box.addButton(accept_text, QDialogButtonBox.ButtonRole.AcceptRole)

        # 危险操作——确认按钮使用红色
        if is_dangerous:
            self._accept_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C; color: #FFFFFF;
                    border: none; border-radius: 4px;
                    padding: 6px 20px; font-weight: 500;
                }
                QPushButton:hover { background-color: #C0392B; }
            """)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
```

---

## 4. 依赖关系

```
ui/component/
├── styled_button.py          # 依赖: PySide6.QtWidgets (QPushButton), PySide6.QtGui (QIcon, QFont)
├── toast_notification.py     # 依赖: PySide6.QtWidgets, PySide6.QtCore (QTimer, QPropertyAnimation)
├── confirm_dialog.py         # 依赖: PySide6.QtWidgets (QDialog, QLabel, QCheckBox, QDialogButtonBox)
└── __init__.py               # 导出: StyledButton, ToastNotification, ToastManager, ConfirmDialog
```

---

## 5. 设计约定

1. **纯 PySide6 组件**: 所有组件不依赖 core/ 或 storage/ 层。它们接收标准 Python 数据类型，由调用方负责桥接。

2. **信号驱动集成**: 组件通过 PySide6 信号与外部通信，不持有业务逻辑引用。调用方连接信号到 MainController 或其他业务层方法。

3. **独立可用**: 每个组件可独立实例化使用——不需要任何全局状态或注册表。

4. **样式内联**: 所有样式通过 setStyleSheet 内联定义，不依赖外部 .qss 文件——每个组件自带完整视觉定义。

5. **暗色主题**: 所有组件默认使用暗色主题配色（深灰背景 #1a1a2e / 浅色文字 #e0e0e0）。预留 `set_theme(light/dark)` 接口以便将来支持亮色主题切换。

6. **无障碍**: 所有按钮和交互控件使用 `setToolTip` 和 `setAccessibleName` 设置可访问性信息（具体实现待补充）。

7. **类型注解**: 所有公开方法使用完整的 Python 3.12+ 类型注解（`str | None`、`list[...]`、`QWidget | None`）。

8. **StyledButton 快捷键标注**: 按钮上显示的快捷键标注纯粹是视觉提示——实际快捷键绑定由调用方在 `MainWindow.keyPressEvent` 或 `QShortcut` 中处理。两者独立维护，确保快捷键标注与实际绑定一致由调用方负责。
