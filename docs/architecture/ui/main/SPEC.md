# SPEC: ui/main — 主窗口 UI 层

> 对应源码路径: `src/ui/main/`
> 负责主窗口的三区布局、系统托盘、UI 状态机控制。使用 PySide6。

---

## 1. 布局概览

```
MainWindow (QMainWindow)
├── central_widget (QWidget)
│   └── QHBoxLayout
│       ├── main_area (QVBoxLayout)
│       │   ├── content_area (QWidget)     —— 内容显示区（状态机切换）
│       │   ├── output_area (QTextEdit)    —— 系统输出区（实时 log）
│       │   └── input_box (QTextEdit)      —— 多行输入框（折行不插换行符）
│       └── sidebar (QWidget)
│           └── QVBoxLayout
│               ├── commands_panel (QWidget)   —— 可用指令列表（可点击）
│               ├── quick_buttons_panel (QWidget) —— 快捷按钮
│               └── search_results (QTableWidget) —— 搜索结果表格
```

### 组件职责速查

| 组件 | 类型 | 职责 |
|------|------|------|
| `content_area` | `QStackedWidget` | 管理三种界面视图的切换：main_view / tasker_view / settings_view |
| `output_area` | `QPlainTextEdit` | 只读，追加 log 行。前端 append + auto-scroll，不参与数据模型 |
| `input_box` | `QPlainTextEdit` | 多行显示，`wrapMode = WidgetWidth`，回车提交时不插入换行符 |
| `commands_panel` | `QWidget` + `QVBoxLayout` | 动态生成 QPushButton 列表，点击 → 填入 input_box 并提交 |
| `quick_buttons_panel` | `QWidget` + `QVBoxLayout` | 动态生成快捷按钮，标注所属 Tasker |
| `search_results` | `QTableWidget` | 仅 Tasker 界面内可见，搜索结果表格 |

---

## 2. MainWindow — 主窗口

```python
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPlainTextEdit, QTableWidget,
    QPushButton, QSplitter, QLabel, QFrame,
)
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QCloseEvent, QPaintEvent, QPainter, QFont, QColor


class MainWindow(QMainWindow):
    """主窗口——统一三区布局 + 右侧常驻区。

    生命周期:
        - __init__ → 构建布局 → 连接 MainController → show()
        - 关闭事件 → hide() 到托盘（不退出）
        - 销毁 → 仅 SystemTray.exit() 或输入 "exit" 触发
    """

    # --- 信号 ---
    input_submitted = Signal(str)       # 用户回车提交输入文本
    window_hidden = Signal()            # 窗口隐藏到托盘（触发 auto-save）
    window_shown = Signal()             # 窗口从托盘恢复

    def __init__(self, parent: QWidget | None = None) -> None:
        """初始化主窗口。

        步骤:
        1. 读取保存的窗口几何（位置 + 大小），若无则使用默认值
        2. 调用 _setup_window_flags() 去除 × 按钮
        3. 调用 _build_layout() 构建三区布局
        4. 连接 input_box.returnPressed → _on_input_submit
        5. 安装 closeEvent 处理器 → 最小化到托盘
        """
        ...

    # --- 窗口标志 ---

    def _setup_window_flags(self) -> None:
        """去除窗口右上角 × 按钮。

        实现:
        - setWindowFlags() 覆盖默认标志
        - 保留: 最小化按钮、标题栏、系统菜单
        - 移除: 关闭按钮 (WindowCloseButtonHint)
        - 同时需要处理 Alt+F4 → 同 closeEvent 逻辑
        
        注意: 不同平台/桌面环境的行为可能不同；
        Windows 11 上 setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint) 可达到去除 × 的效果。
        """
        ...

    def changeEvent(self, event: QEvent) -> None:
        """窗口状态变更事件。当窗口被最小化时不做特殊处理（不在此处隐藏到托盘）。
        仅在用户主动关闭（closeEvent）时 hide 到托盘。
        """
        ...

    def closeEvent(self, event: QCloseEvent) -> None:
        """关闭事件 → 隐藏到托盘。

        行为:
        1. event.ignore() 阻止默认关闭
        2. self.hide() 隐藏窗口（系统托盘仍可见）
        3. 发射 window_hidden 信号 → MainController 收到后触发 auto-save
        """
        ...

    # --- 布局构建 ---

    def _build_layout(self) -> None:
        """构建三区 + 右侧常驻区布局。

        结构:
            QSplitter(Qt.Horizontal) [主区域 | 右侧常驻区]
              主区域: QVBoxLayout [content_area | output_area | input_box]
              右侧常驻区: QVBoxLayout [commands_panel | quick_buttons_panel | search_results]

        QSplitter 允许用户拖动调整右侧常驻区宽度。
        比例默认: 主区域 75% / 右侧 25%。
        """
        ...

    def _build_content_area(self) -> QStackedWidget:
        """构建内容显示区（QStackedWidget）。

        包含三个页面:
        0: main_view   —— 主界面（WatermarkWidget + TaskerListWidget）
        1: tasker_view —— Tasker 界面（TaskTableWidget）
        2: settings_view —— 设置界面（SettingsPanel）

        Returns:
            配置好的 QStackedWidget
        """
        ...

    def _build_main_view(self) -> QWidget:
        """构建主界面视图（页面 0）。

        层次（下→上）:
        1. WatermarkWidget (QWidget, 半透明): GitHub / 作者 / 版本号
        2. TaskerListWidget (QWidget): 可点击 Tasker 列表

        使用 QStackedLayout 或直接 QLabel 作为背景层，
        前景层是透明的 TaskerListWidget 叠加在其上。
        """
        ...

    def _build_output_area(self) -> QPlainTextEdit:
        """构建系统输出区。

        - 只读
        - 等宽字体 (Consolas / monospace, 10pt)
        - scrollbar 自动跟随（追加 log 时 scroll to bottom）
        - 最大行数限制（如 500 行，超出时移除最早行）
        """
        ...

    def _build_input_box(self) -> QPlainTextEdit:
        """构建多行输入框。

        行为:
        - wrapMode: QPlainTextEdit.WidgetWidth（折行显示但不插入 \n）
        - 用户按 Enter 时:
            1. 获取 toPlainText() 全文
            2. 发射 input_submitted 信号
            3. clear() 清空输入框
        - Shift+Enter 不提交——此行为通过 installEventFilter 或重写 keyPressEvent 实现
        - 历史记录: 上/下方向键回溯历史输入（存储最近 50 条）
        """
        ...

    def _build_sidebar(self) -> QWidget:
        """构建右侧常驻区。

        从上到下:
        1. commands_label (QLabel: "可用指令")
        2. commands_panel (QWidget + QVBoxLayout)
        3. separator_line (QFrame, HLine)
        4. quick_buttons_label (QLabel: "快捷按钮")
        5. quick_buttons_panel (QWidget + QVBoxLayout)
        6. separator_line
        7. search_results_label (QLabel: "搜索结果")
        8. search_results (QTableWidget)
        """
        ...

    # --- 输入处理 ---

    def _on_input_submit(self) -> None:
        """用户按 Enter 提交输入。

        1. 从 input_box 获取文本
        2. 存入历史记录
        3. 清空 input_box
        4. 发射 input_submitted 信号 → MainController.preprocess_and_dispatch()
        """
        ...

    def set_input_text(self, text: str) -> None:
        """外部设置输入框内容（如点击常驻区指令按钮时）。"""
        ...

    def append_history(self, text: str) -> None:
        """追加到输入历史。最多保留 50 条。"""
        ...

    # --- 界面状态切换 ---

    def switch_to_main_view(self) -> None:
        """切换到主界面视图 (stacked index 0)。
        背景水印可见，TaskerListWidget 刷新列表。
        """
        ...

    def switch_to_tasker_view(self, tasker_id: str) -> None:
        """切换到 Tasker 界面视图 (stacked index 1)。
        启动两段懒加载，TaskTableWidget 显示最近 N 条记录。
        """
        ...

    def switch_to_settings_view(self) -> None:
        """切换到设置界面视图 (stacked index 2)。
        加载当前配置项。
        """
        ...

    @property
    def current_view(self) -> str:
        """返回当前界面名称: "main" | "tasker" | "settings" """
        ...

    # --- 系统输出 ---

    def log(self, message: str, level: str = "info") -> None:
        """追加一行到 output_area。

        Args:
            message: 日志文本
            level: "info" (默认灰), "warn" (橙), "error" (红)
        """
        ...

    def clear_log(self) -> None:
        """清空输出区。"""
        ...

    # --- 常驻区管理 ---

    def set_commands(self, commands: list[str]) -> None:
        """设置常驻区可用指令列表。

        每个 command 名字生成一个 QPushButton。
        点击 → 填入 input_box 并提交。

        Args:
            commands: 指令名列表（如 ["new", "search", "delete", "edit"]）
        """
        ...

    def set_quick_buttons(
        self, buttons: list[dict]
    ) -> None:
        """设置常驻区快捷按钮。

        Args:
            buttons: [{tasker_label, tasker_id, command, label, preset}, ...]
                     按 usage_count 降序排列

        每个按钮显示 label 并标注所属 Tasker。
        点击 → MainController.handle_quick_button(button_dict)
        """
        ...

    def set_search_results(
        self, headers: list[str], rows: list[list[str]]
    ) -> None:
        """设置搜索结果表格。

        Args:
            headers: 列标题（如 ["索引", "日期", "属性", "内容"]）
            rows: 数据行
        """
        ...

    def clear_search_results(self) -> None:
        """清空搜索结果（退出 Tasker 时调用）。"""
        ...

    # --- 窗口显示控制 ---

    def show_and_raise(self) -> None:
        """从托盘恢复窗口: show() + raise_() + activateWindow() + 聚焦 input_box。"""
        ...

    def minimize_to_tray(self) -> None:
        """隐藏窗口到托盘。等价 self.hide()。"""
        ...

    def save_window_state(self) -> None:
        """保存窗口几何（位置 + 大小）到 AppConfig。"""
        ...

    def restore_window_state(self) -> None:
        """从 AppConfig 恢复窗口几何。"""
        ...
```

---

## 3. WatermarkWidget — 水印背景

```python
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QFont, QColor, QPaintEvent


class WatermarkWidget(QWidget):
    """半透明水印背景组件。用于主界面的内容显示区底部。

    显示内容:
    1. 软件名称（大字，居中偏上）
    2. 作者名
    3. GitHub 仓库链接
    4. 版本号
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """初始化水印。读取软件元信息（名称、版本、作者、GitHub 链接）。"""
        ...

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制半透明水印。

        绘制顺序（下→上）:
        1. 软件名称: 大字 (36pt), 粗体, 灰色 rgba(128,128,128, 40)
        2. 作者名:   (14pt), 灰色 rgba(128,128,128, 30)
        3. GitHub 链接: (12pt), 灰色 rgba(128,128,128, 25)
        4. 版本号:   (12pt), 灰色 rgba(128,128,128, 25)
        """
        ...

    @property
    def app_name(self) -> str: ...
    @property
    def app_version(self) -> str: ...
    @property
    def app_author(self) -> str: ...
    @property
    def app_github(self) -> str: ...
```

---

## 4. SystemTray — 系统托盘

```python
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction


class SystemTray(QSystemTrayIcon):
    """系统托盘图标。

    生命周期跟随应用全程——应用启动时创建，退出时销毁。
    """

    # --- 信号 ---
    show_window_requested = Signal()    # 右键菜单"显示窗口"
    new_record_requested = Signal()     # 右键菜单"新建记录"（快速新建）
    exit_requested = Signal()           # 右键菜单"退出"

    def __init__(self, parent: QWidget | None = None) -> None:
        """初始化系统托盘。

        1. 设置图标（应用 icon）
        2. 构建右键菜单 (_build_context_menu)
        3. 连接 activated 信号（左键双击 → show_window）
        """
        ...

    def _build_context_menu(self) -> QMenu:
        """构建右键菜单。

        项目（从上到下）:
        - "显示窗口"    → show_window_requested
        - "新建记录"    → new_record_requested
        - separator
        - "退出"        → exit_requested
        """
        ...

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """托盘图标激活事件。左键双击 → 显示窗口。"""
        ...

    def show_tray_message(
        self, title: str, message: str, icon_type: int = QSystemTrayIcon.Information
    ) -> None:
        """显示托盘气泡提示（如"已保存""计时进行中"）。"""
        ...
```

---

## 5. MainController — 主控制器（UI 状态机）

```python
from typing import TYPE_CHECKING
from core.input_processor import InputPreprocessor

if TYPE_CHECKING:
    from core.base_service import BaseTaskerService, BaseTaskService
    from config.app_config import AppConfig


class MainController:
    """主控制器——管理 UI 状态转换，连接输入预处理链，委托到服务层。

    生命周期为单例，由 main.py 创建后持有。
    窗口关闭不等于销毁——控制器生命周期与托盘相同。
    """

    # 界面状态枚举
    class UIState:
        MAIN = "main"
        TASKER = "tasker"
        SETTINGS = "settings"
        CHART = "chart"

    def __init__(
        self,
        main_window: 'MainWindow',
        system_tray: 'SystemTray',
        tasker_service: 'BaseTaskerService',
        task_service: 'BaseTaskService',
        app_config: 'AppConfig',
    ) -> None:
        """初始化控制器。

        Args:
            main_window: 主窗口实例
            system_tray: 系统托盘实例
            tasker_service: Tasker 管理服务
            task_service: Task CRUD 服务
            app_config: 应用配置

        步骤:
        1. 保存依赖引用
        2. 连接信号:
           - main_window.input_submitted → self.preprocess_and_dispatch
           - main_window.window_hidden → self._on_window_hidden
           - system_tray.show_window_requested → self.show_window
           - system_tray.new_record_requested → self._on_new_record
           - system_tray.exit_requested → self.exit_app
        3. 初始化状态: state=MAIN
        """
        ...

    # --- 输入预处理 + 分发 ---

    def preprocess_and_dispatch(self, raw_input: str) -> None:
        """预处理输入并分发到对应的处理器。

        流程:
        1. 去除首尾空白
        2. 空输入 → 忽略
        3. 经过 InputPreprocessor.process(raw) 预处理链
        4. 分发:
           - "exit" → 如果当前在 Tasker 内 → _exit_tasker()
                     如果在 settings 内 → _exit_settings()
                     如果在主界面 → exit_app()
           - "hide" → 隐藏窗口
           - "/" 前缀 → 强制识别为指令 → _dispatch_command()
           - 数字 → 按索引操作（仅在 Tasker 界面内有效）
           - 其他 → _dispatch_ambiguous()（先尝试匹配指令，再尝试匹配 Tasker 名）
        """
        ...

    def _dispatch_command(self, command_line: str) -> None:
        """解析并执行指令。

        主界面下的指令:
        - /get <name> / <name> → enter_tasker(name_or_id)
        - /add → open_create_tasker_dialog()
        - /edit <name> → open_edit_tasker_dialog(name)
        - /delete <name> → confirm_delete_tasker(name)
        - /info <name> → show_tasker_info(name)
        - /sort <field> → sort_tasker_list(field)
        - /settings / settings → enter_settings()
        - backup → backup_all()
        - reload → reload_from_backup()

        Tasker 界面下的指令:
        - 由当前 Tasker 的 get_commands() 列表中的指令名
        - new / search / delete / edit / backup / reload 等
        - 委托给当前激活的 Tasker 对象处理
        """
        ...

    def _dispatch_ambiguous(self, text: str) -> None:
        """歧义分发——先尝试匹配全局指令，再尝试 Tasker 名称/索引匹配。

        主界面: 输入文本尝试精确匹配某个 Tasker 的 label → 进入该 Tasker
        Tasker 界面: 输入文本尝试匹配该 Tasker 的指令 → 执行指令
        """
        ...

    # --- 界面状态管理 ---

    @property
    def current_state(self) -> str: ...

    @property
    def current_tasker_id(self) -> str | None:
        """当前进入的 Tasker id。主界面/设置界面下为 None。"""
        ...

    def enter_tasker(self, tasker_id_or_label: str) -> None:
        """进入 Tasker 界面。

        流程:
        1. 查找 tasker（支持 id 或 label 匹配）
        2. 调用 tasker_service.get_tasker(tasker_id) → 两段懒加载
        3. main_window.switch_to_tasker_view(tasker_id)
        4. 设置常驻区指令列表 = tasker.get_commands()
        5. 设置常驻区快捷按钮 = 该 Tasker 的 quick_buttons
        6. state → TASKER
        """
        ...

    def _exit_tasker(self) -> None:
        """退出 Tasker 回到主界面。

        流程:
        1. 触发 auto-save（保存当前 Tasker 中 dirty 的 segment）
        2. 释放当前 Tasker 内存中加载的 segment 数据
        3. main_window.switch_to_main_view()
        4. 设置常驻区指令列表 = 全局指令
        5. 设置常驻区快捷按钮 = 所有 Tasker 的按钮汇总
        6. 清空搜索结果
        7. state → MAIN
        """
        ...

    def enter_settings(self) -> None:
        """进入设置界面。

        流程:
        1. 加载 app_config 当前配置项
        2. main_window.switch_to_settings_view()
        3. 常驻区指令列表清空（设置界面不需要指令）
        4. state → SETTINGS
        """
        ...

    def _exit_settings(self) -> None:
        """退出设置界面回到主界面。

        流程:
        1. 验证所有配置项的输入合法性
           - 不合法的项保留修改前的值（不更新）
        2. 保存配置到 config JSON
        3. main_window.switch_to_main_view()
        4. state → MAIN
        """
        ...

    def enter_chart_mode(self, chart_type: str) -> None:
        """进入图表模式（启动 HTTP 服务 + 打开浏览器）。

        流程:
        1. 启动本地 HTTP 服务 (127.0.0.1:{port})
        2. 处理图表初始数据
        3. webbrowser.open() 打开浏览器
        4. state → CHART
        5. 输入框保持可用——用户可继续 CRUD

        图表模式下输入 exit → 停止 HTTP 服务 → 释放端口 → state → MAIN
        """
        ...

    def exit_chart_mode(self) -> None:
        """退出图表模式。停止 HTTP 服务，释放端口。"""
        ...

    # --- 窗口控制 ---

    def show_window(self) -> None:
        """从托盘恢复窗口。"""
        ...

    def hide_window(self) -> None:
        """隐藏窗口到托盘。"""
        ...

    def _on_window_hidden(self) -> None:
        """窗口隐藏到托盘的回调。触发 auto-save。"""
        ...

    def exit_app(self) -> None:
        """退出应用。

        流程:
        1. 强制 flush_save() 立即保存所有待写数据
        2. 释放所有已加载的 Tasker
        3. 停止 HTTP 服务（如果在运行）
        4. 保存窗口状态
        5. QApplication.quit()
        """
        ...

    # --- 快捷按钮 ---

    def handle_quick_button(self, button_def: dict) -> None:
        """处理快捷按钮点击。

        Args:
            button_def: {
                "tasker_id": str,
                "command": str,
                "label": str,
                "preset": PresetFields,
            }

        流程:
        1. 如果不在该 Tasker 的界面内 → 先 enter_tasker(tasker_id)
        2. 调用 tasker.execute_quick_button(button_def)
        3. 如果返回 None（content 为空）→ 弹出输入对话框让用户补充
        4. 否则 → task_service.create_task() → 更新表格视图
        """
        ...

    # --- Tasker 管理（从主界面触发） ---

    def open_create_tasker_dialog(self) -> None:
        """打开"创建 Tasker"对话框。
        收集: type, label, description → tasker_service.create_tasker()
        """
        ...

    def open_edit_tasker_dialog(self, tasker_id_or_label: str) -> None:
        """打开"编辑 Tasker"对话框。"""
        ...

    def confirm_delete_tasker(self, tasker_id_or_label: str) -> None:
        """弹出确认 → tasker_service.delete_tasker()。"""
        ...

    def show_tasker_info(self, tasker_id_or_label: str) -> None:
        """在 output_area 打印 Tasker 详细信息。"""
        ...

    def sort_tasker_list(self, field: str) -> None:
        """重排 Tasker 列表并保存到 taskers.json。"""
        ...

    # --- 备份 ---

    def backup_all(self) -> None:
        """遍历所有 Tasker 全量读取 → 写入备份文件夹。"""
        ...

    def reload_from_backup(self) -> None:
        """选择备份文件夹 → 检查 taskers.json → 读取对比 → 确认替换。"""
        ...
```

---

## 6. InputHistory — 输入历史管理

```python
class InputHistory:
    """输入历史——支持上/下方向键回溯。

    属于 MainWindow 内部组件，不单独暴露。
    """

    def __init__(self, max_size: int = 50) -> None:
        self._history: list[str] = []
        self._cursor: int = -1  # -1 = 当前输入行（不在历史中）
        self._max_size = max_size

    def append(self, text: str) -> None:
        """追加到历史。相同文本不重复追加。满 max_size 时移除最早条目。"""
        ...

    def navigate_up(self) -> str | None:
        """返回上一条历史。cursor 到达顶部后不再移动。"""
        ...

    def navigate_down(self) -> str | None:
        """返回下一条历史。cursor 到达底部（-1）时返回空字符串。"""
        ...

    def reset_cursor(self) -> None:
        """重置游标到当前输入（提交后）。"""
        ...
```

---

## 7. 依赖关系

```
ui/main/
├── main_window.py          # 依赖: PySide6, config.AppConfig, core.types
├── watermark_widget.py      # 依赖: PySide6 (独立)
├── system_tray.py           # 依赖: PySide6 (独立)
├── main_controller.py       # 依赖: core.base_service, core.input_processor, config.AppConfig, main_window, system_tray
├── input_history.py         # 依赖: 无 (纯 Python)
└── __init__.py
```

## 8. 信号流

```
┌─────────────────────────────────────────────────────────────────┐
│                          信号流图                                │
│                                                                 │
│  input_box.returnPressed                                        │
│       │                                                         │
│       v                                                         │
│  MainWindow.input_submitted(text)                               │
│       │                                                         │
│       v                                                         │
│  MainController.preprocess_and_dispatch(text)                   │
│       │                                                         │
│       ├── "exit" ──────────► _exit_tasker() / exit_app()        │
│       ├── "hide" ──────────► hide_window()                      │
│       ├── "/cmd" ──────────► _dispatch_command()                │
│       └── 其他 ────────────► _dispatch_ambiguous()               │
│                                                                 │
│  system_tray.show_window_requested                              │
│       │                                                         │
│       v                                                         │
│  MainController.show_window() → MainWindow.show_and_raise()     │
│                                                                 │
│  system_tray.exit_requested                                     │
│       │                                                         │
│       v                                                         │
│  MainController.exit_app() → QApplication.quit()                │
│                                                                 │
│  main_window.window_hidden                                      │
│       │                                                         │
│       v                                                         │
│  MainController._on_window_hidden() → auto_save                 │
│                                                                 │
│  快捷按钮 click                                                 │
│       │                                                         │
│       v                                                         │
│  MainController.handle_quick_button(button_def)                 │
│       │                                                         │
│       ├── 不在对应 Tasker → enter_tasker()                      │
│       └── tasker.execute_quick_button() → task_service.create() │
│                                                                 │
│  指令按钮 click (commands_panel)                                │
│       │                                                         │
│       v                                                         │
│  MainWindow.set_input_text(cmd) → input_submitted(cmd)          │
└─────────────────────────────────────────────────────────────────┘
```

## 9. 注意事项

1. **PySide6 移除 × 按钮**：Windows 11 下 `setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.CustomizeWindowHint)` 可达到效果。某些桌面管理器可能不完全支持，需要平台相关的 fallback。

2. **输入框 Enter 行为**：`QPlainTextEdit` 默认 Enter 插入换行符。需重写 `keyPressEvent` 或安装 `eventFilter` 拦截单次 Enter。Shift+Enter 保留换行行为。

3. **托盘图标**：需提供 `.ico` 文件。Windows 上建议 16x16 + 32x32 + 48x48 多尺寸。托盘气泡提示在某些 Windows 版本上可能被系统静默。

4. **水印 overlay**：实现方式为在 `main_view` 的 QStackedLayout 中，先加入 WatermarkWidget，再加入透明的 TaskerListWidget。后者设置 `setAttribute(Qt.WA_TranslucentBackground)` 或使用 stylesheet 背景透明。

5. **QStackedWidget 切换**：切换时不需要销毁旧视图——保持 widget 实例存活，数据由 MainController 在切换时刷新。

6. **线程安全**：所有 UI 操作必须在主线程执行。MainController 的方法由 UI 信号链触发，天然在主线程。HTTP 服务的回调如需更新 UI，用 `QMetaObject.invokeMethod` 或信号。

7. **auto-save 时机**：MainController 在以下时机触发 `storage_manager.flush_save()`：
   - `_on_window_hidden()` 收到 window_hidden 信号
   - `_exit_tasker()` 退出 Tasker
   - `_exit_settings()` 退出设置界面
