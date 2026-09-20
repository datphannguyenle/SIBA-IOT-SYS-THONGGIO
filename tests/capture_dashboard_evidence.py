"""Chụp lại ảnh bằng chứng cho demo VENT-003 (chỉ trang tĩnh cục bộ, không gọi ThingsBoard).

Chạy từ gốc repo: python3 tests/capture_dashboard_evidence.py
"""
import base64
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from webdriver_support import ROOT, Browser, StaticServer  # noqa: E402

EVIDENCE = ROOT / "docs/ventilation/dashboard/evidence"
SHOTS = [(state, width, height, 'vent008-%s-%s.png' % (state.replace('_', '-'), width))
         for width, height in ((1920, 1080), (1366, 768), (820, 1180), (390, 844))
         for state in ('default', 'vent_detail', 'vent_history', 'vent_alarms', 'vent_settings')]
ELEMENT_KEY = 'element-6066-11e4-a52e-4f735466cecf'


def main():
    # Firefox snap không ghi được vào mọi thư mục; chụp vào thư mục tạm rồi chép sang repo.
    with StaticServer() as server, tempfile.TemporaryDirectory(dir=pathlib.Path.home()) as tmp:
        browser = Browser()
        results = []
        try:
            for state, width, height, name in SHOTS:
                url = server.base_url + '/dashboard/index.html#' + state
                frame = None
                if width == 390:
                    browser.resize(1280, 1000)
                    browser._session('POST', '/url', {'url': server.base_url + '/deploy/thingsboard/mobile_frame.html'})
                    frame = browser._session('POST', '/element', {'using': 'css selector', 'value': '#device'})[ELEMENT_KEY]
                    browser._session('POST', '/frame', {'id': {ELEMENT_KEY: frame}})
                    browser.run('location.href=arguments[0]', url)
                else:
                    browser.resize(width, height)
                    browser.resize(width, height + height - browser.run('return innerHeight'))
                    browser.open(url)
                browser.wait_for("return !!document.querySelector('.state-tabs a.active[href=\"#%s\"]')" % state)
                if state == 'default':
                    browser.wait_for('var img=document.querySelector(".barn-illustration img"); return img && img.complete && img.naturalWidth > 0')
                observed = browser.run('return {width:innerWidth,height:innerHeight,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth}')
                if observed != {'width': width, 'height': height, 'overflow': 0}:
                    raise AssertionError((name, observed))
                target = pathlib.Path(tmp) / name
                if frame:
                    browser._session('POST', '/frame/parent', {})
                    target.write_bytes(base64.b64decode(browser._session('GET', '/element/%s/screenshot' % frame)))
                else:
                    browser.screenshot_full(target)
                (EVIDENCE / name).write_bytes(target.read_bytes())
                results.append(dict(observed, state=state, screenshot=name))
                print("captured", name)
            (EVIDENCE / 'vent008_capture.json').write_text(json.dumps(results, indent=2) + '\n')
        finally:
            browser.close()


if __name__ == "__main__":
    main()
