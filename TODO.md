# TODO — Task 2.0 开发总路线图

> 本文档制定全项目的开发顺序与阶段性测试计划。每个阶段完成后通过对应测试验证，再进入下一阶段。

## 编写策略

**不是一次性完成一个模块的所有代码**。每个阶段完成到可测试的程度即止，测试通过后再进入下一阶段。阶段之间按依赖关系排序——`core` 模型先于存储层，存储层先于服务层，服务层先于 GUI。

## 阶段 0：项目骨架与依赖安装

**目标**：创建 `src/` 目录结构，安装依赖，确认开发环境可用。

- [x] `src/requirements.txt` — 列出 pyside6, pyperclip, pynput, pytest
- [x] `pip install -r src/requirements.txt`
- [x] 创建所有空 `__init__.py`
  - [x] `src/core/__init__.py`
  - [x] `src/core/storage/__init__.py`
  - [x] `src/core/service/__init__.py`
  - [x] `src/extensions/default/__init__.py`
  - [x] `src/extensions/timer/__init__.py`
  - [x] `src/extensions/account/__init__.py`
  - [x] `src/extensions/quick_button/__init__.py`
  - [x] `src/extensions/label/__init__.py`
  - [x] `src/ui/__init__.py`
  - [x] `src/ui/main/__init__.py`
  - [x] `src/ui/tasker/__init__.py`
  - [x] `src/ui/task/__init__.py`
  - [x] `src/ui/chart/__init__.py`
  - [x] `src/ui/component/__init__.py`
  - [x] `src/analysis/__init__.py`
  - [x] `src/visualization/__init__.py`
  - [x] `src/io/__init__.py`
  - [x] `src/config/__init__.py`
  - [x] `src/util/__init__.py`
- [x] 创建空的测试目录 `src/tests/`

**测试**：✅ 20/20 子包全部成功导入。`from core import BaseTask` 预期失败（BaseTask 尚未定义，阶段 1 实现）。

## 阶段 1：core 抽象层（无外部依赖）

**目标**：定义所有抽象基类和类型——这些是系统中所有其他模块的语言。此阶段不需要存储、不需要 GUI。

- [x] `src/util/date_utils.py` — `today_str()`, `now_str()`, `parse_date()`, `is_valid_date()`, `format_duration()`
  - 参考：`docs/architecture/util/SPEC.md`
- [x] `src/core/types.py` — `TaskerSummary`, `QuickButtonDef`, `PresetFields`, `SearchQuery`, `AnalysisParams` TypedDict
  - 参考：`docs/architecture/core/SPEC.md` §4
- [x] `src/core/abstract.py` — `BaseTask`, `BaseTasker`, `BaseAnalyzer` 三个抽象基类
  - 参考：`docs/architecture/core/SPEC.md` §1
- [x] `src/core/extension_registry.py` — `ExtensionRegistry` 注册表单例
  - 参考：`docs/architecture/core/SPEC.md` §2
- [x] `src/core/input_processor.py` — `InputPreprocessor` + `step_plus_to_search`
  - 参考：`docs/architecture/core/SPEC.md` §5
- [x] `src/core/base_service.py` — `BaseTaskerService`, `BaseTaskService`
  - 参考：`docs/architecture/core/SPEC.md` §3

**测试**：✅ `src/tests/test_phase1.py` — 8/8 全部通过（submodule imports, date_utils, InputPreprocessor, ExtensionRegistry, BaseTasker 具体子类, QuickButtonDef, execute_quick_button）

## 阶段 2：工具层 + 配置层

**目标**：完成 util 和 config——这两个包是存储层的依赖。不需要 GUI。

- [x] `src/util/json_utils.py` — `load_json(path)`, `save_json(path, data, atomic=True)`
  - 参考：`docs/architecture/util/SPEC.md`
- [x] `src/util/file_utils.py` — `atomic_write()`, `safe_join()`, `ensure_dir()`
  - 参考：`docs/architecture/util/SPEC.md`
- [x] `src/util/string_utils.py` — `parse_semicolon_content()`, `extract_key_value()`
  - 参考：`docs/architecture/util/SPEC.md`
- [x] `src/util/clipboard_utils.py` — `copy_to_clipboard()`, `get_clipboard_text()`
  - 参考：`docs/architecture/util/SPEC.md`
- [x] `src/config/config_store.py` — `ConfigStore` 读写 config.json
  - 参考：`docs/architecture/config/SPEC.md`
- [x] `src/config/app_config.py` — `AppConfig` 单例，默认值定义
  - 参考：`docs/architecture/config/SPEC.md`

**测试**：✅ `src/tests/test_phase2.py` — 7/7 全部通过（JsonUtils 顺序保持+原子写入, FileUtils 目录创建+路径安全, StringUtils 分隔+键值提取+引用提取, ConfigStore 默认值+合并+保存, AppConfig 单例初始化+更新, date_utils 回归）

## 阶段 3：存储层

**目标**：核心读写逻辑。此阶段完成后可以读写 taskers.json 和 segment 文件。

- [x] `src/core/storage/tasker_index_manager.py` — `TaskerIndexManager`
  - 参考：`docs/architecture/core/storage/SPEC.md` §2
- [x] `src/core/storage/segment_manager.py` — `SegmentManager`（含两段懒加载 + 脏写 + 原子写入）
  - 参考：`docs/architecture/core/storage/SPEC.md` §3
- [x] `src/core/storage/auto_save_manager.py` — `AutoSaveManager`（防抖调度）
  - 参考：`docs/architecture/core/storage/SPEC.md` §4
- [x] `src/core/storage/index_builder.py` — `IndexBuilder`
  - 参考：`docs/architecture/core/storage/SPEC.md` §5
- [x] `src/core/storage/storage_manager.py` — `StorageManager`（门面）
  - 参考：`docs/architecture/core/storage/SPEC.md` §1

**测试**：✅ `src/tests/test_phase3.py` — 13/13 全部通过（TaskerIndex 顺序保持, Segment 两段懒加载+全量加载, 脏段写回+净段跳过, 扩容到4段, 缩容到1段, AutoSave 防抖+取消, IndexBuilder 重建, StorageManager 门面+备份+reload）

## 阶段 4：扩展模块注册 + 默认服务

**目标**：完成 default/timer/account/label 扩展模块的 Task 和 Tasker 实现，以及默认服务。注册到 ExtensionRegistry 后，基本的数据结构已就绪。

- [ ] `src/extensions/default/default_task.py` + `default_tasker.py` + `__init__.py`
  - 参考：`docs/architecture/extensions/default/SPEC.md`
- [ ] `src/extensions/timer/timer_task.py` + `timer_tasker.py` + `duration_calculator.py` + `__init__.py`
  - 参考：`docs/architecture/extensions/timer/SPEC.md`
- [ ] `src/extensions/account/account_task.py` + `account_tasker.py` + `password_clipboard.py` + `__init__.py`
  - 参考：`docs/architecture/extensions/account/SPEC.md`
- [ ] `src/extensions/label/label_task.py` + `label_tasker.py` + `__init__.py`
  - 参考：`docs/architecture/extensions/label/SPEC.md`
- [ ] `src/extensions/quick_button/quick_button_service.py` + `__init__.py`
  - 参考：`docs/architecture/extensions/quick_button/SPEC.md`
- [ ] `src/core/service/default_tasker_service.py` — 依赖 StorageManager + ExtensionRegistry
  - 参考：`docs/architecture/core/service/SPEC.md` §1
- [ ] `src/core/service/default_task_service.py`
  - 参考：`docs/architecture/core/service/SPEC.md` §2
- [ ] `src/core/service/search_engine.py`
  - 参考：`docs/architecture/core/service/SPEC.md` §3

**测试**：
1. 注册后 `ExtensionRegistry.create_task("default", ...)` 返回 `DefaultTask` 实例
2. 注册后 `ExtensionRegistry.create_tasker("timer", ...)` 返回 `TimerTasker` 实例
3. 用 `DefaultTaskerService` 创建/删除 Tasker → 验证 `taskers.json` 文件更新
4. 用 `DefaultTaskService` 添加 3 条 Task → 验证 segment 文件内容
5. timer 创建一条进行中的记录 → `task.end_time = ""` → `task.is_running == True`
6. account 搜索密码 → 唯一匹配 → 自动复制到剪贴板

## 阶段 5：PySide6 GUI 骨架

**目标**：启动一个可见窗口——三区布局、SystemTray、输入框可打字并显示 log。不绑定具体业务逻辑。

- [ ] `src/ui/component/styled_button.py`, `toast_notification.py`, `confirm_dialog.py`
  - 参考：`docs/architecture/ui/component/SPEC.md`
- [ ] `src/ui/main/system_tray.py` — `SystemTray`
  - 参考：`docs/architecture/ui/main/SPEC.md`
- [ ] `src/ui/main/main_window.py` — `MainWindow`（三区布局、去除×按钮、托盘 minimize）
  - 参考：`docs/architecture/ui/main/SPEC.md`
- [ ] `src/ui/main/main_controller.py` — `MainController`（状态机 + 预处理链连接）
  - 参考：`docs/architecture/ui/main/SPEC.md`

**测试**：
1. 启动 → 看到窗口 → 打字 → 看到输入框文字 → 回车 → 系统输出区有 log 反馈
2. 点击关闭 → 窗口隐藏 → 托盘图标可见 → 右键托盘 → 显示窗口
3. `+xxx` 输入 → 控制台确认预处理为 `search xxx`

## 阶段 6：Tasker 列表 + Task 表格（主界面可用）

**目标**：主界面能看到 Tasker 列表并点击进入，Tasker 内能看到 Task 表格。

- [ ] `src/ui/tasker/tasker_list_widget.py` + `tasker_edit_dialog.py` + `tasker_context_menu.py`
  - 参考：`docs/architecture/ui/tasker/SPEC.md`
- [ ] `src/ui/task/task_table_widget.py` + `task_table_model.py` + `task_edit_panel.py` + `inline_input_bar.py` + `task_search_bar.py`
  - 参考：`docs/architecture/ui/task/SPEC.md`

**测试**：
1. 启动 → 主界面显示 Tasker 列表（从 taskers.json 读取）→ 半透明背景可见
2. 点击 Tasker → 进入 Tasker 界面 → Task 表格显示（两段懒加载）
3. 滚轮滚动到底 → 触发更多 segment 动态加载
4. `new` 指令 → 编辑面板出现 → 逐字段输入 → 创建成功 → 表格刷新
5. `delete` 指令 → 右侧出现 × 按钮 → 点击 → 删除成功

## 阶段 7：快捷按钮

**目标**：主界面和 Tasker 界面右侧常驻区显示快捷按钮，点击可用。

- [ ] `src/extensions/quick_button/quick_button_bar_widget.py` + `quick_button_editor.py`
  - 参考：`docs/architecture/extensions/quick_button/SPEC.md`

**测试**：
1. taskers.json 中配置了 quick_buttons → 主界面右侧显示所有 Tasker 的按钮
2. 点击主界面的快捷按钮 → 自动进入目标 Tasker → 自动创建预设 Task
3. 点击 Tasker 内的快捷按钮 → 直接创建预设 Task
4. 数字键 1-9 → 触发对应按钮
5. 添加/删除快捷按钮 → taskers.json 更新

## 阶段 8：图表分析 + 3D 可视化

**目标**：启动本地 HTTP 服务，外部浏览器可查看图表。不阻塞输入框。

- [ ] `src/analysis/base_analyzer.py` + `analysis_engine.py`
  - 参考：`docs/architecture/analysis/SPEC.md`
- [ ] `src/analysis/attribute_counter.py` + `monthly_counter.py` + `duration_analyzer.py` + `heatmap_builder.py`
  - 参考：`docs/architecture/analysis/SPEC.md`
- [ ] `src/visualization/monthly_3d_builder.py`
  - 参考：`docs/architecture/visualization/SPEC.md`
- [ ] `src/ui/chart/chart_launcher.py` + `chart_mode_controller.py` + `chart_http_server.py`
  - 参考：`docs/architecture/ui/chart/SPEC.md`
- [ ] 图表 HTML 页面：
  - [ ] `src/extensions/default/charts/attr_count.html`
  - [ ] `src/extensions/default/charts/monthly_count.html`
  - [ ] `src/extensions/timer/charts/duration.html`
  - [ ] `src/extensions/timer/charts/3d_monthly.html`

**测试**：
1. 点击"打开图表"→ 浏览器打开 → 显示 ECharts 柱状图
2. 图表打开中 → 输入框可正常输入 → CRUD 不受影响
3. 切换月份 → `fetch()` → 图表增量更新
4. 输入 `exit` → HTTP 服务停止 → 端口释放

## 阶段 9：数据导入导出

**目标**：旧数据迁移 + 人类可读 txt 导出。

- [ ] `src/io/pkl_migrator.py` — pkl → JSON
  - 参考：`docs/architecture/io/SPEC.md`
- [ ] `src/io/txt_exporter.py` — 三种排序模式
  - 参考：`docs/architecture/io/SPEC.md`
- [ ] `src/io/txt_importer.py` — 旧 backup txt 解析
  - 参考：`docs/architecture/io/SPEC.md`
- [ ] `src/io/export_service.py` + `import_service.py`
  - 参考：`docs/architecture/io/SPEC.md`

**测试**：
1. 指定旧 pkl 文件路径 → PklMigrator 生成新 JSON 文件
2. TxtExporter 生成三种排序模式 → 手动检查格式
3. backup 指令生成备份文件夹 → reload 指令读取 → 数据一致

## 阶段 10：入口 + 打包

**目标**：完整的启动流程，exe 打包。

- [ ] `src/main.py` — 入口
  - [ ] 解析启动参数
  - [ ] 单实例检测
  - [ ] 加载扩展模块（扫描 `extensions/` 导入 `__init__.py`）
  - [ ] 创建 StorageManager → 创建 Services → 启动 SystemTray → 启动 MainWindow
- [ ] PyInstaller 配置 — 打包为单个 .exe

**测试**：
1. 双击 exe → 窗口启动 → 托盘驻留 → 全局热键唤出
2. 数据目录正确读写 taskers.json + segment 文件
3. 打出的 exe 体积 < 100MB

## 全部 TODO 索引

| 模块 | 待完成内容 | 参考 SPEC |
|------|-----------|-----------|
| `src/core/` | abstract, registry, types, input_processor, base_service | `docs/architecture/core/SPEC.md` |
| `src/core/storage/` | 5 个文件 | `docs/architecture/core/storage/SPEC.md` |
| `src/core/service/` | 3 个文件 | `docs/architecture/core/service/SPEC.md` |
| `src/extensions/default/` | default_task, default_tasker, __init__ | `docs/architecture/extensions/default/SPEC.md` |
| `src/extensions/timer/` | timer_task, timer_tasker, duration_calc, __init__ | `docs/architecture/extensions/timer/SPEC.md` |
| `src/extensions/account/` | account_task, account_tasker, password_clipboard, __init__ | `docs/architecture/extensions/account/SPEC.md` |
| `src/extensions/label/` | label_task, label_tasker, __init__ | `docs/architecture/extensions/label/SPEC.md` |
| `src/extensions/quick_button/` | quick_button_service, bar_widget, editor, __init__ | `docs/architecture/extensions/quick_button/SPEC.md` |
| `src/ui/main/` | main_window, system_tray, main_controller | `docs/architecture/ui/main/SPEC.md` |
| `src/ui/tasker/` | tasker_list_widget, edit_dialog, context_menu | `docs/architecture/ui/tasker/SPEC.md` |
| `src/ui/task/` | table_widget, table_model, edit_panel, inline_input_bar, search_bar | `docs/architecture/ui/task/SPEC.md` |
| `src/ui/chart/` | chart_launcher, mode_controller, http_server | `docs/architecture/ui/chart/SPEC.md` |
| `src/ui/component/` | styled_button, toast, confirm_dialog | `docs/architecture/ui/component/SPEC.md` |
| `src/analysis/` | engine, base, attr_counter, monthly_counter, duration_analyzer, heatmap | `docs/architecture/analysis/SPEC.md` |
| `src/visualization/` | monthly_3d_builder | `docs/architecture/visualization/SPEC.md` |
| `src/io/` | pkl_migrator, txt_exporter, txt_importer, export_service, import_service | `docs/architecture/io/SPEC.md` |
| `src/config/` | app_config, config_store | `docs/architecture/config/SPEC.md` |
| `src/util/` | json_utils, date_utils, string_utils, file_utils, clipboard_utils | `docs/architecture/util/SPEC.md` |
| `src/` (入口) | main.py, requirements.txt | — |
| 图表 HTML | 4 个 HTML 页面 | `docs/architecture/ui/chart/SPEC.md` |
