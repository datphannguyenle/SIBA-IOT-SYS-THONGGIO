#!/usr/bin/env python3
"""VENT-011 — xác minh CHỈ ĐỌC dashboard SIM trên trình duyệt thật.

  python3 deploy/thingsboard/verify_vent011_ui.py

Chỉ đăng nhập qua form rồi điều hướng/click/đọc DOM. Không gọi API ghi, không telemetry,
không RPC, không attribute. Không in mật khẩu hay token.

Ba điều test cục bộ không thay được, kiểm ở đây:
  1. Số 0 THẬT hiện là 0, không phải "--"      (SIM-VEN-BOUNDARY)
  2. STALE khác OFFLINE                         (SIM-VEN-STALE / SIM-VEN-OFFLINE)
  3. Click một nhà thì widget chi tiết đổi đúng thiết bị đó
"""
import json
import pathlib
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tests"))
from webdriver_support import Browser  # noqa: E402
from vent_demo_common import EVIDENCE_DIR, TB_URL, write_json  # noqa: E402
from verify_vent_demo_ui import login  # noqa: E402
import vent011_sim as sim  # noqa: E402
from build_vent_live import FRESHNESS_MONITORING_MS  # noqa: E402
from vent011_deploy import SimTB  # noqa: E402

ROOT_SELECTOR = ".vent-modular-root"
EXPECTED_BARNS = 7


def platform_state(manifest):
    """Sự thật từ nền tảng: tuổi telemetry và cờ active của từng thiết bị.

    Bộ kiểm đối chiếu giao diện với số liệu này, chứ KHÔNG giả định `feed` còn đang chạy.
    TB tự đặt active = false sau ngưỡng không hoạt động, nên cả tuổi dữ liệu lẫn kết nối đều
    thay đổi theo thời gian thực.
    """
    tb = SimTB()
    now = int(time.time() * 1000)
    state = {}
    for name, info in manifest["devices"].items():
        body = tb.get_ok("/api/plugins/telemetry/DEVICE/%s/values/timeseries?keys=fanStage"
                         % info["id"])
        series = body.get("fanStage") or []
        # TB trả {"value": ""} với ts HIỆN TẠI cho khóa chưa từng ghi; coi đó là chưa có dữ liệu,
        # không phải dữ liệu mới 0 phút tuổi.
        point = series[0] if series else None
        age = None if point is None or point.get("value") in (None, "") else now - point["ts"]
        attributes = tb.get_ok("/api/plugins/telemetry/DEVICE/%s/values/attributes/SERVER_SCOPE"
                               % info["id"])
        active = {item["key"]: item["value"] for item in attributes}.get("active")
        alarms = tb.get_ok("/api/alarm/DEVICE/%s?pageSize=100&page=0&searchStatus=ACTIVE"
                           % info["id"])
        state[info["scenario"]] = {"age": age, "active": active,
                                   "activeAlarms": sorted(a["type"] for a in alarms["data"])}
    return state


def open_dashboard(browser, dash_id):
    browser._session("POST", "/url", {"url": "%s/dashboards/%s" % (TB_URL, dash_id)})
    browser.wait_for("return !!document.querySelector('%s .vm-barn')" % ROOT_SELECTOR, timeout=120)
    time.sleep(2.5)


def read_overview(browser):
    return browser.run("""
      var out = {kpis: {}, barns: [], notice: null};
      document.querySelectorAll('.vent-modular-root .vm-kpis .vm-card').forEach(function (card) {
        out.kpis[card.querySelector('p').textContent.trim()] = card.querySelector('b').textContent.trim();
      });
      document.querySelectorAll('.vent-modular-root .vm-barn').forEach(function (node) {
        var spans = [].map.call(node.querySelectorAll('span'), function (s) { return s.textContent.trim(); });
        out.barns.push({label: node.querySelector('b').textContent.trim(),
                        entityId: node.getAttribute('data-barn-id'),
                        entityType: node.getAttribute('data-barn-entity-type'),
                        lines: spans});
      });
      var notice = document.querySelector('.vent-modular-root .vm-notice');
      out.notice = notice ? notice.textContent.trim() : null;
      return out;
    """)


def click_barn(browser, label):
    clicked = browser.run("""
      var nodes = document.querySelectorAll('.vent-modular-root .vm-barn');
      for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].querySelector('b').textContent.trim().indexOf(arguments[0]) === 0) {
          nodes[i].click(); return nodes[i].getAttribute('data-barn-id');
        }
      }
      return null;
    """, label)
    if not clicked:
        raise RuntimeError("Không tìm thấy thẻ nhà %s" % label)
    browser.wait_for("return !!document.querySelector('.vent-modular-root .vm-kpis')"
                     " && !document.querySelector('.vent-modular-root .vm-barn')", timeout=60)
    time.sleep(2.5)
    return clicked


def read_detail(browser):
    return browser.run("""
      var root = document.querySelectorAll('.vent-modular-root'), out = {panels: [], text: ''};
      root.forEach(function (node) { out.text += ' ' + node.textContent; });
      document.querySelectorAll('.vent-modular-root .vm-card').forEach(function (card) {
        var name = card.querySelector('p'), value = card.querySelector('b');
        if (name && value) out.panels.push([name.textContent.trim(), value.textContent.trim()]);
      });
      var head = document.querySelector('.vent-modular-root h2');
      out.heading = head ? head.textContent.trim() : null;
      return out;
    """)


def go_tab(browser, state):
    """ Đi sang state khác bằng chính nav của widget header, không dùng URL. """
    moved = browser.run("""
      var tab = document.querySelector('.vent-modular-root .vm-tabs [data-nav="' + arguments[0] + '"]');
      if (!tab) return false;
      tab.click(); return true;
    """, state)
    if not moved:
        raise RuntimeError("Không thấy tab %s" % state)
    time.sleep(3.0)


def read_state(browser):
    return browser.run("""
      var out = {text: '', headings: [], rows: 0, firstRow: [], notices: [],
                 writable: 0, settingsFilled: 0, settingsMissing: 0};
      document.querySelectorAll('.vent-modular-root').forEach(function (node) {
        out.text += ' ' + node.innerText;
      });
      document.querySelectorAll('.vent-modular-root h1, .vent-modular-root h2').forEach(function (h) {
        out.headings.push(h.textContent.trim());
      });
      document.querySelectorAll('.vent-modular-root .vm-notice').forEach(function (n) {
        out.notices.push(n.textContent.trim());
      });
      var body = document.querySelectorAll('.vent-modular-root table tbody tr');
      out.rows = body.length;
      out.tableText = '';
      body.forEach(function (tr) { out.tableText += ' ' + tr.textContent; });
      if (body.length) {
        out.firstRow = [].map.call(body[0].querySelectorAll('td'), function (td) {
          return td.textContent.trim();
        });
      }
      // Chỉ xem: ngoài hộp tìm kiếm thì không được có ô nhập hay điều khiển ghi nào.
      document.querySelectorAll('.vent-modular-root input, .vent-modular-root select, .vent-modular-root textarea').forEach(function (el) {
        if (el.tagName === 'INPUT' && el.getAttribute('type') === 'search') return;
        out.writable += 1;
      });
      var probe = document.querySelector('.vent-modular-root[data-vent-diagnostic]');
      out.diagnostic = probe ? probe.getAttribute('data-vent-diagnostic') : null;
      document.querySelectorAll('.vent-modular-root [data-setting-key]').forEach(function (el) {
        var text = el.textContent.trim();
        if (text === '--' || text === '') out.settingsMissing += 1; else out.settingsFilled += 1;
      });
      return out;
    """)


def back_to_overview(browser):
    browser.run("""
      var tab = document.querySelector('.vent-modular-root [data-nav="default"]');
      if (tab) tab.click();
    """)
    browser.wait_for("return !!document.querySelector('.vent-modular-root .vm-barn')", timeout=60)
    time.sleep(2.0)


def main():
    manifest = json.loads((pathlib.Path(__file__).resolve().parents[2]
                           / "deploy/thingsboard/vent011_manifest.json").read_text(encoding="utf-8"))
    dash_id = manifest["dashboard"]["id"]
    report = {"task": "VENT-011", "dashboard": dash_id, "problems": []}
    platform = platform_state(manifest)
    ages = {scenario: info["age"] for scenario, info in platform.items()}

    with tempfile.TemporaryDirectory(dir=pathlib.Path.home()) as tmp:
        browser = Browser()
        try:
            browser.resize(1600, 1000)
            login(browser)
            open_dashboard(browser, dash_id)
            overview = read_overview(browser)
            report["overview"] = overview

            labels = [barn["label"] for barn in overview["barns"]]
            if len(labels) != EXPECTED_BARNS:
                report["problems"].append("số nhà = %d, mong đợi %d" % (len(labels), EXPECTED_BARNS))
            if overview["notice"]:
                report["problems"].append("còn thông báo trạng thái rỗng: %s" % overview["notice"])
            for barn in overview["barns"]:
                if barn["entityType"] != "DEVICE" or not barn["entityId"]:
                    report["problems"].append("thẻ %s thiếu entityId/entityType" % barn["label"])

            # Nhãn thẻ nhà là label của thiết bị (tiếng Việt), không phải tên kịch bản.
            def barn_of(scenario):
                wanted = sim.SCENARIO_LABEL[scenario]
                for barn in overview["barns"]:
                    if barn["label"].startswith(wanted):
                        return barn
                report["problems"].append("không thấy nhà kịch bản %s (%s)" % (scenario, wanted))
                return {"label": None, "lines": []}

            # 1. Số 0 thật: cấp phải là "0", tuyệt đối không phải "--".
            boundary = " ".join(barn_of("BOUNDARY")["lines"])
            if "Cấp: 0" not in boundary:
                report["problems"].append("BOUNDARY không hiện cấp 0: %s" % boundary)
            if "Cấp: --" in boundary:
                report["problems"].append("BOUNDARY hiện -- thay vì 0")

            # 2. STALE khác OFFLINE.
            stale = " ".join(barn_of("STALE")["lines"])
            offline = " ".join(barn_of("OFFLINE")["lines"])
            unknown = " ".join(barn_of("UNKNOWN")["lines"])
            normal = " ".join(barn_of("NORMAL")["lines"])
            report["rows"] = {"NORMAL": normal, "BOUNDARY": boundary, "STALE": stale,
                              "OFFLINE": offline, "UNKNOWN": unknown}
            report["platform"] = platform
            if stale == offline:
                report["problems"].append("STALE và OFFLINE hiện giống nhau")
            # Kết nối phải khớp cờ active của nền tảng, không phải khớp điều ta mong đợi.
            for scenario, row in (("NORMAL", normal), ("BOUNDARY", boundary), ("STALE", stale),
                                  ("OFFLINE", offline), ("UNKNOWN", unknown)):
                active = platform.get(scenario, {}).get("active")
                offline_label = "Ngoại tuyến" in row
                if active is True and offline_label:
                    report["problems"].append("%s: active=true mà giao diện báo mất kết nối" % scenario)
                if active is False and not offline_label:
                    report["problems"].append("%s: active=false mà giao diện không báo mất kết nối"
                                              % scenario)
            # OFFLINE chưa bao giờ gửi gì, nên dù feed có chạy hay không nó vẫn phải là ngoại tuyến.
            if platform.get("OFFLINE", {}).get("active") is not False:
                report["problems"].append("SIM-VEN-OFFLINE lẽ ra không bao giờ active")
            # Đối chiếu nhãn độ tươi với TUỔI THẬT của telemetry, cả hai chiều. Không giả định
            # rằng `feed` còn đang chạy; attribute `active` cũ không được làm cả nhà thành cũ.
            report["data_age_minutes"] = {k: (None if v is None else round(v / 60000.0, 1))
                                          for k, v in ages.items()}
            for scenario, row in (("NORMAL", normal), ("BOUNDARY", boundary), ("STALE", stale)):
                age = ages.get(scenario)
                if age is None:
                    report["problems"].append("%s không có telemetry nào" % scenario)
                    continue
                fresh_expected = age <= FRESHNESS_MONITORING_MS
                shows_stale = "Dữ liệu cũ" in row
                if fresh_expected and shows_stale:
                    report["problems"].append(
                        "%s: telemetry %0.1f phút tuổi (trong ngưỡng %d phút) mà bị báo dữ liệu cũ"
                        % (scenario, age / 60000.0, FRESHNESS_MONITORING_MS // 60000))
                if not fresh_expected and not shows_stale:
                    report["problems"].append(
                        "%s: telemetry %0.1f phút tuổi (quá ngưỡng) mà vẫn báo hiện hành"
                        % (scenario, age / 60000.0))
                if not fresh_expected and scenario in ("NORMAL", "BOUNDARY"):
                    report.setdefault("notes", []).append(
                        "%s cũ %0.1f phút: `feed` không còn chạy, nên nhãn dữ liệu cũ là đúng"
                        % (scenario, age / 60000.0))

            # 3. Click một nhà thì widget chi tiết bám đúng thiết bị đó.
            # Chọn FAULT vì số liệu của nó khác hẳn các nhà còn lại (cấp 9, 32.0 °C) nên nếu
            # widget chi tiết bám sai thiết bị thì thấy ngay.
            target = barn_of("FAULT")
            if not target["label"]:
                raise SystemExit("Không có thẻ nhà nào để click: %s" % report["problems"])
            clicked_id = click_barn(browser, target["label"])
            detail = read_detail(browser)
            report["detail"] = {"clicked": target["label"], "entityId": clicked_id,
                               "heading": detail["heading"], "cards": detail["panels"][:8]}
            if not target["label"] or target["label"] not in detail["text"]:
                report["problems"].append("màn chi tiết không nhắc tên nhà đã chọn")
            if "MINH HỌA" in detail["text"]:
                report["problems"].append("màn chi tiết vẫn dán nhãn MINH HỌA ở chế độ live")
            cards = dict(detail["panels"])
            indoor = cards.get("Nhiệt độ trong nhà", "")
            if not indoor.startswith("32"):
                report["problems"].append("nhà FAULT phải hiện 32.x °C, đang hiện %r" % indoor)
            if "--" == indoor:
                report["problems"].append("widget chi tiết không nhận được dữ liệu của nhà đã chọn")

            shot = pathlib.Path(tmp) / "vent011-detail.png"
            browser.screenshot_full(shot)
            (EVIDENCE_DIR / "vent011-live-detail-1600.png").write_bytes(shot.read_bytes())

            # --- Ba màn còn lại, vẫn trong ngữ cảnh nhà FAULT đã chọn ---
            states = {}
            for state in ("vent_history", "vent_alarms", "vent_settings"):
                go_tab(browser, state)
                info = read_state(browser)
                states[state] = {"headings": info["headings"], "rows": info["rows"],
                                 "firstRow": info["firstRow"], "notices": info["notices"],
                                 "writable": info["writable"],
                                 "settingsFilled": info["settingsFilled"],
                                 "settingsMissing": info["settingsMissing"],
                                 "tableText": info["tableText"],
                                 "diagnostic": info.get("diagnostic")}
                if info["writable"]:
                    report["problems"].append(
                        "%s có %d điều khiển ghi được, màn này phải chỉ xem"
                        % (state, info["writable"]))
                if target["label"] not in info["text"]:
                    report["problems"].append("%s mất tên nhà đã chọn" % state)
                shot = pathlib.Path(tmp) / (state + ".png")
                browser.screenshot_full(shot)
                (EVIDENCE_DIR / ("vent011-live-%s-1600.png" % state.replace("_", "-"))
                 ).write_bytes(shot.read_bytes())
            report["states"] = states

            history = states["vent_history"]
            if history["rows"] < 10:
                report["problems"].append("màn Lịch sử chỉ có %d dòng, đã nạp 3 giờ dữ liệu"
                                          % history["rows"])
            elif history["firstRow"][0] == "--":
                report["problems"].append("màn Lịch sử thiếu mốc thời gian")
            elif not any(cell not in ("--", "") for cell in history["firstRow"][1:]):
                report["problems"].append("màn Lịch sử không có giá trị nào: %s"
                                          % history["firstRow"])

            settings_state = states["vent_settings"]
            if settings_state["settingsFilled"] < 100:
                report["problems"].append(
                    "màn Cài đặt chỉ đọc được %d giá trị (thiếu %d), đã ghi 224 khóa"
                    % (settings_state["settingsFilled"], settings_state["settingsMissing"]))

            # Bảng Cảnh báo phải khớp alarm ĐANG HOẠT ĐỘNG của đúng nhà đã chọn. Chưa có rule
            # thì bảng rỗng là đúng; điều sai là bịa ra dòng, hoặc hiện alarm của nhà khác.
            alarm_state = states["vent_alarms"]
            expected = platform.get("FAULT", {}).get("activeAlarms") or []
            report["alarm_rows"] = alarm_state["rows"]
            report["alarm_expected"] = expected
            if alarm_state["rows"] < len(expected):
                report["problems"].append(
                    "màn Cảnh báo có %d dòng nhưng nhà FAULT đang có %d alarm: %s"
                    % (alarm_state["rows"], len(expected), expected))
            for alarm_type in expected:
                if alarm_type not in alarm_state.get("tableText", ""):
                    report["problems"].append("màn Cảnh báo thiếu alarm %r" % alarm_type)
            # Không được hiện alarm của nhà khác: BOUNDARY có alarm riêng, FAULT không có nó
            # thì bảng cũng không được có.
            foreign = [a for a in (platform.get("BOUNDARY", {}).get("activeAlarms") or [])
                       if a not in expected]
            for alarm_type in foreign:
                if alarm_type in alarm_state.get("tableText", ""):
                    report["problems"].append(
                        "màn Cảnh báo hiện alarm %r của nhà khác" % alarm_type)

            go_tab(browser, "vent_detail")
            back_to_overview(browser)
            shot = pathlib.Path(tmp) / "vent011-overview.png"
            browser.screenshot_full(shot)
            (EVIDENCE_DIR / "vent011-live-overview-1600.png").write_bytes(shot.read_bytes())
        finally:
            browser.close()

    write_json(EVIDENCE_DIR / "vent011_ui_verify.json", report)
    print(json.dumps(report.get("rows", {}), ensure_ascii=False, indent=2))
    print("nhà:", [b["label"] for b in report["overview"]["barns"]])
    print("KPI:", report["overview"]["kpis"])
    print("chi tiết:", report.get("detail", {}).get("heading"),
          "| clicked", report.get("detail", {}).get("clicked"))
    for state, info in (report.get("states") or {}).items():
        extra = ("cài đặt đọc được %d/%d" % (info["settingsFilled"],
                                             info["settingsFilled"] + info["settingsMissing"])
                 if info["settingsFilled"] or info["settingsMissing"] else "")
        print("%-14s dòng=%-4d ô ghi được=%d %s" % (state, info["rows"], info["writable"], extra))
        if info["notices"]:
            print("               ghi chú:", info["notices"][:2])
    print("tuổi telemetry (phút):", report.get("data_age_minutes"))
    print("active theo nền tảng:", {k: v["active"] for k, v in platform.items()})
    print("alarm đang hoạt động:", {k: v["activeAlarms"] for k, v in platform.items() if v["activeAlarms"]})
    print("bảng Cảnh báo:", report.get("alarm_rows"), "dòng · mong đợi",
          len(report.get("alarm_expected") or []))
    probe = ((report.get("states") or {}).get("vent_alarms") or {}).get("diagnostic")
    if probe:
        print("chẩn đoán widget cảnh báo:", probe)
    for note in report.get("notes") or []:
        print("ghi chú:", note)
    if report["problems"]:
        print("VẤN ĐỀ:")
        for problem in report["problems"]:
            print(" -", problem)
        raise SystemExit(1)
    print("XÁC MINH UI: ĐẠT")


if __name__ == "__main__":
    main()
