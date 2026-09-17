"""Trình điều khiển WebDriver tối giản (geckodriver + Firefox headless), không cần selenium.

Chỉ dùng cho demo repository: phục vụ file tĩnh qua 127.0.0.1, không gọi ThingsBoard.
"""
import base64
import functools
import http.server
import json
import pathlib
import shutil
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def geckodriver_path():
    return shutil.which("geckodriver")


class StaticServer:
    def __init__(self):
        handler = functools.partial(_QuietHandler, directory=str(ROOT))
        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", _free_port()), handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    @property
    def base_url(self):
        return "http://127.0.0.1:%d" % self.httpd.server_address[1]

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.httpd.shutdown()
        self.httpd.server_close()


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class Browser:
    """Phiên Firefox headless; chỉ thao tác với trang demo cục bộ."""

    def __init__(self, width=1920, height=1080):
        self.port = _free_port()
        self.proc = subprocess.Popen([geckodriver_path(), "--port", str(self.port)],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.base = "http://127.0.0.1:%d" % self.port
        self._wait_ready()
        caps = {"capabilities": {"alwaysMatch": {"moz:firefoxOptions": {"args": ["-headless"]}}}}
        self.session = self._call("POST", "/session", caps)["sessionId"]
        self.resize(width, height)

    def _wait_ready(self):
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                self._call("GET", "/status")
                return
            except (urllib.error.URLError, ConnectionError):
                time.sleep(0.2)
        raise RuntimeError("geckodriver did not start")

    def _call(self, method, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(self.base + path, data=data, method=method,
                                         headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read())["value"]

    def _session(self, method, path, body=None):
        return self._call(method, "/session/%s%s" % (self.session, path), body)

    def resize(self, width, height):
        self._session("POST", "/window/rect", {"width": width, "height": height})

    def open(self, url):
        self._session("POST", "/url", {"url": url})
        self.wait_for("return !!document.querySelector('.vent-header')")

    def run(self, script, *args):
        return self._session("POST", "/execute/sync", {"script": script, "args": list(args)})

    def wait_for(self, script, timeout=15):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.run(script):
                return
            time.sleep(0.1)
        raise AssertionError("Timed out waiting for: " + script)

    def screenshot_full(self, path):
        png = self._session("GET", "/moz/screenshot/full")
        pathlib.Path(path).write_bytes(base64.b64decode(png))

    def close(self):
        try:
            self._session("DELETE", "")
        finally:
            self.proc.terminate()
            self.proc.wait(timeout=30)
