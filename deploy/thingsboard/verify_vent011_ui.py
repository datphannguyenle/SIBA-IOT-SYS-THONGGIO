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

ROOT_SELECTOR = ".vent-modular-root"
EXPECTED_BARNS = 7


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
            if stale == offline:
                report["problems"].append("STALE và OFFLINE hiện giống nhau")
            if "Ngoại tuyến" in stale:
                report["problems"].append("STALE bị báo là mất kết nối")
            if "Ngoại tuyến" not in offline:
                report["problems"].append("OFFLINE không báo mất kết nối")
            # Dữ liệu vừa bơm phải là hiện hành; attribute `active` cũ không được làm cả nhà thành cũ.
            for name, row in (("NORMAL", normal), ("BOUNDARY", boundary)):
                if "Dữ liệu cũ" in row:
                    report["problems"].append("%s bị báo dữ liệu cũ dù telemetry vừa về: %s" % (name, row))
            if "Dữ liệu cũ" not in stale:
                report["problems"].append("STALE không báo dữ liệu cũ: %s" % stale)

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
    if report["problems"]:
        print("VẤN ĐỀ:")
        for problem in report["problems"]:
            print(" -", problem)
        raise SystemExit(1)
    print("XÁC MINH UI: ĐẠT")


if __name__ == "__main__":
    main()
