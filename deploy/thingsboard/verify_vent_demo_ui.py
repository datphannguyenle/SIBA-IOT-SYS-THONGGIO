#!/usr/bin/env python3
"""VENT-006 — xác minh UI thật trên ThingsBoard bằng Firefox headless (chỉ xem, không ghi).

Hồ sơ trình duyệt mới mỗi lần chạy (tương đương nạp lại cứng, không cache template cũ).
Đăng nhập qua form UI; mật khẩu lấy từ TB_PASSWORD hoặc file mật khẩu, không in, không lưu.

  python3 verify_vent_demo_ui.py
"""
import json
import pathlib
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tests"))
from webdriver_support import Browser, StaticServer  # noqa: E402
from vent_demo_common import EVIDENCE_DIR, MANIFEST, STATES, TB_URL, TB_USER, read_password, write_json  # noqa: E402

ELEMENT_KEY = "element-6066-11e4-a52e-4f735466cecf"
# --refinement: ghi ảnh/JSON mới, không ghi đè bằng chứng lần deploy đầu.
REFINEMENT = "--refinement" in sys.argv
PREFIX = "vent006r" if REFINEMENT else "vent006"
RESULT_NAME = "vent006_refinement_ui_verification.json" if REFINEMENT else "vent006_ui_verification.json"

STATE_CHECK = """
var state = arguments[0], root = document.querySelector('.vent-demo-root');
if (!root) return {missing: true};
var active = root.querySelector('.state-tabs a.active');
var out = {
  badge: (root.querySelector('.demo-badge') || {}).innerText,
  active: active && active.getAttribute('data-nav'),
  hash: location.hash,
  search: location.search,
  previewShell: document.querySelectorAll('.tb-preview-sidebar,.tb-preview-shell,.vent-demo-root .tb-topbar').length,
  platformSideMenus: document.querySelectorAll('tb-side-menu').length,
  pageOverflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  widgetOverflowX: root.scrollWidth - root.clientWidth,
  widgetHeight: root.clientHeight, viewportHeight: window.innerHeight,
  headerBg: getComputedStyle(root.querySelector('.vent-header')).backgroundColor,
  typography: (function () {
    function cs(sel) { var e = root.querySelector(sel); if (!e) return null; var s = getComputedStyle(e);
      return [s.fontWeight, s.lineHeight, s.fontFamily.split(',')[0].replace(/"/g, ''), s.fontSize]; }
    return {h2: cs('.panel__head h2'), h3: cs('.subsection-title'), p: cs('.panel__head p'), strong: cs('.vent-header__title'),
            kpi: cs('.kpi__value'), th: cs('.data-table th'), td: cs('.data-table td'), tdB: cs('.data-table td b')};
  })(),
  badgeCornersVisible: (function () {
    var r = root.querySelector('.demo-badge').getBoundingClientRect();
    return [[r.left + 2, r.top + 2], [r.right - 2, r.top + 2], [r.right - 2, r.bottom - 2], [r.left + 2, r.bottom - 2]].map(function (pt) {
      var e = document.elementFromPoint(pt[0], pt[1]); return !!(e && e.closest('.demo-badge')); });
  })(),
  text: root.innerText.slice(0, 4000)
};
if (state === 'default') {
  out.identityTags = [...root.querySelectorAll('.barn-card em')].map(e => e.innerText);
}
if (state === 'vent_detail') {
  out.fans = [...root.querySelectorAll('.fan')].map(g => g.getAttribute('class'));
  out.fanStrokes = [...root.querySelectorAll('.fan circle')].map(c => getComputedStyle(c).stroke);
  out.secondary = [...root.querySelectorAll('.secondary-row b')].map(b => b.innerText);
  out.stage = root.innerText.indexOf('4 / 6') >= 0;
}
if (state === 'vent_history') {
  out.indoorMoves = (root.querySelector('.chart .inside').getAttribute('d').match(/M/g) || []).length;
  out.perceivedPath = !!root.querySelector('.chart .perceived').getAttribute('d');
  out.missingCell = [...root.querySelectorAll('.data-table td')].some(td => td.innerText.trim() === '--');
}
if (state === 'vent_alarms') {
  out.controls = root.querySelectorAll('button,input,select,textarea').length;
  out.alarmTypes = [...root.querySelectorAll('.data-table tbody b')].map(b => b.innerText);
}
return out;
"""


def find(browser, css):
    return browser._session("POST", "/element", {"using": "css selector", "value": css})[ELEMENT_KEY]


def navigate(browser, url, in_frame):
    if in_frame:
        browser.run("location.href = arguments[0]", url)
    else:
        browser._session("POST", "/url", {"url": url})


def login(browser, in_frame=False):
    navigate(browser, TB_URL + "/login", in_frame)
    browser.wait_for("return !!document.querySelector('input[type=password]')", timeout=60)
    user = find(browser, "input[formcontrolname=username], input[type=email], input[name=username]")
    pwd = find(browser, "input[type=password]")
    browser._session("POST", "/element/%s/value" % user, {"text": TB_USER})
    browser._session("POST", "/element/%s/value" % pwd, {"text": read_password()})
    browser._session("POST", "/element/%s/click" % find(browser, "button[type=submit]"), {})
    browser.wait_for("return location.pathname.indexOf('/login') < 0", timeout=60)


def open_dashboard(browser, dash_id, in_frame=False):
    navigate(browser, "%s/dashboards/%s" % (TB_URL, dash_id), in_frame)
    browser.wait_for("return !!document.querySelector('.vent-demo-root .demo-badge')", timeout=90)
    if in_frame:
        browser.run("location.reload()")
        time.sleep(2)
    else:
        browser._session("POST", "/refresh", {})
    browser.wait_for("return !!document.querySelector('.vent-demo-root .demo-badge')", timeout=90)
    time.sleep(1.5)


def go_state(browser, state):
    if browser.run("var a=document.querySelector('.vent-demo-root .state-tabs a.active');return a&&a.getAttribute('data-nav')") == state:
        return
    browser.run("document.querySelector('.vent-demo-root .state-tabs a[data-nav=\"%s\"]').click()" % state)
    browser.wait_for("var a=document.querySelector('.vent-demo-root .state-tabs a.active');"
                     "return !!a && a.getAttribute('data-nav')==='%s'" % state, timeout=60)
    time.sleep(1.5)


def evaluate(state, info, mobile):
    problems = []
    if info.get("missing"):
        return ["widget root missing"]
    if info["badge"] != "DEMO DATA":
        problems.append("badge")
    if info["active"] != state:
        problems.append("active tab")
    if info["hash"]:
        problems.append("location.hash used")
    if info["previewShell"]:
        problems.append("preview shell present")
    if info["pageOverflowX"] > 0 or info["widgetOverflowX"] > 0:
        problems.append("horizontal overflow")
    if not mobile and info["platformSideMenus"] > 1:
        problems.append("duplicate platform side menu")
    if info["headerBg"] != "rgb(21, 39, 55)":
        problems.append("panel colour %s" % info["headerBg"])
    if not all(info["badgeCornersVisible"]):
        problems.append("DEMO badge covered %s" % info["badgeCornersVisible"])
    ty = info["typography"]
    if ty["h2"] and ty["h2"][:2] != ["700", "normal"]:
        problems.append("h2 typography %s" % ty["h2"])
    if ty["strong"][0] != "700":
        problems.append("title strong weight %s" % ty["strong"])
    if ty["p"] and ty["p"][1] != "normal":
        problems.append("p line-height %s" % ty["p"])
    if ty["h3"] and ty["h3"][0] != "700":
        problems.append("h3 weight %s" % ty["h3"])
    if ty["kpi"] and ty["kpi"][0] != "600":
        problems.append("kpi weight %s" % ty["kpi"])
    if ty["td"] and ty["td"][2:] != ["Arial", "14px"]:
        problems.append("table cell font %s" % ty["td"])
    if ty["tdB"] and ty["tdB"][0] != "700":
        problems.append("table b weight %s" % ty["tdB"])
    if state == "default" and info["identityTags"] != ["PILOT · DEMO", "DEMO", "DEMO", "DEMO", "SYNTHETIC", "SYNTHETIC"]:
        problems.append("identity tags %s" % info["identityTags"])
    if state == "vent_detail":
        if info["fans"] != ["fan RUNNING", "fan RUNNING", "fan RUNNING", "fan STOPPED", "fan UNKNOWN", "fan FAULT"]:
            problems.append("fan states")
        strokes = info["fanStrokes"]
        if not (strokes[0] == "rgb(46, 230, 168)" and strokes[3] == "rgb(96, 125, 139)" and strokes[5] == "rgb(255, 59, 66)"):
            problems.append("fan colours %s" % strokes)
        if info["secondary"] != ["--", "--", "--"] or not info["stage"]:
            problems.append("controller panel values")
        for value in ("27.8", "31.2", "29.1", "74"):
            if value not in info["text"]:
                problems.append("KPI %s" % value)
    if state == "vent_history" and (info["indoorMoves"] != 2 or not info["perceivedPath"] or not info["missingCell"]):
        problems.append("history gap/perceived")
    if state == "vent_alarms" and (info["controls"] != 0 or not info["alarmTypes"]):
        problems.append("alarm read-only")
    return problems


def check_states(browser, dash_id, tmp, label, mobile, shoot):
    viewport = {"innerWidth": browser.run("return window.innerWidth"), "states": {}}
    for state in STATES:
        go_state(browser, state)
        info = browser.run(STATE_CHECK, state)
        name = "%s-%s-%s.png" % (PREFIX, state.replace("_", "-"), label)
        target = pathlib.Path(tmp) / name
        shoot(target)
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        (EVIDENCE_DIR / name).write_bytes(target.read_bytes())
        problems = evaluate(state, info, mobile)
        info.pop("text", None)
        viewport["states"][state] = {"problems": problems, "observed": info, "screenshot": name}
    # Quay về default bằng tab để kiểm điều hướng hai chiều.
    go_state(browser, "default")
    viewport["returned_to_default"] = browser.run(STATE_CHECK, "default")["active"] == "default"
    return viewport


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dash_id = manifest["created"]["dashboard"]["id"]
    results = {"dashboard_id": dash_id, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "viewports": {},
               "method": "desktop: top-level window 1920x1080; mobile: TB inside a 390x844 iframe "
                         "(Firefox cannot shrink a window below ~500px), fresh profile = hard refresh"}
    with tempfile.TemporaryDirectory(dir=pathlib.Path.home()) as tmp, StaticServer() as server:
        browser = Browser(1920, 1080)
        try:
            login(browser)
            open_dashboard(browser, dash_id)
            results["viewports"]["1920x1080"] = check_states(browser, dash_id, tmp, "1920", False, browser.screenshot_full)

            browser._session("POST", "/url", {"url": server.base_url + "/deploy/thingsboard/mobile_frame.html"})
            frame = find(browser, "#device")
            def shoot_frame(target):
                browser._session("POST", "/frame/parent", {})
                png = browser._session("GET", "/element/%s/screenshot" % find(browser, "#device"))
                import base64
                target.write_bytes(base64.b64decode(png))
                browser._session("POST", "/frame", {"id": {ELEMENT_KEY: find(browser, "#device")}})
            browser._session("POST", "/frame", {"id": {ELEMENT_KEY: frame}})
            login(browser, in_frame=True)
            open_dashboard(browser, dash_id, in_frame=True)
            results["viewports"]["390x844"] = check_states(browser, dash_id, tmp, "390", True, shoot_frame)
        finally:
            browser.close()
    results["ok"] = all(not s["problems"] for v in results["viewports"].values() for s in v["states"].values()) and \
        all(v["returned_to_default"] for v in results["viewports"].values()) and \
        results["viewports"]["390x844"]["innerWidth"] == 390
    write_json(EVIDENCE_DIR / RESULT_NAME, results)
    print(json.dumps({k: {"innerWidth": vp["innerWidth"], "problems": {s: v["problems"] for s, v in vp["states"].items()}}
                      for k, vp in results["viewports"].items()}, ensure_ascii=False, indent=1))
    print("ok:", results["ok"])
    if not results["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
