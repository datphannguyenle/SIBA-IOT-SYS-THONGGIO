"""VENT-006 — hằng số và client ThingsBoard có RÀO CHẮN cho demo thông gió cô lập.

Client chỉ cho phép:
  - GET bất kỳ (đọc)
  - POST /api/auth/login
  - POST /api/widgetType, POST /api/dashboard    (chỉ khi allow_create=True, payload không có id)
  - DELETE đúng ID trong manifest                (chỉ khi allow_delete_ids chứa ID đó)
Mọi lệnh khác bị chặn trước khi gửi. Mật khẩu/token không bao giờ được in hay ghi file.
"""
import hashlib
import json
import os
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEPLOY_DIR = ROOT / "deploy/thingsboard"
BUILD_DIR = DEPLOY_DIR / "build"
MANIFEST = DEPLOY_DIR / "vent006_manifest.json"
EVIDENCE_DIR = ROOT / "docs/ventilation/deployment/evidence"

TB_URL = os.environ.get("TB_URL", "http://100.86.144.207:8080").rstrip("/")
TB_USER = os.environ.get("TB_USER", "tenant@siba.com.vn")
PASSWORD_FILE = pathlib.Path(os.path.expanduser(os.environ.get("TB_PASSWORD_FILE", "~/.config/siba-tb-pass")))

WIDGET_FQN = "siba_vent_demo.vent_demo_view"          # fqn lưu trong TB (không tiền tố)
WIDGET_FULL_FQN = "tenant." + WIDGET_FQN              # typeFullFqn / tra cứu theo fqn
WIDGET_NAMESPACE_PREFIX = "tenant.siba_vent_demo."
DASHBOARD_TITLE = "DB-30-VEN-DETAIL-V1-DEMO"
STATES = ["default", "vent_detail", "vent_history", "vent_alarms"]

# fqn có thật dùng để hiệu chuẩn: tra cứu đúng cú pháp phải trả 200, để 404 của ta có nghĩa.
CALIBRATION_FQN = "tenant.siba_custom_ui.header_bar"

# Mốc đã ghi trong kế hoạch được duyệt (17/09/2026). Lệch bất thường -> DỪNG.
PROTECTED_DASHBOARDS = {
    "bb585f20-a835-11f1-9683-f9c2621c1a59": {"title": "SIBA · Khử mùi", "version": 27, "sha16": "99c899a8188f05b4"},
    "916ba6a0-acb7-11f1-9683-f9c2621c1a59": {"title": "SIBA · Khử mùi · SIMULATION", "version": 9, "sha16": "faccbe9141863dd0"},
    "a66660b0-9a04-11f1-a0fc-e93bd628a87f": {"title": "MUGE · Tổng quan trại", "version": 107, "sha16": "ed99833e5fa97194"},
}
PROTECTED_BUNDLE = {"alias": "siba_custom_ui", "count": 15, "sha16": "af87a8ba7849ac09"}


class Blocked(RuntimeError):
    """Lệnh bị rào chắn chặn trước khi gửi."""


def config_sha(configuration):
    return hashlib.sha256(json.dumps(configuration, sort_keys=True).encode()).hexdigest()


def fqn_list_sha(fqns):
    return hashlib.sha256(",".join(fqns).encode()).hexdigest()


def read_password():
    env = os.environ.get("TB_PASSWORD")
    if env:
        return env
    if not PASSWORD_FILE.is_file():
        raise SystemExit("Thiếu mật khẩu: đặt TB_PASSWORD hoặc tạo %s (quyền 600)" % PASSWORD_FILE)
    return PASSWORD_FILE.read_text().strip()


class GuardedTB:
    def __init__(self, allow_create=False, allow_delete_ids=()):
        self.allow_create = allow_create
        self.allow_delete_ids = set(allow_delete_ids)
        self.mutations = []          # nhật ký lệnh ghi đã gửi (không chứa payload nhạy cảm)
        self._token = None

    def _check(self, method, path, body):
        if method == "GET":
            return
        if method == "POST" and path == "/api/auth/login":
            return
        if method == "POST" and path in ("/api/widgetType", "/api/dashboard"):
            if not self.allow_create:
                raise Blocked("create not enabled: POST %s" % path)
            if not isinstance(body, dict) or "id" in body:
                raise Blocked("create payload must not carry an id: POST %s" % path)
            if path == "/api/widgetType" and body.get("fqn") != WIDGET_FQN:
                raise Blocked("unexpected widget fqn")
            if path == "/api/dashboard" and (body.get("title") != DASHBOARD_TITLE or body.get("assignedCustomers")):
                raise Blocked("unexpected dashboard payload")
            return
        if method == "DELETE":
            for prefix in ("/api/dashboard/", "/api/widgetType/"):
                if path.startswith(prefix) and path[len(prefix):] in self.allow_delete_ids:
                    return
        raise Blocked("%s %s" % (method, path))

    def request(self, path, method="GET", body=None):
        self._check(method, path, body)
        req = urllib.request.Request(TB_URL + path, method=method, headers={"Content-Type": "application/json"})
        if path != "/api/auth/login":
            req.add_header("X-Authorization", "Bearer " + self.token)
        data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
        if method != "GET" and path != "/api/auth/login":
            self.mutations.append({"method": method, "path": path})
        try:
            with urllib.request.urlopen(req, data, timeout=120) as resp:
                raw = resp.read().decode()
                return resp.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as err:
            return err.code, err.read().decode()[:500]

    @property
    def token(self):
        if self._token is None:
            status, body = self.request("/api/auth/login", "POST", {"username": TB_USER, "password": read_password()})
            if status != 200:
                raise SystemExit("Đăng nhập thất bại (%s)" % status)
            self._token = body["token"]
        return self._token

    def get(self, path):
        return self.request(path)

    def get_ok(self, path):
        status, body = self.get(path)
        if status != 200:
            raise RuntimeError("GET %s -> %s" % (path, status))
        return body

    def pages(self, path):
        items, page = [], 0
        while True:
            sep = "&" if "?" in path else "?"
            body = self.get_ok("%s%spageSize=500&page=%d" % (path, sep, page))
            items += body["data"]
            if not body.get("hasNext"):
                return items
            page += 1


def write_json(path, data):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
