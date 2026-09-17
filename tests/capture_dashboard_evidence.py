"""Chụp lại ảnh bằng chứng cho demo VENT-003 (chỉ trang tĩnh cục bộ, không gọi ThingsBoard).

Chạy từ gốc repo: python3 tests/capture_dashboard_evidence.py
"""
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from webdriver_support import ROOT, Browser, StaticServer  # noqa: E402

EVIDENCE = ROOT / "docs/ventilation/dashboard/evidence"
SHOTS = [
    ("default", 1920, 1080, "default-1920.png"),
    ("vent_detail", 1920, 1080, "vent-detail-1920.png"),
    ("vent_history", 1920, 1080, "vent-history-1920.png"),
    ("vent_alarms", 1920, 1080, "vent-alarms-1920.png"),
    ("default", 390, 844, "default-390.png"),
    ("vent_detail", 390, 844, "vent-detail-390.png"),
    ("vent_settings", 1920, 1080, "vent-settings-1920.png"),
    ("vent_settings", 390, 844, "vent-settings-390.png"),
]


def main():
    # Firefox snap không ghi được vào mọi thư mục; chụp vào thư mục tạm rồi chép sang repo.
    with StaticServer() as server, tempfile.TemporaryDirectory(dir=pathlib.Path.home()) as tmp:
        browser = Browser()
        try:
            for state, width, height, name in SHOTS:
                browser.resize(width, height)
                browser.open(server.base_url + "/dashboard/index.html#" + state)
                browser.wait_for("return !!document.querySelector('.state-tabs a.active[href=\"#%s\"]')" % state)
                target = pathlib.Path(tmp) / name
                browser.screenshot_full(target)
                (EVIDENCE / name).write_bytes(target.read_bytes())
                print("captured", name)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
