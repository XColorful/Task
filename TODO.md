## 阶段 12：剩余工作

以下基于用户测试反馈，列出仍需补充的功能点（已在当前分支完成）。

### 12.1 设置界面完善
- [x] 增加 `max_segment_size` 配置项（已在 AppConfig 中定义）
- [x] 支持从 AppConfig 读取 `http_port` 并应用到 ChartHttpServer

### 12.2 Tasker 内部界面通信
- [x] 搜索功能：搜索结果面板与常驻区表格同步（已有 `show_search_results`）
- [x] 快速按钮：支持跨 Tasker 触发（已有 `_cmd_task_new` 及 end_timer）
- [x] 搜索结果为空时提示

### 12.3 数据迁移与导入导出
- [x] migrate 指令支持从 old backup txt 文件导入（`migrate <path>.txt`）— TxtImporter 已完成
- [x] txt 导出路径改为软件数据目录下生成

## All phases complete. 92 files, 5649 LOC, 4 charts, all tests pass.