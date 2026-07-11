# SPEC: ui/tasker — Tasker 管理 UI 组件

> 对应源码路径: `src/ui/tasker/`
> 主界面内容显示区中的 Tasker 列表、创建/编辑对话框、右键菜单。使用 PySide6。

---

## 1. 布局概览

```
main_view (QStackedWidget 第 0 页)
├── WatermarkWidget (背景层, 半透明)
└── TaskerListWidget (前景层, 透明背景, QWidget)
    ├── QVBoxLayout
    │   ├── header_label (QLabel: "Tasker 列表")
    │   └── tasker_list_widget (QListWidget)
    │       ├── tasker_item_0  →  left-click: emit tasker_selected(id)
    │       │                   →  right-click: TaskerContextMenu
    │       ├── tasker_item_1
    │       └── ...
```

### 组件职责速查

| 组件 | 类型 | 职责 |
|------|------|------|
| `TaskerListWidget` | `QWidget` | 加载并展示 taskers.json 中的 Tasker 列表，支持点击选择和右键菜单 |
| `TaskerEditDialog` | `QDialog` | 模态对话框——创建/编辑 Tasker（label, description, type） |
| `TaskerContextMenu` | `QMenu` | 右键菜单——重命名、删除、查看信息 |

---

## 2. TaskerListWidget — Tasker 可点击列表

```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QAbstractItemView,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QContextMenuEvent, QFont, QColor
from core.types import TaskerSummary


class TaskerListWidget(QWidget):
    """主界面中显示 Tasker 可点击列表。按 taskers.json 数组顺序排列。

    作为 main_view 的前景层叠加在 WatermarkWidget 之上。
    自身背景透明，列表项使用圆角卡片样式。

    生命周期:
        - __init__ → 构建空列表 → MainController 调用 refresh() 加载数据
        - 用户进入 Tasker → 列表保留在内存（QStackedWidget 切换不销毁）
        - 返回主界面 → refresh() 刷新（可能新增/删除/重命名了 Tasker）
    """

    # --- 信号 ---
    tasker_selected = Signal(str)       # 用户左键单击 Tasker 项，参数为 tasker_id
    tasker_double_clicked = Signal(str) # 用户双击 Tasker 项 → 进入该 Tasker
    rename_requested = Signal(str)      # 右键 "重命名"，参数 tasker_id
    delete_requested = Signal(str)      # 右键 "删除"，参数 tasker_id
    info_requested = Signal(str)        # 右键 "查看信息"，参数 tasker_id

    def __init__(self, parent: QWidget | None = None) -> None:
        """初始化 Tasker 列表控件。

        步骤:
        1. 设置透明背景: setAttribute(Qt.WA_TranslucentBackground)
        2. 创建 QVBoxLayout: header_label + QListWidget
        3. 配置 QListWidget:
           - setSelectionMode(SingleSelection)
           - setFocusPolicy(NoFocus)  # 列表项不可编辑
           - setVerticalScrollMode(ScrollPerPixel)
           - 安装 custom delegate 绘制圆角卡片样式
        4. 连接信号:
           - itemClicked → 发射 tasker_selected
           - itemDoubleClicked → 发射 tasker_double_clicked
        5. 安装 contextMenuPolicy(CustomContextMenu) → 右键菜单
        """
        ...

    # --- 公共方法 ---

    def refresh(self, taskers: list[TaskerSummary]) -> None:
        """清空并重建列表（按 taskers 数组顺序）。

        Args:
            taskers: 从 taskers.json 读取的 Tasker 摘要列表。
                     每个元素包含 id, type, label, description, folder, quick_buttons。

        每个列表项的显示内容:
        - 主标题: label（粗体，14pt）
        - 副标题: description（截断至 80 字符，灰色，11pt）
        - 类型标签: type（小徽章，如 "default" / "timer" / "account"，彩色背景）

        使用 QListWidgetItem.setData(Qt.UserRole, tasker_id) 存储 id。
        """
        ...

    def set_loading(self, loading: bool) -> None:
        """设置加载状态——列表为空时显示 "加载中..." 占位文本。"""
        ...

    def clear_selection(self) -> None:
        """清除当前选中项。"""
        ...

    @property
    def selected_tasker_id(self) -> str | None:
        """当前选中的 Tasker id。无选中时返回 None。"""
        item = self._list.currentItem()
        return item.data(Qt.UserRole) if item else None

    @property
    def tasker_count(self) -> int:
        """当前列表中的 Tasker 数量。"""
        return self._list.count()

    # --- 右键菜单 ---

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """右键菜单事件。

        流程:
        1. 获取被右键的 item → 提取 tasker_id
        2. 若点击在空白区域（无 item）→ 不弹出菜单
        3. 创建 TaskerContextMenu 实例
        4. 连接 TaskerContextMenu 信号 → 转发为本 widget 信号
        5. menu.exec(event.globalPos())
        """
        ...

    # --- 样式 ---

    def _apply_styles(self) -> None:
        """应用列表样式。

        - QListWidget: 背景透明，无边线
        - QListWidget::item: 圆角 8px，margin 2px，hover 时浅灰背景
        - QListWidget::item:selected: 浅蓝背景 (#E3F2FD)
        """
        ...

    # --- 内部 ---

    def _build_ui(self) -> None:
        """构建布局。"""
        ...

    def _create_item_widget(self, tasker: TaskerSummary) -> QListWidgetItem:
        """为单个 Tasker 摘要创建 QListWidgetItem。

        Returns:
            配置好的 QListWidgetItem，UserRole 存储 tasker_id
        """
        ...

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """列表项点击 → 发射 tasker_selected(tasker_id)。
        同时更新选中样式（由 Qt 自动处理）。
        """
        ...

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """列表项双击 → 发射 tasker_double_clicked(tasker_id)。
        MainController 收到后调用 enter_tasker()。
        """
        ...
```

---

## 3. TaskerEditDialog — Tasker 创建/编辑对话框

```python
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QComboBox, QDialogButtonBox,
    QLabel, QMessageBox,
)
from PySide6.QtCore import Qt
from core.types import TaskerSummary


class TaskerEditDialog(QDialog):
    """模态对话框——创建或编辑 Tasker。

    字段:
    - label: 显示名称（QLineEdit, 必填）
    - description: 描述（QTextEdit, 2行, 可选）
    - type: Tasker 类型（QComboBox, 创建时可选择, 编辑时禁用只读）

    编辑模式下 pre-populate 已有字段值，type 下拉框禁用（不可改类型）。
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        existing: TaskerSummary | None = None,
        registered_types: list[str] | None = None,
    ) -> None:
        """初始化对话框。

        Args:
            parent: 父窗口
            existing: 编辑模式——传入现有 Tasker 摘要。None 为创建模式。
            registered_types: 可选 Tasker 类型列表（从 ExtensionRegistry 获取）。
                              如 ["default", "timer", "account", "label"]。
                              创建模式下为空或只有一个选项时禁用下拉框。

        步骤:
        1. 设置窗口标题: "新建 Tasker" / "编辑 Tasker"
        2. setMinimumWidth(400)
        3. 构建表单布局
        4. 若 existing → _populate(existing) 预填字段
        5. 若创建模式 → type 下拉框可选择；编辑模式 → 禁用
        6. 连接 OK/Cancel 按钮
        """
        ...

    # --- 公共方法 ---

    def get_result(self) -> dict:
        """返回编辑结果（仅在 accepted 后调用有效）。

        Returns:
            dict: {
                "label": str,
                "description": str,
                "type": str,  # 创建模式返回用户选择的类型，编辑模式返回原类型
            }

        Raises:
            RuntimeError: 对话框未通过 accepted 关闭时调用
        """
        ...

    @staticmethod
    def create_tasker(
        parent: QWidget | None = None,
        registered_types: list[str] | None = None,
    ) -> dict | None:
        """便捷静态方法——打开创建对话框。

        Args:
            parent: 父窗口
            registered_types: 可选 Tasker 类型列表

        Returns:
            结果 dict 或 None（用户取消）
        """
        dlg = TaskerEditDialog(parent, existing=None, registered_types=registered_types)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg.get_result()
        return None

    @staticmethod
    def edit_tasker(
        parent: QWidget | None = None,
        existing: TaskerSummary | None = None,
    ) -> dict | None:
        """便捷静态方法——打开编辑对话框。

        Args:
            parent: 父窗口
            existing: 现有 Tasker 信息

        Returns:
            结果 dict 或 None（用户取消）
        """
        dlg = TaskerEditDialog(parent, existing=existing)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg.get_result()
        return None

    # --- 内部 ---

    def _build_form(self) -> None:
        """构建表单布局。

        表单行:
        - "名称:" → self._label_edit (QLineEdit, placeholder="输入 Tasker 名称")
        - "描述:" → self._desc_edit (QTextEdit, max_height=60, placeholder="可选描述")
        - "类型:" → self._type_combo (QComboBox, items=registered_types)
        """
        ...

    def _populate(self, existing: TaskerSummary) -> None:
        """预填已有数据。

        - label_edit.setText(existing["label"])
        - desc_edit.setText(existing["description"])
        - type_combo 设为 existing["type"] 并禁用
        """
        ...

    def _validate_and_accept(self) -> None:
        """验证输入后接受对话框。

        验证规则:
        - label 不能为空（去除首尾空白后）
        - type 必须有选中项

        不合法时弹出 QMessageBox.warning 并聚焦对应控件。
        """
        ...
```

---

## 4. TaskerContextMenu — 右键菜单

```python
from PySide6.QtWidgets import QMenu, QWidget
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction


class TaskerContextMenu(QMenu):
    """Tasker 列表项上的右键菜单。

    三个菜单项:
    - "重命名" → 发射 rename_triggered(tasker_id)
    - "删除"   → 发射 delete_triggered(tasker_id)
    - "信息"   → 发射 info_triggered(tasker_id)
    """

    # --- 信号 ---
    rename_triggered = Signal(str)  # tasker_id
    delete_triggered = Signal(str)  # tasker_id
    info_triggered = Signal(str)    # tasker_id

    def __init__(self, parent: QWidget | None, tasker_id: str, tasker_label: str = "") -> None:
        """初始化右键菜单。

        Args:
            parent: 父控件
            tasker_id: 右键的 Tasker id
            tasker_label: Tasker 显示名称（用于菜单中的文本，如 "删除 "班级""）

        步骤:
        1. 调用 super().__init__(parent)
        2. 添加 QAction("重命名") → 连接 rename_triggered
        3. 添加 QAction(f'删除 "{tasker_label}"') → 连接 delete_triggered
           - 删除项使用红色文字样式
        4. 添加 separator
        5. 添加 QAction("查看信息") → 连接 info_triggered
        """
        ...

    def _on_rename(self) -> None:
        """触发重命名: 发射 rename_triggered(tasker_id)。
        MainController 收到后打开 TaskerEditDialog (编辑模式)。
        """
        ...

    def _on_delete(self) -> None:
        """触发删除: 发射 delete_triggered(tasker_id)。
        MainController 收到后弹出 ConfirmDialog → tasker_service.delete_tasker()。
        """
        ...

    def _on_info(self) -> None:
        """触发查看信息: 发射 info_triggered(tasker_id)。
        MainController 收到后在 output_area 打印 Tasker 详细信息
        （id, type, label, description, folder, 已加载 task 数量）。
        """
        ...
```

---

## 5. 信号流

```
┌─────────────────────────────────────────────────────────────────┐
│                       Tasker UI 信号流                           │
│                                                                 │
│  TaskerListWidget.tasker_selected(tasker_id)                    │
│       │                                                         │
│       └──► MainController._on_tasker_selected(id)               │
│               → 高亮选中项，更新 commands_panel 显示全局指令      │
│                                                                 │
│  TaskerListWidget.tasker_double_clicked(tasker_id)               │
│       │                                                         │
│       └──► MainController.enter_tasker(tasker_id)               │
│                                                                 │
│  TaskerListWidget.rename_requested(tasker_id)                    │
│       │                                                         │
│       └──► TaskerEditDialog.edit_tasker(parent, existing)       │
│               → tasker_service.update_tasker(id, result)        │
│               → TaskerListWidget.refresh()                       │
│                                                                 │
│  TaskerListWidget.delete_requested(tasker_id)                    │
│       │                                                         │
│       └──► ConfirmDialog("确认删除此 Tasker 及其全部数据？")      │
│               → 确认: tasker_service.delete_tasker(id)          │
│               → TaskerListWidget.refresh()                       │
│                                                                 │
│  TaskerListWidget.info_requested(tasker_id)                      │
│       │                                                         │
│       └──► tasker_service.get_tasker(id)                        │
│               → MainWindow.log(tasker_info_text)                │
│                                                                 │
│  TaskerEditDialog.accepted                                       │
│       │                                                         │
│       └──► 创建模式: tasker_service.create_tasker(result)        │
│               → TaskerListWidget.refresh()                       │
│           编辑模式: tasker_service.update_tasker(id, result)     │
│               → TaskerListWidget.refresh()                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. 与 MainController 的集成

MainController 连接 TaskerListWidget 信号:

```python
# 在 MainController.__init__ 或 _build_main_view 中:
tasker_list = TaskerListWidget()
tasker_list.tasker_double_clicked.connect(self.enter_tasker)
tasker_list.rename_requested.connect(self.open_edit_tasker_dialog)
tasker_list.delete_requested.connect(self.confirm_delete_tasker)
tasker_list.info_requested.connect(self.show_tasker_info)

# 初始加载:
tasker_list.refresh(self._tasker_service.list_taskers())

# 返回主界面时刷新:
def switch_to_main_view(self):
    self._main_window.content_area.setCurrentIndex(0)
    self._tasker_list_widget.refresh(self._tasker_service.list_taskers())
```

---

## 7. 依赖关系

```
ui/tasker/
├── tasker_list_widget.py    # 依赖: PySide6, core/types.py (TaskerSummary)
├── tasker_edit_dialog.py    # 依赖: PySide6, core/types.py (TaskerSummary)
├── tasker_context_menu.py   # 依赖: PySide6
└── __init__.py
```

本包不直接导入 core 服务接口——所有数据通过信号传递给 MainController，由 MainController 调用服务层。

---

## 8. 注意事项

1. **列表透明背景**：TaskerListWidget 作为 WatermarkWidget 的前景层，必须设置 `setAttribute(Qt.WA_TranslucentBackground)` 并避免绘制背景。QListWidget 使用 stylesheet 设置 `background: transparent`。

2. **列表项圆角卡片**：使用 `QStyledItemDelegate` 在 `paint()` 中绘制圆角矩形背景。hover / selected 状态通过不同背景色区分。

3. **列表刷新频率**：仅在以下时机调用 `refresh()`：
   - MainController 初始化完成后
   - 创建/删除/重命名 Tasker 后
   - 从 tasker_view 返回 main_view 时
   不需要每次 Task CRUD 都刷新（列表内容不变）。

4. **TaskerEditDialog 的 type 字段**：编辑模式下禁用 type 下拉框——Tasker 类型创建后不可更改。这避免了类型不匹配导致的数据读取错误。

5. **删除确认**：右键菜单的"删除"项不直接执行删除——发射 delete_requested 信号后，由 MainController 弹出 ConfirmDialog 获取二次确认，防止误操作。

6. **右键菜单的 tasker_label**：用于"删除"菜单项的文本（如 `删除 "班级"`），提供视觉确认让用户知道正在操作哪个 Tasker。label 可能很长——截断至 30 字符并加省略号。
