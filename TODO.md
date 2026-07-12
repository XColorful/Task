## 阶段 12：剩余工作

以下基于用户测试反馈，列出仍需补充的功能点。

### 12.1 设置界面完善
- [ ] 增加 `max_segment_size` 配置项
- [ ] 支持从 AppConfig 读取 `http_port` 并应用到 ChartHttpServer

### 12.2 Tasker 内部界面通信
- [ ] 搜索功能：搜索结果面板与常驻区表格同步
- [ ] 快速按钮：支持跨 Tasker 触发
- [ ] 搜索结果为空时提示

### 12.3 数据迁移与导入导出
- [ ] migrate 指令支持从 old backup txt 文件导入（`migrate <path>.txt`）
- [ ] txt 导出路径改为软件数据目录下生成

### 12.4 配置管理
- [ ] 从 AppConfig 读取 `http_port` 并应用到 ChartHttpServer
