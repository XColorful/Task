# SPEC: ui/chart — 图表模式 UI 层

> 对应源码路径: `src/ui/chart/`
> 管理外部浏览器图表生命周期——本地 HTTP 服务启停、浏览器打开。图表模式期间输入框保持可用，用户可继续正常 CRUD。

---

## 1. chart_launcher.py

### 1.1 ChartLauncher

```python
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QComboBox
from PySide6.QtCore import Signal


class ChartLauncher(QWidget):
    """图表入口组件——包含启动按钮和图表类型选择器。

    位于主界面内容区的工具栏区域。点击"打开图表"按钮后:
    1. 根据当前选中的图表类型，从存储层预取分析数据
    2. 启动本地 HTTP 服务
    3. 调用 webbrowser.open() 打开浏览器
    4. 主窗口进入图表模式（输入框仍可用）
    """

    # 信号: 请求启动图表模式
    # 参数: (chart_type: str, initial_data: dict)
    # chart_type 为 "attr_count" | "monthly_count" | "duration" | "3d_monthly"
    launch_requested = Signal(str, dict)

    # 支持的图表类型列表
    CHART_TYPES: list[tuple[str, str]] = [
        ("attr_count",    "属性统计"),
        ("monthly_count", "月度趋势"),
        ("duration",      "时长分析"),
        ("3d_monthly",    "3D 月度"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        """初始化图表启动器。

        布局:
        - QComboBox: 图表类型下拉选择器
        - QPushButton: "打开图表"按钮

        按钮初始状态为 enabled。点击后:
        1. 按钮变为 disabled + 文字变为 "启动中…"（防止重复点击）
        2. 调用 _prefetch_data() 预取初始数据
        3. 发射 launch_requested 信号
        4. 回调成功 → 按钮保持 disabled + "图表已打开"
        5. 回调失败 → 按钮恢复 enabled + "打开图表"
        """
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._type_selector = QComboBox()
        for value, label in self.CHART_TYPES:
            self._type_selector.addItem(label, value)

        self._launch_btn = QPushButton("打开图表")
        self._launch_btn.clicked.connect(self._on_launch)

        layout.addWidget(self._type_selector)
        layout.addWidget(self._launch_btn)

    # --- 属性 ---

    @property
    def selected_chart_type(self) -> str:
        """返回当前选中的图表类型标识（如 "attr_count"）。"""
        return self._type_selector.currentData()

    # --- 状态控制 ---

    def set_launching(self) -> None:
        """设置按钮为"启动中"状态——disabled + 文字变更。"""
        self._launch_btn.setEnabled(False)
        self._launch_btn.setText("启动中…")

    def set_launched(self) -> None:
        """设置按钮为"已启动"状态——disabled + 文字变更。"""
        self._launch_btn.setEnabled(False)
        self._launch_btn.setText("图表已打开")

    def set_idle(self) -> None:
        """恢复按钮到可点击状态。"""
        self._launch_btn.setEnabled(True)
        self._launch_btn.setText("打开图表")

    # --- 内部 ---

    def _on_launch(self) -> None:
        """按钮点击处理。

        步骤:
        1. 获取 selected_chart_type
        2. set_launching()
        3. 调用 _prefetch_data(chart_type) 预取初始数据
        4. 发射 launch_requested(chart_type, initial_data)
           - MainController / ChartModeController 连接此信号
           - 成功 → 回调 set_launched()
           - 失败 → 回调 set_idle() + 在 output_area 显示错误
        """
        chart_type = self.selected_chart_type
        self.set_launching()
        try:
            initial_data = self._prefetch_data(chart_type)
            self.launch_requested.emit(chart_type, initial_data)
        except Exception as e:
            self.set_idle()
            raise  # 由 MainController 捕获并 log

    def _prefetch_data(self, chart_type: str) -> dict:
        """预取初始分析数据。

        在浏览器打开之前预先调用分析引擎获取初始数据，
        存入 ChartModeController._initial_data 中。
        浏览器首次 fetch /api/analysis/{name} 时直接返回缓存数据，
        避免浏览器打开后等待首次 API 调用。

        数据获取逻辑:
        - 根据 chart_type 查找对应分析器
        - attr_count / monthly_count: 使用默认 Tasker + 当前年月
        - duration / 3d_monthly: 使用默认 Timer Tasker + 当前年月
        - 返回 dict 供 ECharts 页面消费

        Returns:
            分析结果 dict，结构由对应分析器定义
        """
        ...
```

---

## 2. chart_mode_controller.py

### 2.1 ChartModeController

```python
from PySide6.QtCore import QObject, Signal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chart_http_server import ChartHttpServer


class ChartModeController(QObject):
    """管理图表模式状态——HTTP 服务生命周期、端口管理。

    由 MainController 持有。图表模式下的生命周期:
    1. enter_chart_mode(chart_type, initial_data) → 启动 HTTP 服务 + 打开浏览器
    2. 用户在浏览器中交互（fetch API 动态获取数据）
    3. exit_chart_mode() → 停止 HTTP 服务 + 释放端口 + 恢复主界面状态
    """

    # 信号
    chart_mode_entered = Signal()       # 图表模式已进入
    chart_mode_exited = Signal()        # 图表模式已退出
    server_error = Signal(str)          # HTTP 服务错误

    def __init__(self, parent: QObject | None = None) -> None:
        """初始化图表模式控制器。

        状态:
        - _server: ChartHttpServer | None —— 当前运行的 HTTP 服务实例
        - _current_port: int —— 当前使用的端口号
        - _initial_data: dict | None —— 预取的分析数据（首次 API 调用直接返回）
        - _is_chart_mode: bool —— 是否处于图表模式
        """
        super().__init__(parent)
        self._server: 'ChartHttpServer | None' = None
        self._current_port: int = 0
        self._initial_data: dict | None = None
        self._is_chart_mode: bool = False

    # --- 公共方法 ---

    @property
    def is_chart_mode(self) -> bool:
        """是否处于图表模式。"""
        return self._is_chart_mode

    @property
    def current_port(self) -> int:
        """当前 HTTP 服务端口号。未启动时为 0。"""
        return self._current_port

    @property
    def initial_data(self) -> dict | None:
        """预取的初始分析数据（供 ChartHttpServer 首次 API 调用直接返回）。"""
        return self._initial_data

    def enter_chart_mode(self, chart_type: str, initial_data: dict) -> None:
        """进入图表模式。

        流程:
        1. 如果已在图表模式 → 先 exit_chart_mode()
        2. 保存 initial_data（首次 HTTP API 调用直接返回缓存数据）
        3. 分配端口号:
           - 优先使用 AppConfig 中配置的端口（默认 8765）
           - 端口被占用 → 自动递增查找可用端口（最多尝试 100 次）
           - 仍失败 → 发射 server_error + 返回
        4. 创建 ChartHttpServer 实例并启动
        5. 调用 webbrowser.open(f"http://127.0.0.1:{port}/chart/{chart_type}.html")
        6. 更新 _is_chart_mode = True
        7. 发射 chart_mode_entered 信号

        Args:
            chart_type: 图表类型标识（"attr_count" 等）
            initial_data: 预取的分析数据 dict

        异常处理:
        - 端口分配失败 → log 错误 + 发射 server_error
        - HTTP 服务启动失败 → log 错误 + 发射 server_error
        - webbrowser.open() 失败不阻塞流程——浏览器未打开时服务仍可运行
        """
        ...

    def exit_chart_mode(self) -> None:
        """退出图表模式。

        流程:
        1. 如果 _server 不为 None:
           a. 调用 _server.shutdown() 停止 HTTP 服务
           b. 等待服务线程结束（join）
           c. 释放 _server 引用
        2. _is_chart_mode = False
        3. _current_port = 0
        4. _initial_data = None
        5. 发射 chart_mode_exited 信号

        调用时机:
        - 用户在输入框输入 "exit" 或 "/exit"（图表模式下）
        - 用户点击系统托盘 "退出"
        - 应用退出时（MainController.exit_app() 中调用）
        """
        ...

    def _find_available_port(self, start_port: int = 8765, max_attempts: int = 100) -> int | None:
        """查找可用端口。

        Args:
            start_port: 起始端口号
            max_attempts: 最大尝试次数

        Returns:
            可用端口号，或 None（所有端口被占用）

        实现:
        - 逐个尝试 bind socket (127.0.0.1, port)
        - 成功 bind → 关闭 socket → 返回端口号
        - 失败 → port += 1 继续
        """
        ...
```

---

## 3. chart_http_server.py

### 3.1 ChartHttpServer

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.extension_registry import ExtensionRegistry


class ChartHttpServer:
    """本地 HTTP 服务——仅监听 127.0.0.1，只读查询。

    线程模型:
    - 服务运行在独立线程中（daemon thread）
    - 每个请求在 HTTP 服务线程中处理
    - 分析器调用（storage 读取）是只读操作——不产生写竞争
    - 存储层原子写入（tmp → rename）天然保证并发安全

    路由:
    - GET /api/analysis/{analyzer_name}?params... → 调用分析引擎 → 返回 JSON
    - GET /chart/{page_name}.html → 返回扩展模块 charts/ 目录下的 HTML 文件
    """

    def __init__(self, port: int, initial_data: dict | None = None) -> None:
        """初始化 HTTP 服务。

        Args:
            port: 监听端口号
            initial_data: 预取数据——首个请求直接返回缓存，无需调用分析引擎

        内部:
        - 创建 HTTPServer((127.0.0.1, port), _RequestHandler)
        - _RequestHandler 通过类属性获取 server 实例引用以访问路由逻辑
        """
        self._port = port
        self._initial_data = initial_data
        self._server: HTTPServer | None = None
        self._thread: Thread | None = None

    # --- 生命周期 ---

    def start(self) -> None:
        """在独立线程中启动 HTTP 服务。

        步骤:
        1. 创建 HTTPServer 实例，绑定 127.0.0.1:{port}
        2. 将 self 注入到 _RequestHandler 的类属性中（以便访问路由方法）
        3. 创建 Thread(target=self._server.serve_forever, daemon=True)
        4. 启动线程
        """
        ...

    def shutdown(self) -> None:
        """停止 HTTP 服务。

        步骤:
        1. 调用 self._server.shutdown()
        2. 调用 self._server.server_close()
        3. 等待线程结束（join with timeout 5s）

        幂等——多次调用无害。
        """
        ...

    @property
    def is_running(self) -> bool:
        """服务是否在运行。"""
        return self._thread is not None and self._thread.is_alive()

    @property
    def port(self) -> int:
        return self._port

    # --- 路由处理 ---

    def handle_request(self, path: str, query_params: dict[str, str]) -> tuple[int, str, str]:
        """路由分发。

        Args:
            path: 请求路径（如 "/api/analysis/attr_count"）
            query_params: URL 查询参数字典

        Returns:
            (status_code, content_type, body) 三元组
            - status_code: HTTP 状态码
            - content_type: "application/json" 或 "text/html"
            - body: 响应体字符串

        路由规则:
        1. GET /api/analysis/{analyzer_name}
           - 提取 analyzer_name
           - 如果是首次请求（_initial_data 不为 None）→ 返回缓存数据 + 清空 _initial_data
           - 否则 → 调用分析引擎 → 返回 JSON
           - analyzer_name 不存在 → 404
        2. GET /chart/{page_name}.html
           - 从 ExtensionRegistry 查找 page_name 对应的 HTML 文件路径
           - 读取 HTML 文件内容 → 返回
           - page_name 不存在 → 404
        3. 其他路径 → 404
        """
        ...

    def _handle_analysis(self, analyzer_name: str, params: dict[str, str]) -> tuple[int, str, str]:
        """处理分析 API 请求。

        步骤:
        1. 如果 self._initial_data 不为 None:
           - 检查 analyzer_name 是否与缓存的类型匹配
           - 匹配 → 返回缓存数据 + self._initial_data = None
           - 不匹配 → 继续走正常分析流程
        2. 通过 ExtensionRegistry.get_analyzer(analyzer_name) 获取分析器实例
        3. 调用 analyzer.analyze(params) 获取结果
        4. 序列化为 JSON 返回

        Returns:
            (200, "application/json", json_string) 或 (404, ..., ...)
        """
        ...

    def _handle_chart_page(self, page_name: str) -> tuple[int, str, str]:
        """处理图表 HTML 页面请求。

        步骤:
        1. 通过 ExtensionRegistry.get_chart_page(page_name) 获取文件路径
           - 路径格式: "extensions/{module}/charts/{page_name}.html"
        2. 拼接完整路径: {project_root}/src/{chart_page_path}
        3. 读取文件内容（UTF-8）
        4. 返回 HTML 内容

        Returns:
            (200, "text/html; charset=utf-8", html_string) 或 (404, ..., ...)
        """
        ...

    def _handle_not_found(self) -> tuple[int, str, str]:
        """404 响应。"""
        return (404, "application/json", '{"error": "Not found"}')
```

### 3.2 _RequestHandler

```python
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class _RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器（内部类，由 ChartHttpServer 使用）。

    类属性:
    - server_instance: ChartHttpServer —— 在服务启动时注入

    所有请求方法均为 GET。
    """

    server_instance: 'ChartHttpServer | None' = None

    def do_GET(self) -> None:
        """处理 GET 请求。

        流程:
        1. 解析 URL: path + query params
        2. 调用 self.server_instance.handle_request(path, params)
        3. 写入响应 status code + headers + body
        """
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        if self.server_instance is None:
            self._send_response(500, "application/json", '{"error": "Server not ready"}')
            return

        status, content_type, body = self.server_instance.handle_request(path, query_params)
        self._send_response(status, content_type, body)

    def _send_response(self, status: int, content_type: str, body: str) -> None:
        """发送 HTTP 响应。"""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")  # 允许浏览器 fetch
        self.send_header("Cache-Control", "no-cache")          # 禁用缓存（数据实时）
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format: str, *args) -> None:
        """覆盖默认日志——输出到应用日志而非 stderr。"""
        ...
```

---

## 4. 图表 HTML 页面模板结构

每个扩展模块的 `charts/` 子目录下包含静态 HTML 页面文件。所有页面遵循统一的模板结构。

### 4.1 核心模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><!-- 页面标题: 如 "属性统计" --></title>

    <!-- ECharts CDN -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>

    <style>
        /* ── 公共样式 ── */
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                         "Microsoft YaHei", sans-serif;
            background: #1a1a2e;
            color: #e0e0e0;
            min-height: 100vh;
        }

        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 24px;
            background: #16213e;
            border-bottom: 1px solid #0f3460;
        }

        .header h1 {
            font-size: 20px;
            font-weight: 600;
            color: #e94560;
        }

        .header .controls {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .header select, .header input, .header button {
            padding: 6px 12px;
            border: 1px solid #0f3460;
            border-radius: 4px;
            background: #1a1a2e;
            color: #e0e0e0;
            font-size: 14px;
        }

        .header button {
            cursor: pointer;
            background: #e94560;
            border-color: #e94560;
            color: #fff;
            font-weight: 500;
        }

        .header button:hover { background: #c73650; }
        .header button:disabled {
            background: #555;
            border-color: #555;
            cursor: not-allowed;
        }

        .chart-container {
            width: 100%;
            height: calc(100vh - 80px); /* 减去 header 高度 */
        }

        .loading-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(26, 26, 46, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }

        .loading-overlay.hidden { display: none; }

        .loading-spinner {
            width: 40px; height: 40px;
            border: 3px solid #0f3460;
            border-top-color: #e94560;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        .error-banner {
            display: none;
            padding: 12px 24px;
            background: #e94560;
            color: #fff;
            text-align: center;
            font-size: 14px;
        }

        .error-banner.visible { display: block; }
    </style>
</head>
<body>
    <!-- 顶部工具栏 -->
    <div class="header">
        <h1><!-- 页面标题 --></h1>
        <div class="controls">
            <!-- 筛选控件: 下拉框、输入框、刷新按钮（按页面需求） -->
            <button id="refresh-btn" onclick="refreshChart()">刷新</button>
        </div>
    </div>

    <!-- 图表区域 -->
    <div class="chart-container" id="chart-container"></div>

    <!-- 加载遮罩 -->
    <div class="loading-overlay" id="loading-overlay">
        <div class="loading-spinner"></div>
    </div>

    <!-- 错误横幅 -->
    <div class="error-banner" id="error-banner"></div>

    <script>
        // ── 全局变量 ──
        const API_BASE = `http://127.0.0.1:${new URLSearchParams(window.location.search).get('port') || '8765'}`;
        const ANALYZER_NAME = '<!-- 分析器名称: attr_count / monthly_count / duration / 3d_monthly -->';
        let chartInstance = null;
        let isLoading = false;

        // ── 初始化 ──
        document.addEventListener('DOMContentLoaded', () => {
            initChart();
            fetchData();
        });

        // 窗口大小变化时自适应图表
        window.addEventListener('resize', () => {
            if (chartInstance) chartInstance.resize();
        });

        // ── 图表初始化 ──
        function initChart() {
            const container = document.getElementById('chart-container');
            chartInstance = echarts.init(container, 'dark');
            // 可在此设置通用的 ECharts option 默认值
        }

        // ── 数据获取 ──
        async function fetchData(params = {}) {
            if (isLoading) return;
            isLoading = true;
            showLoading(true);
            hideError();

            try {
                // 构建查询参数
                const urlParams = new URLSearchParams(params);
                const url = `${API_BASE}/api/analysis/${ANALYZER_NAME}?${urlParams.toString()}`;

                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();

                if (data.error) {
                    throw new Error(data.error);
                }

                // 根据页面类型调用对应的渲染函数
                renderChart(data);

            } catch (error) {
                console.error('数据获取失败:', error);
                showError(`数据加载失败: ${error.message}`);
            } finally {
                isLoading = false;
                showLoading(false);
            }
        }

        // ── 图表渲染 ──
        function renderChart(data) {
            // 各页面自行实现——构建 ECharts option 并调用:
            // chartInstance.setOption(option, { notMerge: true });
            //
            // 示例结构（以 attr_count 饼图为例）:
            // const option = {
            //     title: { text: '属性统计', left: 'center' },
            //     tooltip: { trigger: 'item' },
            //     series: [{
            //         type: 'pie',
            //         radius: ['40%', '70%'],
            //         data: data.categories.map(c => ({ name: c.name, value: c.count })),
            //     }],
            // };
            // chartInstance.setOption(option, { notMerge: true });
        }

        function refreshChart() {
            // 收集当前筛选条件，重新 fetchData
            const params = collectFilterParams();
            fetchData(params);
        }

        // ── 筛选参数收集（各页面按需覆写）──
        function collectFilterParams() {
            return {};
        }

        // ── UI 辅助 ──
        function showLoading(show) {
            document.getElementById('loading-overlay').classList.toggle('hidden', !show);
        }

        function showError(message) {
            const banner = document.getElementById('error-banner');
            banner.textContent = message;
            banner.classList.add('visible');
            // 5 秒后自动隐藏
            setTimeout(() => banner.classList.remove('visible'), 5000);
        }

        function hideError() {
            document.getElementById('error-banner').classList.remove('visible');
        }
    </script>
</body>
</html>
```

### 4.2 页面模板约定

每个图表 HTML 页面在核心模板基础上按以下约定定制:

| 定制项 | 说明 |
|--------|------|
| `<title>` + `<h1>` | 图表名称（如 "属性统计"、"月度趋势"、"时长分析"、"3D 月度网格"） |
| `ANALYZER_NAME` | 对应分析器注册名（`attr_count` / `monthly_count` / `duration` / `3d_monthly`） |
| `.controls` | 页面专属的筛选控件（年份选择、月份选择、属性过滤下拉框等） |
| `renderChart()` | 页面专属的 ECharts option 构建逻辑 |
| `collectFilterParams()` | 从筛选控件收集参数 dict，传给 fetchData |

**3D 月度页面额外加载:**
```html
<script src="https://cdn.jsdelivr.net/npm/echarts-gl@2.0.9/dist/echarts-gl.min.js"></script>
```

### 4.3 数据获取模式

```
浏览器发起请求
  → GET /api/analysis/{analyzer_name}?tasker_id=xxx&year=2026&month=7
  → ChartHttpServer._handle_analysis() 路由
  → 首次请求: 返回 Controller 预取的 initial_data（响应立即返回，无延迟）
  → 后续请求: 调用 ExtensionRegistry.get_analyzer(name).analyze(params)
  → 分析器从存储层读取数据
  → 聚合计算
  → 返回 JSON
  → 浏览器 renderChart(data) 更新图表
```

### 4.4 错误处理

- **网络错误** (fetch failed): 显示错误横幅 + 控制台日志
- **HTTP 4xx/5xx**: 显示 HTTP 状态码错误横幅
- **API 返回 error 字段**: 显示业务错误信息
- **空数据**: renderChart 中判断 data 是否为空，显示 "暂无数据" 或空图表
- **自动重试**: 不自动重试——用户点击 "刷新" 按钮手动重新请求
- **超时**: fetch 默认无超时；由浏览器自身或网络层控制

---

## 5. 依赖关系

```
ui/chart/
├── chart_launcher.py           # 依赖: PySide6, core.extension_registry, core.base_service
├── chart_mode_controller.py    # 依赖: PySide6 (Signal), chart_http_server, webbrowser
├── chart_http_server.py        # 依赖: http.server (stdlib), core.extension_registry, pathlib
└── __init__.py
```

```
图表页面 (扩展模块 charts/ 目录下):
extensions/default/charts/
├── attr_count.html             # 依赖: ECharts CDN, fetch API
└── monthly_count.html          # 依赖: ECharts CDN, fetch API

extensions/timer/charts/
├── duration.html               # 依赖: ECharts CDN, fetch API
└── 3d_monthly.html             # 依赖: ECharts CDN + ECharts GL CDN, fetch API
```

---

## 6. 图表模式状态流转

```
┌──────────────────────────────────────────────────────────────┐
│                       图表模式状态机                          │
│                                                              │
│  [MAIN 状态]                                                 │
│       │                                                      │
│       │ 用户点击 ChartLauncher "打开图表"                     │
│       ▼                                                      │
│  1. _prefetch_data(chart_type) 预取分析数据                   │
│       │                                                      │
│       ▼                                                      │
│  2. ChartModeController.enter_chart_mode(type, data)         │
│       │                                                      │
│       ├── 2a. _find_available_port() 分配端口                │
│       ├── 2b. ChartHttpServer 启动（独立线程）                │
│       ├── 2c. webbrowser.open(URL) 打开浏览器                │
│       └── 2d. state → CHART                                 │
│       │                                                      │
│       ▼                                                      │
│  [CHART 状态]                                                │
│       │                                                      │
│       │ 浏览器首次 fetch /api/analysis/...                   │
│       │ → 返回 initial_data (缓存数据，立即响应)              │
│       │                                                      │
│       │ 浏览器后续 fetch (筛选条件变化 / 用户刷新)            │
│       │ → 调用分析引擎 → 返回新数据                           │
│       │                                                      │
│       │ 用户在输入框输入 "exit" 或 "/exit"                    │
│       ▼                                                      │
│  3. ChartModeController.exit_chart_mode()                    │
│       │                                                      │
│       ├── 3a. server.shutdown() 停止 HTTP 服务               │
│       ├── 3b. join 线程 + 释放端口                            │
│       └── 3c. state → MAIN                                   │
│       │                                                      │
│       ▼                                                      │
│  [MAIN 状态]                                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. 注意事项

1. **输入框保持可用**: 图表模式不是"全屏独占"——MainWindow 的 input_box 持续接受输入，用户可切换 Tasker、增删改 Task。退出图表模式（"exit"）是唯一新增的指令。

2. **浏览器生命周期独立**: 关闭浏览器标签页不会退出图表模式——HTTP 服务仍运行。用户只需在 input_box 输入 "exit" 即可停止服务。无意中关闭浏览器后重新点击 "打开图表" 会复用现有服务。

3. **端口冲突处理**: 默认端口 8765。被占用时自动递增查找（8766, 8767, ...）。建议在 AppConfig 中记录上次成功使用的端口号以便下次快速复用。

4. **并发安全**: HTTP 服务运行在独立线程。分析器的数据读取（storage 读取）是只读操作，不产生写竞争。存储层的原子写入（先写 .tmp 再 rename）保证写入时的一致性——读取操作要么读到旧文件（写入前）要么读到新文件（rename 后），不会读到半写状态。

5. **线程安全边界**: HTTP 服务线程不得直接操作 PySide6 控件。如需从分析器回调更新 UI（如显示分析进度），通过 `QMetaObject.invokeMethod` 或 Signal 跨线程调度到主线程。

6. **daemon 线程**: HTTP 服务线程为 daemon——应用退出（QApplication.quit()）时自动终止，不会阻塞进程退出。但建议在 exit_app() 中显式调用 exit_chart_mode() 做优雅关闭。

7. **只监听 127.0.0.1**: ChartHttpServer 仅绑定回环地址，不暴露到局域网。MIME 类型: `.html` → `text/html; charset=utf-8`，`.js` → `application/javascript`（如需），JSON → `application/json; charset=utf-8`。

8. **CORS 头**: 浏览器从 `file://` 或 `http://127.0.0.1:{port}` 加载页面后 fetch API 同源——理论上不需要 CORS。添加 `Access-Control-Allow-Origin: *` 作为防御性措施以应对某些浏览器的严格同源策略。
