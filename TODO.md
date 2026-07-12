## 阶段 11：主界面功能补完

**调查结果**：MainController 当前仅有占位符（`[TODO]` 或 `log("No Tasker found")`），以下是对比界面设计文档后列出的全部未实现功能。

### 11.1 主界面 Tasker CRUD（`_dispatch_main`）

- [x] `add` — 弹出 TaskerEditDialog → 创建 Tasker → 刷新 TaskerListWidget
- [x] `delete` — 按索引/标签选择 → 确认删除 → 刷新列表
- [x] `edit` — 按索引/标签选择 → 弹出编辑对话框 → 更新 → 刷新
- [x] `info` — 按索引/标签选择 → 显示 Tasker 详细信息（log 区）
- [x] `sort` — 按 tasker_label 排序 → 保存新顺序 → 刷新
- [x] 直接输入 Tasker 名/索引 → 进入该 Tasker

### 11.2 主界面全局操作

- [x] `backup` — 调用 StorageManager.backup_all() → 创建时间戳文件夹
- [x] `reload` — 指定备份目录 → reload_from_backup → 显示结果
- [x] `txt` — 调用 ExportService/TxtExporter → 生成 Task_txt.txt
- [x] `migrate` — 调用 PklMigrator 迁移旧 pkl 数据

### 11.3 设置界面

- [x] SettingsView — placeholder, 显示配置信息 (AppConfig)

### 11.4 Tasker 内部指令

- [x] `new` — 弹出 TaskEditPanel → 填写字段 → 创建 → 表格刷新
- [x] `search` — 调用 search_tasks → 结果显示在右侧常驻区（表格格式）
- [x] `delete` — 按索引/搜索 → 确认删除 → 刷新表格
- [x] `edit` — 按索引/搜索 → 编辑面板 → 更新 → 刷新
- [x] `end` — Timer end_timer（进行中计时器结束）

### 11.5 旧数据导入

- [x] `migrate` — `migrate <pkl路径>` → 调用 PklMigrator → 刷新列表
