"""Chụp bằng chứng VENT-010 từ harness cục bộ (không chạm ThingsBoard).

  python3 tests/capture_vent010_evidence.py
"""
import pathlib
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from webdriver_support import ROOT, Browser, StaticServer  # noqa: E402

EVIDENCE = ROOT / "docs/ventilation/dashboard/evidence"
# (chế độ nguồn, state, rộng, cao, tên file)
SHOTS = [
    ("demo", "default", 1366, 768, "vent010-demo-default-1366.png"),
    ("demo", "vent_detail", 1366, 768, "vent010-demo-vent-detail-1366.png"),
    ("live", "default", 1366, 768, "vent010-live-empty-default-1366.png"),
    ("subscription", "vent_detail", 1366, 768, "vent010-subscription-vent-detail-1366.png"),
    ("demo", "default", 390, 844, "vent010-demo-default-390.png"),
]


def main():
    with StaticServer() as server, tempfile.TemporaryDirectory(dir=pathlib.Path.home()) as tmp:
        browser = Browser()
        try:
            for mode, state, width, height, name in SHOTS:
                browser.resize(width, height)
                browser._session("POST", "/url", {"url": "%s/dashboard/modular-preview.html#%s" % (server.base_url, state)})
                browser.wait_for("return !!document.getElementById('test-source')")
                browser.run("var s = document.getElementById('test-source'); s.value = arguments[0];"
                            "s.dispatchEvent(new Event('change'));", mode)
                time.sleep(1.2)
                target = pathlib.Path(tmp) / name
                browser.screenshot_full(target)
                EVIDENCE.mkdir(parents=True, exist_ok=True)
                (EVIDENCE / name).write_bytes(target.read_bytes())
                print("captured", name)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
