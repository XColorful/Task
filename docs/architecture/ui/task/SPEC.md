# SPEC: ui/task — Task 表格、编辑面板、内联输入与搜索

> 对应源码路径: `src/ui/task/`
> Tasker 界面内用于展示、创建、编辑、搜索 Task 的核心 UI 组件。使用 PySide6。

---

## 1. 布局概览

```
tasker_view (QStackedWidget 第 1 页)
├── QVBoxLayout
│   ├── TaskSearchBar (QLineEdit, 防抖 200ms)
│   │   └── 输入即搜索 → 实时过滤 TaskTableWidget
│   ├── TaskTableWidget (QTableView + TaskTableModel)
│   │   └── 列: index | date | attribute | content | comment
│   │   └── 支持按列排序、方向键/鼠标滚动动态加载 segment
│   ├── InlineInputBar (QLineEdit)
│   │   └── 快捷创建: 输入 content → Tab 选 Tasker → Enter 创建
│   └── TaskEditPanel (QWidget, 可折叠)
│       └── 表单: date | attribute | content | comment
│       └── Tab 键在字段间跳转, Ctrl+Enter 提交
```

### 组件职责速查

| 组件 | 类型 | 职责 |
|------|------|------|
| `TaskTableWidget` | `QTableView` | 展示 Task 列表，内置 `TaskTableModel`，支持排序、滚动分段加载 |
| `TaskTableModel` | `QAbstractTableModel` | Task 数据源——从 BaseTasker.task_list 读取，索引列虚拟化 |
| `TaskEditPanel` | `QWidget` | 表单布局的 Task 创建/编辑面板，Tab 导航，可折叠 |
| `InlineInputBar` | `QLineEdit` | 快捷创建输入框——content 先行，Tab 选 Tasker，Enter 创建 |
| `TaskSearchBar` | `QLineEdit` | 带防抖的实时搜索栏，过滤 TaskTableWidget |

---

## 2. TaskTableModel — Task 数据模型

```python
from __future__ import annotations
from typing import Any
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QColor
from core.abstract import BaseTask


class TaskTableModel(QAbstractTableModel):
    """Task 数据的表格模型。基于 BaseTasker.task_list 提供 QTableView 数据源。

    列定义（5 列）:
        0: index     — int, 全局序号（从 1 开始，虚拟化计算，不存于 Task）
        1: date      — str, "YYYY_MM_DD"
        2: attribute — str, 属性/分类
        3: content   — str, 主要内容
        4: comment   — str, 注释

    排序: 默认按 task_list 顺序（即 index 升序）。
          点击列表头切换排序列/升降序，使用 QSortFilterProxyModel 代理。
          排序仅在内存已加载范围内进行。

    生命周期:
        - MainController.enter_tasker() 时创建
        - 切换 Tasker 时创建新 model 实例替换旧 model
        - 退出 Tasker 时销毁
    """

    # 表头标签
    _HEADERS: list[str] = ["#", "日期", "属性", "内容", "注释"]

    def __init__(self, parent: QWidget | None = None) -> None:
        """初始化空 model。task_list 通过 set_task_list() 设置。"""
        super().__init__(parent)
        self._tasks: list[BaseTask] = []
        self._offset: int = 0  # 此批数据的起始全局索引

    # --- 数据设置 ---

    def set_task_list(self, tasks: list[BaseTask], offset: int = 0) -> None:
        """设置/替换全部 task 数据。

        Args:
            tasks: Task 列表（已加载的 segment 数据）
            offset: 此批数据在全局 task_list 中的起始索引（用于 index 列计算）

        调用:
            beginResetModel() → self._tasks = tasks → self._offset = offset → endResetModel()
        """
        ...

    def append_tasks(self, tasks: list[BaseTask]) -> None:
        """追加任务（滚动加载更多 segment 时）。

        Args:
            tasks: 新加载的 Task 列表

        调用:
            beginInsertRows() → extend → endInsertRows()
        """
        ...

    def prepend_tasks(self, tasks: list[BaseTask]) -> None:
        """前插任务（向上滚动加载更早 segment 时）。

        Args:
            tasks: 更早的 Task 列表

        调用:
            beginInsertRows() → 插入到头部 → endInsertRows() → 更新 self._offset
        """
        ...

    def update_task(self, row: int, task: BaseTask) -> None:
        """更新单行数据（编辑 Task 后调用）。"""
        self._tasks[row] = task
        self.dataChanged.emit(
            self.index(row, 0), self.index(row, self.columnCount() - 1)
        )

    def remove_task(self, row: int) -> None:
        """移除单行（删除 Task 后调用）。"""
        beginRemoveRows → del → endRemoveRows

    def insert_task(self, row: int, task: BaseTask) -> None:
        """在指定位置插入一行（新建 Task 后调用）。"""
        beginInsertRows → insert → endInsertRows

    def task_at(self, row: int) -> BaseTask | None:
        """返回指定行的 BaseTask。行越界返回 None。"""
        ...

    def global_index_for_row(self, row: int) -> int:
        """计算行的全局序号 = self._offset + row + 1。"""
        return self._offset + row + 1

    @property
    def task_count(self) -> int:
        """当前 model 中的 Task 数量。"""
        return len(self._tasks)

    # --- QAbstractTableModel 必须实现 ---

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """返回 self._tasks 的长度。"""
        return len(self._tasks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """固定 5 列。"""
        return 5

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """根据角色返回数据。

        Qt.DisplayRole:
            col 0 → 全局序号 (self._offset + row + 1)
            col 1 → task.date
            col 2 → task.attribute
            col 3 → task.content
            col 4 → task.comment

        Qt.TextAlignmentRole:
            col 0 → AlignRight | AlignVCenter（序号右对齐）
            其他列 → AlignLeft | AlignVCenter

        Qt.ForegroundRole:
            col 2 (attribute) 为空或 "N/A" → 灰色 (#AAA)
            col 4 (comment) 为空 → 灰色 (#CCC)

        Qt.UserRole:
            返回 (global_index, task) 元组 —— 供代理视图排序/搜索时使用
        """
        ...

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole) -> Any:
        """返回表头文本。"""
        ...

    # --- 自定义角色 ---
    TASK_ROLE = Qt.UserRole + 1  # 返回 BaseTask 实例
    GLOBAL_INDEX_ROLE = Qt.UserRole + 2  # 返回全局序号 int
```

---

## 3. TaskTableWidget — 中央 Task 表格

```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView,
)
from PySide6.QtCore import Signal, Qt, QItemSelection
from PySide6.QtGui import QKeyEvent, QWheelEvent
from core.abstract import BaseTask


class TaskTableWidget(QWidget):
    """Tasker 界面中的中央 Task 表格。封装 QTableView + TaskTableModel + 排序代理。

    功能:
    - 列可排序（点击表头切换升降序）
    - 滚动到边界自动触发分段加载（向上 → 加载更早 segment，向下 → 加载更晚 segment）
    - 键盘导航: 上下方向键移动选中行，Delete 键触发删除当前行
    - 双击行 → 打开 TaskEditPanel 编辑模式
    - 右键菜单 → 编辑 / 删除（由 TaskerContextMenu 风格扩展）

    两段懒加载策略:
    - 进入 Tasker 时: 加载最后 2 个 segment（最近 ~1000 条），视图滚动到最底部
    - 向上滚动到顶部: 触发加载上一段 segment 并前置到 model 开头
    - 向下滚动到底部: 若无更晚段则不触发；若中间段（全量加载后）不做加载
    - 正数索引用法（用户使用正数索引查找早期记录）→ 触发全量加载

    生命周期:
        - MainController.enter_tasker() 创建 → 放入 tasker_view
        - 切换 Tasker → 创建新实例替换
        - 退出 Tasker → 销毁
    """

    # --- 信号 ---
    task_selected = Signal(int, BaseTask)       # (global_index, task) — 选中行变化
    task_double_clicked = Signal(int, BaseTask) # (global_index, task) — 双击编辑
    task_delete_requested = Signal(int)         # global_index — 请求删除
    more_data_needed = Signal(int)              # direction: -1=向上(更早段), +1=向下(更晚段)
    all_data_needed = Signal()                  # 用户使用正数索引 → 请求全量加载

    def __init__(self, parent: QWidget | None = None) -> None:
        """初始化表格。

        步骤:
        1. 创建 QVBoxLayout → QTableView
        2. 创建 TaskTableModel 并设置到 view
        3. 创建 QSortFilterProxyModel 包裹 model（启用排序）
        4. 配置 QTableView:
           - setSelectionBehavior(SelectRows)
           - setSelectionMode(SingleSelection)
           - setSortingEnabled(True)
           - setAlternatingRowColors(True)
           - horizontalHeader().setStretchLastSection(True)
           - verticalHeader().setVisible(False)
           - setEditTriggers(NoEditTriggers)  # 不可直接编辑单元格
        5. 设置列宽:
           - col 0 (index):    固定 60px
           - col 1 (date):     固定 100px
           - col 2 (attribute): 固定 120px
           - col 3 (content):  自动拉伸 (Stretch)
           - col 4 (comment):  自动拉伸 (Stretch)
        6. 安装事件过滤器处理 Delete 键
        7. 连接信号:
           - selectionModel().selectionChanged → task_selected
           - view.doubleClicked → task_double_clicked
           - 自定义滚动检测 → more_data_needed
        """
        ...

    # --- 公共方法 ---

    def load_initial_data(self, tasks: list[BaseTask], total_count: int) -> None:
        """加载初始数据（进入 Tasker 时调用）。

        Args:
            tasks: 最后 2 个 segment 的 Task 列表
            total_count: Task 总数（用于判断是否需要加载更多段）

        行为:
        1. model.set_task_list(tasks, offset = total_count - len(tasks))
        2. view.scrollToBottom()  # 默认展示最新记录
        3. 若 total_count > len(tasks) → 上面还有更多数据，滚动可见
        """
        ...

    def append_tasks(self, tasks: list[BaseTask]) -> None:
        """追加新 Task（向下滚动加载更晚 segment / 新建 Task 后）。"""
        self._model.append_tasks(tasks)

    def prepend_tasks(self, tasks: list[BaseTask]) -> None:
        """前置 Task（向上滚动加载更早 segment 后）。"""
        self._model.prepend_tasks(tasks)

    def add_task(self, task: BaseTask) -> None:
        """新增单条 Task（在末尾追加）。
        若排序代理正在排序 → 重置排序 → 追加 → 滚动到底部。
        """
        ...

    def update_task(self, global_index: int, task: BaseTask) -> None:
        """更新指定全局索引的 Task。"""
        row = global_index - self._model._offset - 1
        self._model.update_task(row, task)

    def remove_task(self, global_index: int) -> None:
        """删除指定全局索引的 Task。"""
        row = global_index - self._model._offset - 1
        self._model.remove_task(row)

    def filter_by_query(self, query: str) -> None:
        """委托排序代理的 setFilterFixedString(query) 过滤。
        空字符串 → 显示全部。
        """
        ...

    def clear_all(self) -> None:
        """清空表格（退出 Tasker 时）。"""
        self._model.set_task_list([], offset=0)

    @property
    def selected_task(self) -> tuple[int, BaseTask] | None:
        """当前选中行的 (global_index, task)。无选中返回 None。"""
        ...

    @property
    def row_count(self) -> int:
        """当前可见行数。"""
        ...

    # --- 内部滚动检测 ---

    def _on_scrollbar_value_changed(self, value: int) -> None:
        """滚动条值变更 → 检测是否触及边界。

        - value == minimum → 已到顶部，触发 more_data_needed(-1)
        - value == maximum → 已到底部，触发 more_data_needed(+1)

        防止重复触发: 用 self._loading_more 标记正在加载中。
        """
        ...

    # --- 键盘处理 ---

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """键盘事件处理。

        - Delete 键: 若当前有选中行 → 发射 task_delete_requested(global_index)
        - Enter 键: 若有选中行 → 发射 task_double_clicked(global_index, task) —— 打开编辑
        - 其他键 → 交给 QTableView 默认处理
        """
        ...

    # --- 样式 ---

    def _apply_styles(self) -> None:
        """应用表格样式。

        - 选中行背景: #E3F2FD
        - 交替行颜色: white / #FAFAFA
        - 网格线颜色: #E0E0E0
        - 表头: 粗体, 底边框 2px solid #BDBDBD
        """
        ...
```

---

## 4. TaskEditPanel — Task 创建/编辑面板

```python
from __future__ import annotations
from typing import Callable
from PySide6.QtWidgets import (
    QWidget, QFormLayout, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QPushButton, QLabel,
    QFrame, QSizePolicy,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeyEvent
from core.abstract import BaseTask
from core.types import PresetFields


class TaskEditPanel(QWidget):
    """Task 创建/编辑面板——表单布局，支持 Tab 导航和 Ctrl+Enter 提交。

    模式:
    - 创建模式: 空表单，标题 "新建记录"
    - 编辑模式: pre-populate 已有数据，标题 "编辑记录"

    字段:
    - date:      QLineEdit, placeholder="YYYY_MM_DD（留空=今天）"
    - attribute: QLineEdit, placeholder="属性/分类"
    - content:   QLineEdit, placeholder="内容"
    - comment:   QLineEdit, placeholder="注释（可选）"

    Tab 导航顺序: date → attribute → content → comment → submit button
    Ctrl+Enter: 在任意字段中按下 → 提交表单
    Escape: 取消/折叠面板（创建模式下清空，编辑模式下恢复原值）

    可折叠: 点击标题栏或按 Escape 可将面板折叠为仅标题行（展开/折叠动效）。
    """

    # --- 信号 ---
    task_submitted = Signal(dict)   # 用户提交表单，参数为字段 dict
    panel_cancelled = Signal()      # 用户取消/折叠面板

    def __init__(self, parent: QWidget | None = None) -> None:
        """初始化面板。

        步骤:
        1. 创建整体布局: title_bar + form_container（可折叠区）
        2. title_bar: QLabel("新建记录") + 折叠按钮
        3. form_container: QFormLayout
           - "日期:" → self._date_edit
           - "属性:" → self._attr_edit
           - "内容:" → self._content_edit
           - "注释:" → self._comment_edit
        4. 按钮行: QPushButton("提交") + QPushButton("取消")
        5. 设置 Tab 顺序
        6. 安装 eventFilter 到所有输入控件，拦截 Ctrl+Enter
        7. 初始状态: 折叠（只显示标题栏）
        """
        ...

    # --- 公共方法 ---

    def open_for_create(self, preset: PresetFields | None = None) -> None:
        """以创建模式展开面板。

        Args:
            preset: 快捷按钮预设字段（可选）。传入时预填对应字段，
                    如 {"attribute": "作业", "use_default_date": True}。
                    use_default_date=True 时 date 编辑框禁用并显示今天日期。

        行为:
        - 标题改为 "新建记录"
        - 清空所有字段
        - 若 preset 非空 → 预填
        - 展开表单 → date_edit.setFocus()
        """
        ...

    def open_for_edit(self, global_index: int, task: BaseTask) -> None:
        """以编辑模式展开面板。

        Args:
            global_index: Task 的全局索引（仅用于标题显示）
            task: 待编辑的 BaseTask 实例

        行为:
        - 标题改为 f"编辑记录 #{global_index}"
        - 各字段 pre-populate:
          - date: task.date
          - attribute: task.attribute（"N/A" → 显示为空）
          - content: task.content
          - comment: task.comment
        - 展开表单 → content_edit.setFocus()
        """
        ...

    def collapse(self) -> None:
        """折叠面板（仅显示标题栏）。"""
        ...

    def expand(self) -> None:
        """展开面板。"""
        ...

    @property
    def is_expanded(self) -> bool:
        """面板是否展开。"""
        ...

    @property
    def is_dirty(self) -> bool:
        """面板展开后字段是否被修改过。用于关闭前提示。"""
        ...

    def clear(self) -> None:
        """清空所有字段并折叠。"""
        ...

    # --- 内部 ---

    def _get_fields(self) -> dict:
        """收集表单字段为 dict。

        Returns:
            {"date": str, "attribute": str, "content": str, "comment": str}

        - date 为空时 → 取 today_str()
        - attribute 为空时 → "N/A"
        """
        ...

    def _validate_and_submit(self) -> None:
        """验证输入并提交。

        验证规则:
        - content 不能为空
        - date 非空时必须是 YYYY_MM_DD 格式
        - attribute 可为空（默认 N/A）

        验证失败 → 聚焦对应控件，不发射信号
        验证通过 → 发射 task_submitted(fields_dict) → 清空并折叠面板
        """
        ...

    def _on_submit_clicked(self) -> None:
        """提交按钮点击。"""
        ...

    def _on_cancel_clicked(self) -> None:
        """取消按钮点击 → 清空并折叠 → 发射 panel_cancelled。"""
        ...

    def _on_fold_toggle(self) -> None:
        """标题栏点击 → 切换折叠/展开。"""
        ...

    def _eventFilter(self, obj: QWidget, event: QKeyEvent) -> bool:
        """拦截 Ctrl+Enter → 触发 _validate_and_submit。"""
        ...

    def _build_ui(self) -> None:
        """构建完整布局。"""
        ...
```

---

## 5. InlineInputBar — 内联快捷输入

```python
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QComboBox, QPushButton,
    QFrame,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeyEvent


class InlineInputBar(QWidget):
    """嵌入 Tasker 视图底部的快捷创建输入栏。

    工作流（模拟旧项目的交互体验）:
    1. 用户在输入框输入 content
    2. 按 Tab → 焦点跳到 Tasker 选择下拉框（可键盘搜索选择）
    3. 按下拉框中的 Tasker 后 → 按 Enter → 创建 Task

    输入支持 "|||" 分隔符快速填充字段:
        "content|||attribute|||date" → 解析为对应字段
        "content|||attribute"       → date 取今天
        "content"                   → attribute 取 "N/A", date 取今天

    创建完成后:
    - 输入框清空
    - 下拉框保持最后选择的 Tasker（方便连续创建同 Tasker 的多条记录）
    - 若当前在目标 Tasker 界面内 → 更新表格
    - 若不在 → 不更新表格（Tasker 未加载）
    """

    # --- 信号 ---
    create_requested = Signal(str, dict)  # (tasker_id, fields_dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        """初始化内联输入栏。

        步骤:
        1. 创建水平布局:
           QLabel("快捷创建") | content_input | tasker_combo | create_button
        2. content_input (QLineEdit):
           - placeholder = "输入内容 (|||属性|||日期)"
        3. tasker_combo (QComboBox):
           - 可编辑、可搜索（setEditable(True)）
           - 从 taskers.json 加载所有 Tasker label
           - 每项存储 tasker_id 在 UserRole
        4. create_button (QPushButton):
           - 文本: "+"
           - 点击 → _parse_and_emit
        5. Tab 顺序: content_input → tasker_combo → create_button
        6. Enter 在 tasker_combo 中 → _parse_and_emit
        7. Enter 在 content_input 中 → 焦点跳到 tasker_combo
        """
        ...

    # --- 公共方法 ---

    def refresh_taskers(self, tasker_list: list[dict]) -> None:
        """刷新 Tasker 下拉框选项。

        Args:
            tasker_list: taskers.json 中的 Tasker 列表。
                         每个 dict 含 id, label。

        保持当前选中项（按 id 匹配），若原选中 Tasker 已删除 → 选中第一项。
        """
        ...

    def set_content(self, text: str) -> None:
        """外部设置输入框内容（如快捷按钮触发后回填 content）."""
        self._content_input.setText(text)
        self._content_input.setFocus()

    def clear(self) -> None:
        """清空输入框（创建成功后调用）。"""
        self._content_input.clear()

    @property
    def current_tasker_id(self) -> str | None:
        """当前选择的 Tasker id。"""
        ...

    # --- 内部 ---

    def _parse_and_emit(self) -> None:
        """解析输入并发射创建信号。

        解析逻辑:
        1. 获取 content_input 文本
        2. 按 "|||" 分割: parts = text.split("|||", maxsplit=2)
        3. len(parts) == 1 → content=parts[0], attribute="N/A", date=""(取今天)
        4. len(parts) == 2 → content=parts[0], attribute=parts[1], date=""
        5. len(parts) == 3 → content=parts[0], attribute=parts[1], date=parts[2]
        6. content 为空 → 不创建（忽略）
        7. 获取当前选择的 tasker_id
        8. 发射 create_requested(tasker_id, {"content": ..., "attribute": ..., "date": ...})

        MainController 收到后:
        - 若不在目标 Tasker 内 → enter_tasker(tasker_id) → task_service.create_task()
        - 若已在目标 Tasker 内 → 直接 task_service.create_task()
        """
        ...

    def _on_content_enter(self) -> None:
        """content_input 按 Enter → 焦点移到 tasker_combo。"""
        ...

    def _on_combo_enter(self) -> None:
        """tasker_combo 按 Enter → 触发 _parse_and_emit。"""
        ...

    def _build_ui(self) -> None:
        """构建布局。"""
        ...
```

---

## 6. TaskSearchBar — 实时搜索栏

```python
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import QTimer, Qt, Signal


class TaskSearchBar(QWidget):
    """带防抖的实时搜索栏。输入即搜，防抖 200ms。

    附加功能:
    - 左侧搜索图标 (QLabel, unicode "🔍" 或 QIcon)
    - 右侧 "×" 清除按钮（输入框非空时显示）
    - 匹配结果计数标签（如 "找到 12 条"）
    - Escape 键清空搜索
    """

    # --- 信号 ---
    search_changed = Signal(str)    # 搜索文本变化（经防抖），空字符串 = 清除搜索

    def __init__(self, parent: QWidget | None = None) -> None:
        """初始化搜索栏。

        步骤:
        1. 创建水平布局: search_icon | input | clear_btn | result_count_label
        2. input (QLineEdit):
           - placeholder = "搜索..."
           - 安装 eventFilter 拦截 Escape
        3. clear_btn (QPushButton):
           - 文本: "×"
           - 初始隐藏（input 为空时）
           - 点击 → 清空 input → 发射 search_changed("")
        4. result_count_label (QLabel):
           - 初始隐藏
           - 显示 "找到 N 条"
        5. 防抖 timer (QTimer):
           - singleShot, interval=200ms
           - input.textChanged → timer.start()
           - timer.timeout → 发射 search_changed(current_text)
           - 连续输入时 timer 自动重置（防抖效果）
        """
        ...

    # --- 公共方法 ---

    def set_result_count(self, count: int) -> None:
        """设置搜索结果计数标签。

        Args:
            count: 匹配的 Task 数量。-1 表示隐藏标签。
        """
        ...

    def clear(self) -> None:
        """清空搜索输入（外部调用）。不清除焦点。"""
        self._input.clear()

    def focus_search(self) -> None:
        """聚焦搜索框并全选文本（Ctrl+F 快捷键调用）。"""
        self._input.setFocus()
        self._input.selectAll()

    @property
    def current_query(self) -> str:
        """当前搜索文本。"""
        return self._input.text().strip()

    # --- 内部 ---

    def _on_text_changed(self, text: str) -> None:
        """输入文本变化 → 启动/重置防抖 timer。

        - 文本为空 → 立即发射 search_changed("")（无防抖），隐藏清除按钮
        - 文本非空 → 显示清除按钮，启动 200ms timer
        """
        ...

    def _on_timer_timeout(self) -> None:
        """防抖 timer 超时 → 发射 search_changed(current_query)。"""
        ...

    def _on_clear_clicked(self) -> None:
        """清除按钮点击 → 清空 + 发射 search_changed("") + input.setFocus()。"""
        ...

    def _on_escape(self) -> None:
        """Escape 键 → 清空搜索。"""
        ...
```

---

## 7. 信号流

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Task UI 信号流                                │
│                                                                      │
│  TaskSearchBar.search_changed(query)                                  │
│       │                                                              │
│       └──► TaskTableWidget.filter_by_query(query)                    │
│               → QSortFilterProxyModel.setFilterFixedString(query)     │
│               → TaskSearchBar.set_result_count(visible_rows)          │
│                                                                      │
│  TaskTableWidget.task_selected(global_index, task)                    │
│       │                                                              │
│       └──► MainController._on_task_selected(index, task)              │
│               → 更新 sidebar 搜索结果 / 指令状态                      │
│                                                                      │
│  TaskTableWidget.task_double_clicked(global_index, task)              │
│       │                                                              │
│       └──► TaskEditPanel.open_for_edit(global_index, task)           │
│               → 面板展开，用户编辑后提交                                │
│                                                                      │
│  TaskTableWidget.task_delete_requested(global_index)                  │
│       │                                                              │
│       └──► ConfirmDialog("确认删除此记录？")                           │
│               → 确认: task_service.delete_task(tasker_id, index)      │
│               → TaskTableWidget.remove_task(global_index)            │
│                                                                      │
│  TaskEditPanel.task_submitted(fields_dict)                            │
│       │                                                              │
│       ├── 创建模式: task_service.create_task(tasker_id, fields)       │
│       │               → TaskTableWidget.add_task(new_task)           │
│       │                                                              │
│       └── 编辑模式: task_service.update_task(tasker_id, idx, fields) │
│                       → TaskTableWidget.update_task(idx, new_task)   │
│                                                                      │
│  TaskEditPanel.panel_cancelled()                                      │
│       │                                                              │
│       └──► 面板折叠，丢弃修改                                         │
│                                                                      │
│  InlineInputBar.create_requested(tasker_id, fields)                   │
│       │                                                              │
│       └──► MainController._on_inline_create(tasker_id, fields)        │
│               → 若不在目标 Tasker → enter_tasker(tasker_id)           │
│               → task_service.create_task(tasker_id, fields)          │
│               → 若在当前 Tasker 界面 → TaskTableWidget.add_task()    │
│               → InlineInputBar.clear()                               │
│                                                                      │
│  TaskTableWidget.more_data_needed(direction)                          │
│       │                                                              │
│       ├── direction == -1 (向上/更早):                                 │
│       │   → task_service.get_tasks(tasker_id, offset=... , limit=500)│
│       │   → TaskTableWidget.prepend_tasks(new_tasks)                 │
│       │                                                              │
│       └── direction == +1 (向下/更晚):                                 │
│           → task_service.get_tasks(tasker_id, offset=... , limit=500)│
│           → TaskTableWidget.append_tasks(new_tasks)                  │
│                                                                      │
│  TaskTableWidget.all_data_needed()                                    │
│       │                                                              │
│       └──► task_service.get_tasks(tasker_id, limit=-1)  # 全量加载   │
│               → TaskTableWidget.load_initial_data(all_tasks, total)  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 8. 与 MainController 的集成

```python
# 在 MainController.enter_tasker(tasker_id) 中:

tasker = self._tasker_service.get_tasker(tasker_id)
if tasker is None:
    return

# 1. 创建/替换 TaskTableWidget
self._task_table = TaskTableWidget()
self._task_table.task_double_clicked.connect(self._on_edit_task)
self._task_table.task_delete_requested.connect(self._on_delete_task)
self._task_table.more_data_needed.connect(self._on_load_more)
self._task_table.all_data_needed.connect(self._on_load_all)

# 2. 初始加载（两段懒加载）
total_count = self._storage_manager.segment.get_total_count(tasker.folder)
tasks = self._tasker_service.get_tasks(tasker_id, offset=-500, limit=500)
self._task_table.load_initial_data(tasks, total_count)

# 3. 创建 TaskSearchBar 并连接
self._search_bar = TaskSearchBar()
self._search_bar.search_changed.connect(self._task_table.filter_by_query)

# 4. 创建 TaskEditPanel（初始折叠）
self._edit_panel = TaskEditPanel()
self._edit_panel.task_submitted.connect(
    lambda fields: self._on_task_form_submit(tasker_id, fields)
)

# 5. 创建 InlineInputBar
self._inline_bar = InlineInputBar()
self._inline_bar.refresh_taskers(self._tasker_service.list_taskers())
self._inline_bar.create_requested.connect(self._on_inline_create)

# 6. 组装 tasker_view 布局
# QVBoxLayout: search_bar → task_table → inline_bar → edit_panel
self._main_window.set_tasker_view_widget(tasker_view_widget)
self._main_window.switch_to_tasker_view(tasker_id)

# 7. 设置 commands_panel
self._main_window.set_commands(tasker.get_commands())
```

---

## 9. 依赖关系

```
ui/task/
├── task_table_model.py      # 依赖: PySide6, core/abstract.py (BaseTask)
├── task_table_widget.py     # 依赖: PySide6, core/abstract.py (BaseTask), .task_table_model
├── task_edit_panel.py       # 依赖: PySide6, core/abstract.py (BaseTask), core/types.py (PresetFields)
├── inline_input_bar.py      # 依赖: PySide6
├── task_search_bar.py       # 依赖: PySide6
└── __init__.py
```

本包不直接导入 core 服务接口——数据通过信号传递，由 MainController 桥接 UI 和服务层。

---

## 10. 注意事项

1. **QSortFilterProxyModel 与 index 列**：排序代理改变了行在视图中出现的顺序。index 列的值为全局序号（`self._offset + source_row + 1`），它表达了数据顺序而非排序后的视觉顺序。在 data() 方法中计算而非存储，保证切换排序后序号不变。

2. **分段加载的视图稳定性**：向上加载更早 segment 后 prepend 数据，视图的滚动位置需要补偿偏移量（`QTableView.verticalScrollBar().setValue(old_max - new_max + old_value)`），防止视图跳动。

3. **防抖 timer 生命周期**：TaskSearchBar 使用 `QTimer.singleShot`，每次文本变化时停止前一个 timer 并启动新的。组件销毁时无需手动清理（Qt 父子关系自动处置）。

4. **"|||" 分隔符**：InlineInputBar 的 "|||" 解析语法继承自旧 CLI 项目。分隔符在 content 中的字面使用不受支持（与旧项目的 BLOCK_LIST 限制一致）。如需在 content 中使用 "|||"，需通过 TaskEditPanel 完整表单输入。

5. **Tab 导航策略**：TaskEditPanel 中各字段的 tabOrder 为 date → attribute → content → comment。date 为只读或不常用时可跳过（通过 setTabOrder 控制）。Ctrl+Enter 作为全局提交快捷键，通过 eventFilter 安装到所有输入控件。

6. **编辑模式下的并发安全**：若用户在 TaskEditPanel 编辑某条 Task 时，快捷按钮或 InlineInputBar 触发了对同 Tasker 的新建操作，新建操作照常进行并更新表格视图。编辑面板的数据是 Task 对象的快照引用——若该 Task 在外部被删除后用户尝试提交编辑，task_service.update_task() 应返回 None 或抛异常，UI 层捕获后显示错误提示并折叠面板。

7. **性能和行数上限**：每个 segment 最多 500 条，两段懒加载初始最多 ~1000 条。QTableView 的 model/view 架构天然支持大数据量（只渲染可见行）。但若触发全量加载（所有 segment 加载到内存），对于大型 Tasker（如 10k+ 条），考虑设置全量加载警告或用 QProgressDialog 显示进度。

8. **列宽策略**：date 和 attribute 固定宽度防止频繁 resize。content 和 comment 按比例分配剩余空间（Stretch）。用户手动拖拽列宽后宽度存储在 AppConfig 中，下次进入 Tasker 时恢复。
