# SPEC: extensions/quick_button — 快捷按钮模块

> 对应源码路径: `src/extensions/quick_button/`
> 快捷按钮是用户自定义的一键 Task 创建预设。模板数据存储在 `taskers.json` 中绑定在对应 Tasker 上。主界面常驻区列出所有 Tasker 的快捷按钮——点击后自动进入目标 Tasker 并执行。

## 1. quick_button_service.py

```python
from core.abstract import BaseTask, BaseTasker
from core.types import QuickButtonDef


class QuickButtonService:
    """快捷按钮业务逻辑——触发、计数、排序。"""

    def trigger(self, tasker: BaseTasker, button_def: QuickButtonDef) -> BaseTask | None:
        """触发一个快捷按钮，在指定 Tasker 中创建一条 Task。

        流程:
        1. 调用 tasker.execute_quick_button(button_def)
           - Tasker 内部解析 preset，处理 use_default_date、默认值等
           - 各 Tasker 类型自行实现具体字段映射（如 TimerTasker 额外填入 start_time）
        2. 若返回 None（content 为空且 Tasker 判定需用户输入）→ 返回 None
           调用方应弹出输入框让用户补充 content，修改 button_def["preset"]["content"] 后重试
        3. 若返回有效 Task → 调用 increment_count(button_def) 记录使用次数 → 返回创建的 Task

        Args:
            tasker: 目标 Tasker 实例（由调用方先进入或加载）
            button_def: 快捷按钮模板定义

        Returns:
            创建的 BaseTask 实例，或 None（content 为空，等待用户输入后重试）
        """
        result = tasker.execute_quick_button(button_def)
        if result is not None:
            self.increment_count(button_def)
        return result

    def increment_count(self, button_def: QuickButtonDef) -> None:
        """递增按钮的使用计数。

        button_def 为可变 dict —— 直接在其上读写 usage_count 字段。
        usage_count 不存在时从 1 开始；已存在时 +1。
        该字段持久化到 taskers.json 的 quick_buttons 数组的每条记录中。
        """
        button_def["usage_count"] = button_def.get("usage_count", 0) + 1

    def sort_by_usage(self, buttons: list[QuickButtonDef]) -> None:
        """按使用频率降序排列按钮列表（原地排序）。

        usage_count 缺失的按钮视为 0，排在末尾。
        同次数按钮保持原有相对顺序（稳定排序）。

        Args:
            buttons: 快捷按钮定义列表（原地修改）
        """
        buttons.sort(key=lambda b: b.get("usage_count", 0), reverse=True)
```

## 2. quick_button_bar_widget.py

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal
from core.types import QuickButtonDef
from typing import Callable


class QuickButtonBarWidget(QWidget):
    """常驻区中的快捷按钮 UI 组件。

    垂直排列，按 Tasker 分组显示所有快捷按钮。
    按钮上方显示所属 Tasker 标签（若有多个 Tasker 各自有按钮时）。
    数字键 1-9 可触发前 9 个按钮，Enter 确认触发当前高亮按钮。
    """

    # 信号: 请求触发某个 Tasker 下的按钮
    # 参数: (tasker_id: str, button_def: QuickButtonDef)
    trigger_requested = Signal(str, dict)

    def __init__(self, parent: QWidget | None,
                 buttons_by_tasker: dict[str, list[QuickButtonDef]],
                 on_trigger: Callable[[str, QuickButtonDef], None]):
        """
        Args:
            parent: 父控件
            buttons_by_tasker: {tasker_id: [QuickButtonDef, ...], ...}
               每个 Tasker 的快捷按钮列表。key 为 tasker_id，用于标识按钮归属。
               按钮列表已按使用频率排序（调用方先用 sort_by_usage 排好）。
            on_trigger: 回调 (tasker_id, button_def) —— 当按钮被点击或数字键触发时调用。
               回调负责: 进入目标 Tasker → 调用 QuickButtonService.trigger() 创建 Task。
        """
        super().__init__(parent)
        self._buttons_by_tasker = buttons_by_tasker
        self._on_trigger = on_trigger
        self._button_widgets: list[QPushButton] = []  # 扁平化按钮引用（按显示顺序）
        self._highlighted_index: int = -1

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(4)

        self._build_ui()

    # ── 公共方法 ──

    def refresh(self) -> None:
        """刷新按钮显示——清空并重建全部按钮控件。

        调用时机:
        - 快捷按钮模板被编辑（新增/删除/修改）
        - Tasker 被删除（其按钮需移除）
        - 按钮使用后重新排序

        调用方应先更新 self._buttons_by_tasker 的引用或内容，再调用 refresh()。
        """
        self._clear_layout()
        self._build_ui()

    def highlight_nth(self, n: int) -> None:
        """高亮第 n 个按钮（n 从 1 开始，对应数字键 1-9）。

        行为:
        - 清除上一个高亮按钮的样式
        - 对第 n 个按钮应用高亮样式（如边框加粗或背景色变化）
        - n 超出按钮总数 → 不做任何操作
        - 按下 Enter 键时触发当前高亮按钮

        Args:
            n: 按钮序号（1-based，对应数字键）
        """
        if n < 1 or n > len(self._button_widgets):
            return
        # 清除旧高亮
        if 0 <= self._highlighted_index < len(self._button_widgets):
            self._button_widgets[self._highlighted_index].setStyleSheet("")
        # 设置新高亮
        self._highlighted_index = n - 1
        btn = self._button_widgets[self._highlighted_index]
        btn.setStyleSheet("border: 2px solid #4A90D9;")

    def trigger_highlighted(self) -> None:
        """触发当前高亮的按钮（由 Enter 键调用）。无高亮按钮时无操作。"""
        if 0 <= self._highlighted_index < len(self._button_widgets):
            self._button_widgets[self._highlighted_index].click()

    # ── 内部构建 ──

    def _build_ui(self) -> None:
        """根据 buttons_by_tasker 构建按钮布局。

        扁平化遍历所有 Tasker 的按钮:
        - 若多个 Tasker 都有按钮 → 每个 Tasker 前插入一个分隔标签显示 Tasker 名
        - 若仅一个 Tasker 有按钮 → 省略 Tasker 标签
        - 每个按钮前标注序号（1-9），后面超出部分不标号但保留按钮

        每个按钮存储 (tasker_id, button_def) 对，点击时发射 trigger_requested 信号并调用 on_trigger。
        """
        self._button_widgets.clear()
        self._highlighted_index = -1

        taskers_with_buttons = [
            (tid, btns) for tid, btns in self._buttons_by_tasker.items() if btns
        ]
        show_tasker_labels = len(taskers_with_buttons) > 1

        global_index = 0
        for tasker_id, buttons in taskers_with_buttons:
            if show_tasker_labels:
                label = QLabel(f"▸ {tasker_id}")
                label.setStyleSheet("color: #888; font-size: 11px; padding: 4px 0 2px 4px;")
                self._layout.addWidget(label)

            for btn_def in buttons:
                global_index += 1
                num_prefix = f"{global_index}. " if global_index <= 9 else ""
                text = f"{num_prefix}{btn_def.get('label', btn_def.get('command', ''))}"
                btn = QPushButton(text)
                btn.setToolTip(
                    f"指令: {btn_def.get('command', '')}\n"
                    f"Tasker: {tasker_id}\n"
                    f"预设: {btn_def.get('preset', {})}"
                )
                # 闭包捕获当前 tasker_id 和 btn_def
                btn.clicked.connect(
                    lambda checked=False, tid=tasker_id, bd=btn_def: self._on_button_clicked(tid, bd)
                )
                self._layout.addWidget(btn)
                self._button_widgets.append(btn)

        self._layout.addStretch()

    def _on_button_clicked(self, tasker_id: str, button_def: QuickButtonDef) -> None:
        """按钮点击处理——发射信号并调用外部回调。"""
        self.trigger_requested.emit(tasker_id, button_def)
        self._on_trigger(tasker_id, button_def)

    def _clear_layout(self) -> None:
        """递归清空布局中的所有子控件。"""
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_sublayout(item.layout())

    def _clear_sublayout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_sublayout(item.layout())
```

## 3. quick_button_editor.py

```python
from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit,
                                QCheckBox, QDialogButtonBox, QVBoxLayout)
from core.types import QuickButtonDef, PresetFields


class QuickButtonEditor(QDialog):
    """创建/编辑快捷按钮的对话框。

    模态对话框，包含:
    - command: 自定义指令名（如 "hw"）
    - label: 按钮显示文本（如 "记作业"）
    - date: 固定日期（留空 + use_default_date=True → 自动取当天）
    - attribute: 预设属性
    - content: 预设内容（留空 → 点击后需用户输入）
    - comment: 预设注释
    - use_default_date: 勾选后忽略 date 字段，自动取当天日期
    """

    def __init__(self, parent: QWidget | None = None,
                 existing: QuickButtonDef | None = None):
        """
        Args:
            parent: 父窗口
            existing: 编辑已有按钮时传入现有定义；创建新按钮时传 None
        """
        super().__init__(parent)
        self.setWindowTitle("编辑快捷按钮" if existing else "新建快捷按钮")
        self.setMinimumWidth(360)

        # ── 表单控件 ──
        self._cmd_edit = QLineEdit()
        self._cmd_edit.setPlaceholderText("如: hw")

        self._label_edit = QLineEdit()
        self._label_edit.setPlaceholderText("如: 记作业")

        self._use_default_date_cb = QCheckBox("使用当天日期")
        self._use_default_date_cb.toggled.connect(self._on_use_default_toggled)

        self._date_edit = QLineEdit()
        self._date_edit.setPlaceholderText("YYYY_MM_DD（留空+勾选上方=当天）")

        self._attr_edit = QLineEdit()
        self._attr_edit.setPlaceholderText("如: 作业")

        self._content_edit = QLineEdit()
        self._content_edit.setPlaceholderText("留空则点击后需用户输入")

        self._comment_edit = QLineEdit()
        self._comment_edit.setPlaceholderText("可选注释")

        # ── 布局 ──
        form = QFormLayout()
        form.addRow("指令名:", self._cmd_edit)
        form.addRow("显示标签:", self._label_edit)
        form.addRow("", self._use_default_date_cb)
        form.addRow("日期:", self._date_edit)
        form.addRow("属性:", self._attr_edit)
        form.addRow("内容:", self._content_edit)
        form.addRow("注释:", self._comment_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        # ── 预填已有数据 ──
        if existing:
            self._populate(existing)

    # ── 公共方法 ──

    def get_button_def(self) -> QuickButtonDef:
        """返回编辑结果（仅在 accepted 后调用有效）。

        Returns:
            QuickButtonDef: {"command": str, "label": str, "preset": PresetFields}
        """
        preset: PresetFields = {}
        if self._use_default_date_cb.isChecked():
            preset["use_default_date"] = True
        elif self._date_edit.text().strip():
            preset["date"] = self._date_edit.text().strip()
        if self._attr_edit.text().strip():
            preset["attribute"] = self._attr_edit.text().strip()
        if self._content_edit.text().strip():
            preset["content"] = self._content_edit.text().strip()
        if self._comment_edit.text().strip():
            preset["comment"] = self._comment_edit.text().strip()

        return QuickButtonDef(
            command=self._cmd_edit.text().strip(),
            label=self._label_edit.text().strip(),
            preset=preset,
        )

    @staticmethod
    def edit_button(parent: QWidget | None,
                    existing: QuickButtonDef | None = None) -> QuickButtonDef | None:
        """便捷静态方法——打开对话框并返回结果。

        Args:
            parent: 父窗口
            existing: 现有按钮定义（编辑模式），None 为新建模式

        Returns:
            QuickButtonDef 或 None（用户取消）
        """
        dlg = QuickButtonEditor(parent, existing)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg.get_button_def()
        return None

    # ── 内部 ──

    def _populate(self, existing: QuickButtonDef) -> None:
        """预填已有数据。"""
        self._cmd_edit.setText(existing.get("command", ""))
        self._label_edit.setText(existing.get("label", ""))
        preset = existing.get("preset", {})
        if preset.get("use_default_date"):
            self._use_default_date_cb.setChecked(True)
        else:
            self._date_edit.setText(preset.get("date", ""))
        self._attr_edit.setText(preset.get("attribute", ""))
        self._content_edit.setText(preset.get("content", ""))
        self._comment_edit.setText(preset.get("comment", ""))

    def _on_use_default_toggled(self, checked: bool) -> None:
        """勾选"使用当天日期"时禁用日期输入框。"""
        self._date_edit.setEnabled(not checked)

    def _validate_and_accept(self) -> None:
        """验证输入后接受对话框。

        验证规则:
        - command 不能为空
        - label 不能为空
        """
        cmd = self._cmd_edit.text().strip()
        label = self._label_edit.text().strip()
        if not cmd:
            # 简单提示 —— 实际可通过 QMessageBox 显示错误
            self._cmd_edit.setFocus()
            return
        if not label:
            self._label_edit.setFocus()
            return
        self.accept()
```

## 4. __init__.py

```python
# 快捷按钮模块不注册任何类型到 ExtensionRegistry。
# 快捷按钮是数据驱动的——模板存储在 taskers.json 的 quick_buttons 字段中，
# 由 QuickButtonService 负责触发逻辑，无需通过注册表查找。
#
# 导出本模块的公共 API:
from .quick_button_service import QuickButtonService
from .quick_button_bar_widget import QuickButtonBarWidget
from .quick_button_editor import QuickButtonEditor

__all__ = [
    "QuickButtonService",
    "QuickButtonBarWidget",
    "QuickButtonEditor",
]
```

## 5. 数据流与交互

### 5.1 主界面 → 快捷按钮触发

```
用户点击主界面常驻区中的快捷按钮
  → QuickButtonBarWidget 发射 trigger_requested(tasker_id, button_def)
  → MainController.on_quick_button_triggered(tasker_id, button_def):
      1. 通过 DefaultTaskerService.get_tasker(tasker_id) 加载目标 Tasker
      2. 切换到该 Tasker 视图
      3. 调用 QuickButtonService.trigger(tasker, button_def)
         → tasker.execute_quick_button(button_def)
           → 解析 preset → create_task(fields) → 返回 BaseTask
         → increment_count(button_def)
         → 返回 BaseTask
      4. 若返回 None（content 为空）→ 弹出 InlineInputBar 让用户输入 content
         → 修改 button_def["preset"]["content"] → 重试 trigger()
      5. Task 创建成功 → 刷新 Task 表格 → 按钮按使用频率重排 → 保存 taskers.json
```

### 5.2 快捷按钮的持久化

- 按钮模板存储在 `taskers.json` 每条 Tasker 的 `quick_buttons` 数组中
- `usage_count` 为每个按钮的动态字段，不在 `QuickButtonDef` TypedDict 中声明但由 service 读写
- 按钮的增删改通过 TaskerIndexManager 写回 `taskers.json`
- 触发按钮后 usage_count 变更 → 需调度保存 taskers.json（低频，不是每次增删 Task）

### 5.3 数字键触发

```
用户在 Tasker 界面或主界面按数字键 1-9
  → MainWindow.keyPressEvent 捕获
  → QuickButtonBarWidget.highlight_nth(n) 高亮对应按钮
  → 用户按 Enter
  → QuickButtonBarWidget.trigger_highlighted()
  → 走 5.1 的流程
```

### 5.4 Tasker 侧实现要求

每个实现 `BaseTasker` 的 Tasker 子类必须实现 `execute_quick_button(button_template: dict) → BaseTask | None` 方法。该方法负责:
- 从 `button_template["preset"]` 提取预设字段
- 处理 `use_default_date`（取当天日期）
- 处理空 content（返回 None 由 UI 层弹框）
- 调用 `self.create_task(fields)` 创建并返回 Task

此方法不依赖 UI 信号——由 QuickButtonService 直接调用。

## 6. 依赖关系

```
extensions/quick_button/
├── quick_button_service.py     # 依赖 core/abstract.py (BaseTask, BaseTasker), core/types.py
├── quick_button_bar_widget.py  # 依赖 PySide6, core/types.py
├── quick_button_editor.py      # 依赖 PySide6, core/types.py
└── __init__.py                 # 不注册到 ExtensionRegistry，仅导出公共 API
```

本模块是唯一不向 ExtensionRegistry 注册任何类型的扩展模块——按钮逻辑由数据驱动，不依赖类型注册表。
