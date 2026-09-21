#!/usr/bin/env python3
"""VENT-008 — xác minh UI live v0.3 chỉ đọc bằng các phiên Firefox mới.

Chỉ chạy SAU KHI MAIN đã deploy widget/dashboard VENT-008:

  python3 deploy/thingsboard/verify_vent008_ui.py

Script chỉ đăng nhập qua form (POST /api/auth/login do trình duyệt thực hiện). Mọi
thao tác sau đó là điều hướng/click/read DOM; không gọi API ghi, telemetry, RPC hay
attribute. Không in hoặc lưu mật khẩu/token. Mỗi viewport dùng một Firefox profile
mới (tương đương hard refresh); viewport 390px chạy bên trong iframe thật vì Firefox
headless không thể thu nhỏ cửa sổ top-level xuống 390px một cách đáng tin cậy.
"""
import base64
import argparse
import json
import pathlib
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tests"))
from webdriver_support import Browser, StaticServer  # noqa: E402
from vent_demo_common import EVIDENCE_DIR, write_json  # noqa: E402
from verify_vent_demo_ui import ELEMENT_KEY, find, login, open_dashboard  # noqa: E402

DASHBOARD_ID = "b9ff4d70-b26a-11f1-83ad-9912edc644d2"
WIDGET_TYPE_ID = "b9fa9280-b26a-11f1-83ad-9912edc644d2"
STATES = ("default", "vent_detail", "vent_history", "vent_alarms", "vent_settings")
VIEWPORTS = (("1920x1080", 1920, 1080), ("1366x768", 1366, 768), ("820x1180", 820, 1180))
EVIDENCE_PREFIX = 'vent008'


STATE_CHECK = r"""
var state = arguments[0], root = document.querySelector('.vent-demo-root');
if (!root) return {missing: true};
var active = root.querySelector('.state-tabs a.active');
function mediaRulePresent() {
  function rules(list) {
    if (!list) return false;
    for (var i = 0; i < list.length; i += 1) {
      var rule = list[i], text = rule.cssText || '';
      if (/prefers-reduced-motion/.test(text) && /fan\.RUNNING/.test(text)) return true;
      try { if (rules(rule.cssRules)) return true; } catch (ignore) {}
    }
    return false;
  }
  for (var j = 0; j < document.styleSheets.length; j += 1) {
    try { if (rules(document.styleSheets[j].cssRules)) return true; } catch (ignore) {}
  }
  return false;
}
var info = {
  active: active && active.getAttribute('data-nav'),
  badge: (root.querySelector('.demo-badge') || {}).innerText,
  innerWidth: window.innerWidth,
  innerHeight: window.innerHeight,
  pageOverflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  widgetOverflowX: root.scrollWidth - root.clientWidth,
  widgetClientHeight: root.clientHeight,
  widgetScrollHeight: root.scrollHeight,
  widgetOverflowY: getComputedStyle(root).overflowY,
  controls: root.querySelectorAll('button,select,textarea,form').length,
  rawStates: [...root.querySelectorAll('[data-raw-state]')].map(function (el) {
    return {raw: el.getAttribute('data-raw-state'), text: el.textContent.trim(), cls: el.getAttribute('class') || ''};
  }),
  reducedMotionRule: mediaRulePresent(),
  runningAnimation: (function () {
    var blades = root.querySelector('.fan.RUNNING.quality-CURRENT.connectivity-ONLINE .fan-blades');
    return blades ? getComputedStyle(blades).animationName : null;
  }())
};
if (state === 'default') {
  var illustration = root.querySelector('.barn-illustration img');
  info.illustration = illustration && {loaded: illustration.complete && illustration.naturalWidth > 0,
    width: illustration.naturalWidth, height: illustration.naturalHeight,
    embedded: illustration.src.indexOf('data:image/webp;base64,') === 0};
  info.barns = [...root.querySelectorAll('.barn-card')].map(function (card) {
    return {id: card.getAttribute('data-barn-id'), label: card.querySelector('b').innerText};
  });
  info.filterInputs = root.querySelectorAll('[data-filter-input=barn]').length;
}
if (state === 'vent_detail') {
  info.selectedContext = (root.querySelector('.selected-barn-context') || {}).innerText || null;
  info.detailLayouts = root.querySelectorAll('.detail-layout').length;
}
if (state === 'vent_history') {
  function path(cls) { var node = root.querySelector('.chart .' + cls); return node && node.getAttribute('d') || ''; }
  info.history = {insideMoves: (path('inside').match(/M/g) || []).length, outsideMoves: (path('outside').match(/M/g) || []).length,
    perceivedMoves: (path('perceived').match(/M/g) || []).length, humidityMoves: (path('humidity').match(/M/g) || []).length,
    leftAxes: root.querySelectorAll('.chart .axis-left').length, rightAxes: root.querySelectorAll('.chart .axis-right').length,
    samples: [...root.querySelectorAll('.chart-sample')].map(function (sample) { return {
      tabindex: sample.getAttribute('tabindex'), role: sample.getAttribute('role'), label: sample.getAttribute('aria-label'),
      title: (sample.querySelector('title') || {}).textContent || '', points: sample.querySelectorAll('.chart-point').length}; })};
}
if (state === 'vent_alarms') {
  info.filterInputs = root.querySelectorAll('[data-filter-input=alarm]').length;
  info.alarmRows = root.querySelectorAll('.data-table tbody tr').length;
}
if (state === 'vent_settings') {
  info.filterInputs = root.querySelectorAll('[data-filter-input=settings]').length;
  info.settings = {cells: root.querySelectorAll('[data-setting-key]').length,
    unique: new Set([...root.querySelectorAll('[data-setting-key]')].map(function (item) { return item.getAttribute('data-setting-key'); })).size,
    nonFilterInputs: root.querySelectorAll('input:not([data-filter-input=settings])').length};
}
return info;
"""


def go_state(browser, state):
    current = browser.run("var root=document.querySelector('.vent-demo-root'),active=root&&root.querySelector('.state-tabs a.active');return root&&root.getAttribute('data-vent-state')||(active&&active.getAttribute('data-nav'))")
    if current == state:
        return
    browser.run("document.querySelector('.vent-demo-root a[data-nav=\"%s\"]').click()" % state)
    browser.wait_for("var root=document.querySelector('.vent-demo-root'),active=root&&root.querySelector('.state-tabs a.active');return root&&root.getAttribute('data-vent-state')==='%s'&&(active?active.getAttribute('data-nav')==='%s':%s)" % (state,state,'true' if state == 'default' else 'false'),
                     timeout=60)
    time.sleep(1)


def validate(state, info, expected_width=None):
    problems = []
    if info.get("missing"):
        return ["widget root missing"]
    if state == 'default' and info["active"] is not None:
        problems.append("overview must not show house menu")
    if state != 'default' and info["active"] != state:
        problems.append("active tab")
    if info["badge"] != "DEMO DATA":
        problems.append("demo badge")
    if expected_width is not None and info["innerWidth"] != expected_width:
        problems.append("innerWidth %s != %s" % (info["innerWidth"], expected_width))
    if info["pageOverflowX"] > 0 or info["widgetOverflowX"] > 0:
        problems.append("horizontal overflow")
    if expected_width is not None and expected_width > 1100:
        if info["widgetScrollHeight"] > info["widgetClientHeight"] + 1 or info["widgetOverflowY"] != "hidden":
            problems.append("desktop root vertical scroll")
    if not info["reducedMotionRule"]:
        problems.append("reduced-motion fan safety rule")
    if state == "default" and info.get("illustration") != {"loaded": True, "width": 1536, "height": 1024, "embedded": True}:
        problems.append("original embedded illustration")
    if state == "default" and info.get("active") is not None:
        problems.append("overview house menu visible")
    if state == "vent_detail" and info["runningAnimation"] != "vent-fan-spin":
        problems.append("current online running fan animation")
    if state == "vent_detail" and not any(item["raw"] == "RUNNING" and item["text"] == "Đang chạy"
                                          and "status-RUNNING" in item["cls"] for item in info["rawStates"]):
        problems.append("Vietnamese visible state / raw RUNNING attribute")
    if state == "vent_history":
        history = info["history"]
        if (history["insideMoves"], history["outsideMoves"], history["perceivedMoves"], history["humidityMoves"]) != (2, 1, 1, 1):
            problems.append("history series gaps")
        if (history["leftAxes"], history["rightAxes"]) != (4, 4):
            problems.append("history dual axes")
        if not history["samples"] or not all(sample["tabindex"] == "0" and sample["role"] == "img" and sample["label"] and sample["title"] and sample["points"] for sample in history["samples"]):
            problems.append("keyboard chart tooltip")
    if state == "vent_alarms" and (info["controls"] or info["filterInputs"] != 1 or not info["alarmRows"]):
        problems.append("alarms read-only/filter")
    if state == "vent_settings":
        settings = info["settings"]
        if info["controls"] or info["filterInputs"] != 1 or settings != {"cells": 224, "unique": 224, "nonFilterInputs": 0}:
            problems.append("224 settings read-only/filter")
    return problems


def screenshot_frame(browser, target):
    browser._session("POST", "/frame/parent", {})
    png = browser._session("GET", "/element/%s/screenshot" % find(browser, "#device"))
    target.write_bytes(base64.b64decode(png))
    browser._session("POST", "/frame", {"id": {ELEMENT_KEY: find(browser, "#device")}})


def check_all_states(browser, label, temporary_dir, shoot, expected_width=None):
    result = {"innerWidth": browser.run("return window.innerWidth"), "states": {}}
    for state in STATES:
        go_state(browser, state)
        if state == "default":
            browser.wait_for("var img=document.querySelector('.barn-illustration img'); return img && img.complete && img.naturalWidth > 0")
        info = browser.run(STATE_CHECK, state)
        if state == "vent_detail":
            info["fanActuallyMoves"] = browser._session("POST", "/execute/async", {"script": """
              var cb=arguments[arguments.length-1],el=document.querySelector('.fan.RUNNING .fan-blades');
              var start=getComputedStyle(el).transform;
              setTimeout(function(){cb(start!==getComputedStyle(el).transform);},220);
            """, "args": []})
        filename = "%s-%s-%s.png" % (EVIDENCE_PREFIX, label, state.replace("_", "-"))
        target = pathlib.Path(temporary_dir) / filename
        shoot(target)
        evidence = EVIDENCE_DIR / filename
        evidence.write_bytes(target.read_bytes())
        problems = validate(state, info, expected_width)
        if state == "vent_detail" and not info["fanActuallyMoves"]:
            problems.append("fan transform did not change over time")
        result["states"][state] = {"problems": problems, "observed": info, "screenshot": filename}
    return result


def verify_barn_navigation(browser):
    go_state(browser, "default")
    barns = browser.run("return [...document.querySelectorAll('.vent-demo-root .barn-card')].map(function (card) { return {id:card.getAttribute('data-barn-id'), label:card.querySelector('b').firstChild.textContent.trim()}; })")
    if len(barns) < 2:
        return {"problems": ["insufficient barn cards"]}
    browser.run("document.querySelectorAll('.vent-demo-root .barn-card')[1].click()")
    browser.wait_for("return !!document.querySelector('.vent-demo-root .selected-barn-context')", timeout=60)
    context = browser.run("var root=document.querySelector('.vent-demo-root'); return {label:root.querySelector('.selected-barn-context h2').textContent.trim(), text:root.querySelector('.selected-barn-context').innerText, detail:root.querySelectorAll('.detail-layout').length};")
    problems = []
    if barns[1]["label"] != context["label"] or context["detail"]:
        problems.append("barn navigation context")
    browser.run("document.querySelector('.selected-barn-context [data-barn-id]').click()")
    browser.wait_for("return !!document.querySelector('.detail-layout')", timeout=60)
    recovered = browser.run("return document.querySelector('.detail-main h2').innerText")
    if "ND2-1" not in recovered:
        problems.append("same-state sample recovery")
    return {"selected": barns[1], "context": context, "sampleRecovery": recovered, "problems": problems}


def run_desktop(label, width, height, temporary_dir):
    browser = Browser(width, height)
    try:
        browser.resize(width, height + height - browser.run("return window.innerHeight"))
        login(browser)
        open_dashboard(browser, DASHBOARD_ID)
        result = check_all_states(browser, label, temporary_dir, browser.screenshot_full, expected_width=width)
        result["barnNavigation"] = verify_barn_navigation(browser)
        return result
    finally:
        browser.close()


def run_mobile(server, temporary_dir):
    browser = Browser(1280, 1000)
    try:
        browser._session("POST", "/url", {"url": server.base_url + "/deploy/thingsboard/mobile_frame.html"})
        browser._session("POST", "/frame", {"id": {ELEMENT_KEY: find(browser, "#device")}})
        login(browser, in_frame=True)
        open_dashboard(browser, DASHBOARD_ID, in_frame=True)
        result = check_all_states(browser, "390", temporary_dir, lambda target: screenshot_frame(browser, target), expected_width=390)
        result["barnNavigation"] = verify_barn_navigation(browser)
        return result
    finally:
        browser.close()


def main():
    global EVIDENCE_PREFIX
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-prefix', choices=('vent008', 'vent009'), default='vent008')
    EVIDENCE_PREFIX = parser.parse_args().evidence_prefix
    stamp = time.strftime("%Y%m%dT%H%M%S%z")
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    results = {"at": stamp, "dashboardId": DASHBOARD_ID, "widgetTypeId": WIDGET_TYPE_ID, "states": list(STATES),
               "method": "new Firefox session per viewport; UI login only; mobile inside 390x844 iframe", "viewports": {}}
    with tempfile.TemporaryDirectory(prefix="vent008-ui-", dir=pathlib.Path.home()) as temporary_dir, StaticServer() as server:
        for label, width, height in VIEWPORTS:
            results["viewports"][label] = run_desktop(label, width, height, temporary_dir)
        results["viewports"]["390x844"] = run_mobile(server, temporary_dir)
    results["ok"] = all(not check["problems"] for viewport in results["viewports"].values()
                        for check in viewport["states"].values()) and all(not viewport["barnNavigation"]["problems"] for viewport in results["viewports"].values())
    report = EVIDENCE_DIR / ("%s_ui_verification_%s.json" % (EVIDENCE_PREFIX, stamp))
    write_json(report, results)
    print(json.dumps({label: {state: check["problems"] for state, check in viewport["states"].items()}
                      for label, viewport in results["viewports"].items()}, ensure_ascii=False, indent=2))
    print("report:", report.name)
    print("ok:", results["ok"])
    if not results["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
