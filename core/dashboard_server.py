"""
Industrial HTTP Telemetry & Dashboard Server for Jarvis.
Runs a lightweight, non-blocking HTTP server on port 8766 so any computer,
tablet, or phone on the local Wi-Fi can view Jarvis's live telemetry and memory banks.
"""

import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from core.dashboard import generate_dashboard_html

logger = logging.getLogger("Jarvis.DashboardServer")

class DashboardHandler(BaseHTTPRequestHandler):
    data_provider = None

    def do_GET(self):
        if self.path in ["/", "/dashboard", "/status"]:
            data = self.data_provider() if self.data_provider else {}
            content = generate_dashboard_html(data).encode("utf-8")
            
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress noisy HTTP access logs in terminal
        pass

class DashboardServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8766, data_provider=None):
        self.host = host
        self.port = port
        DashboardHandler.data_provider = data_provider
        self.server = None
        self.thread = None

    def start(self):
        try:
            self.server = HTTPServer((self.host, self.port), DashboardHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info(f"📊 Industrial Mission-Control Dashboard live at: http://{self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to start Dashboard server: {e}")
