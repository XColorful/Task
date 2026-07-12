"""ChartHttpServer -- lightweight HTTP server for chart data API, 127.0.0.1 only."""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread


class ChartHttpServer:
    """Lightweight HTTP server for chart pages. Listens on 127.0.0.1 only."""

    def __init__(self, port=19527):
        self._port = port
        self._server = None
        self._thread = None
        self._engine = None
        self._chart_dir = None

    def set_engine(self, engine):
        self._engine = engine

    def set_chart_dir(self, path):
        self._chart_dir = path

    def start(self):
        server = self
        engine = self._engine
        chart_dir = self._chart_dir

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    if self.path.startswith('/api/analysis/'):
                        name = self.path[len('/api/analysis/'):].split('?')[0]
                        result = engine.analyze(name) if engine else {"error": "no engine"}
                        self._json(200, result)
                    elif self.path.startswith('/chart/') and chart_dir:
                        fname = self.path.split('/')[-1]
                        self._serve_file(chart_dir, fname)
                    elif self.path == '/' or self.path == '/index.html':
                        self._json(200, {"status": "Task Chart Server"})
                    else:
                        self._json(404, {"error": "not found"})
                except Exception as e:
                    self._json(500, {"error": str(e)})

            def _json(self, code, data):
                self.send_response(code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

            def _serve_file(self, base_dir, filename):
                path = None
                for root, dirs, files in os.walk(base_dir):
                    if filename in files:
                        path = os.path.join(root, filename)
                        break
                if path and os.path.exists(path):
                    self.send_response(200)
                    ct = 'text/html'
                    if filename.endswith('.js'): ct = 'application/javascript'
                    elif filename.endswith('.css'): ct = 'text/css'
                    self.send_header('Content-Type', ct)
                    self.end_headers()
                    with open(path, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    self._json(404, {"error": f"chart file not found: {filename}"})

            def log_message(self, format, *args):
                pass  # silent

        self._server = HTTPServer(('127.0.0.1', self._port), Handler)
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server = None

    @property
    def url(self):
        return f"http://127.0.0.1:{self._port}"
