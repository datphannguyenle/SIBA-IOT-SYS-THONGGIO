#!/usr/bin/env python3
"""VENT-006 — dựng payload widget type + dashboard DEMO từ nguồn repo (không gọi mạng).

Nguồn: widgets/ventilation-contract-v03.js, widgets/ventilation-adapter.js, dashboard/app.js, fixtures/ventilation/demo.json,
dashboard/thingsboard-reset.css, dashboard/dashboard.css, dashboard/thingsboard-widget.css.
Đầu ra (xác định, không timestamp): deploy/thingsboard/build/widget_type.json, dashboard.json.

  python3 deploy/thingsboard/build_vent_demo.py          # ghi file build
  python3 deploy/thingsboard/build_vent_demo.py --check  # báo lỗi nếu file build lệch nguồn
"""
import base64
import json
import re
import sys
import uuid

from vent_demo_common import (BUILD_DIR, DASHBOARD_TITLE, ROOT, STATES, WIDGET_FQN, WIDGET_FULL_FQN,
                              write_json)

STATE_NAMES = {"default": "Tổng quan thông gió (DEMO)", "vent_detail": "Giám sát thông gió (DEMO)",
               "vent_history": "Lịch sử thông gió (DEMO)", "vent_alarms": "Cảnh báo thông gió (DEMO)",
               "vent_settings": "Cài đặt thông gió · chỉ đọc (DEMO)"}
UUID_NS = uuid.UUID("7c1e8f3a-0b6d-4c1e-9a52-5e0d7a1f0006")
BG = "#0c1622"


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def scope_iife(source, name):
    # Hai file đều kết thúc bằng }(window)); đổi sang đối tượng cục bộ để không rò global trong TB.
    marker = "}(window));"
    if source.count(marker) != 1:
        raise SystemExit("%s: cần đúng một '%s'" % (name, marker))
    return source.replace(marker, "}(__vent));")


def strip_css_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def build_css():
    # Reset typography nạp trước để class của bản đã duyệt vẫn thắng ở cùng độ đặc hiệu.
    css = strip_css_comments(read("dashboard/thingsboard-reset.css") + "\n" + read("dashboard/dashboard.css") + "\n"
                             + read("dashboard/thingsboard-widget.css"))
    return "\n".join(line for line in css.splitlines() if line.strip()) + "\n"


def build_controller():
    fixture = json.loads(read("fixtures/ventilation/demo.json"))
    if fixture.get("demo") is not True:
        raise SystemExit("fixture phải có demo: true")
    return (
        "// SINH TỰ ĐỘNG bởi deploy/thingsboard/build_vent_demo.py (VENT-006). KHÔNG sửa trong Widget Editor.\n"
        "// Demo fixture cô lập: không datasource, không telemetry, không RPC, không ghi attribute.\n"
        "self.onInit = function () {\n"
        "  var __vent = {};\n"
        "  __vent.VentilationAssets = {barnIllustration: " + json.dumps("data:image/webp;base64," + base64.b64encode((ROOT / "dashboard/assets/ventilation-barn-v1.webp").read_bytes()).decode("ascii")) + "};\n"
        + scope_iife(read("widgets/ventilation-contract-v03.js"), "contract") + "\n"
        + scope_iife(read("widgets/ventilation-adapter.js"), "adapter") + "\n"
        + scope_iife(read("dashboard/app.js"), "app") + "\n"
        "  var FIXTURE = " + json.dumps(fixture, ensure_ascii=False, separators=(",", ":")) + ";\n"
        "  var ctx = self.ctx;\n"
        "  var container = ctx.$container[0].querySelector('.vent-demo-root');\n"
        "  var viewState = (ctx.settings && ctx.settings.viewState) || 'default';\n"
        "  var vm = __vent.VentilationAdapter.createViewModel(FIXTURE);\n"
        "  var stateParams = ctx.stateController.getStateParams ? ctx.stateController.getStateParams() : {};\n"
        "  var currentParams = {barnId: stateParams.barnId || (vm.barns[0] || {}).id};\n"
        "  function fitViewport() {\n"
        "    container.style.height = '100%';\n"
        "    if (window.innerWidth <= 1100) { container.classList.remove('vent-compact-height'); return; }\n"
        "    var viewportHeight = window.visualViewport ? Math.min(window.innerHeight, window.visualViewport.height) : window.innerHeight;\n"
        "    var top = Math.max(0, container.getBoundingClientRect().top);\n"
        "    var available = Math.max(420, Math.floor(viewportHeight - top));\n"
        "    var parentHeight = container.parentElement ? container.parentElement.clientHeight : available;\n"
        "    container.style.height = Math.min(parentHeight || available, available) + 'px';\n"
        "    container.classList.toggle('vent-compact-height', container.clientHeight < 760);\n"
        "  }\n"
        "  function draw() { fitViewport(); __vent.VentilationDashboard.render(container, vm, viewState, function (next, params) {\n"
        "    if (next === viewState && params && params.barnId === currentParams.barnId) return;\n"
        "    ctx.stateController.openState(next, params || {}, false);\n"
        "    if (next === viewState) { currentParams = params || {}; draw(); }\n"
        "  }, currentParams); requestAnimationFrame(fitViewport); }\n"
        "  draw();\n"
        "  self._ventFitViewport = fitViewport;\n"
        "  self._ventRedraw = viewState === 'vent_history' ? draw : null;\n"
        "  self._ventResizeObserver = typeof ResizeObserver === 'function' ? new ResizeObserver(fitViewport) : null;\n"
        "  if (self._ventResizeObserver) self._ventResizeObserver.observe(ctx.$container[0]);\n"
        "};\n"
        "self.onResize = function () { if (self._ventFitViewport) self._ventFitViewport(); if (self._ventRedraw) self._ventRedraw(); };\n"
        "self.onDestroy = function () { if (self._ventResizeObserver) self._ventResizeObserver.disconnect(); self._ventResizeObserver = null; self._ventFitViewport = null; self._ventRedraw = null; };\n"
    )


def widget_type_payload():
    default_config = {"datasources": [], "showTitle": False, "backgroundColor": BG, "color": "#edf5f9",
                      "padding": "0px", "settings": {"viewState": "default"}, "title": "SIBA vent demo view"}
    return {
        "fqn": WIDGET_FQN,
        "name": "SIBA vent demo view (DEMO)",
        "deprecated": False,
        "scada": False,
        "description": "VENT-006 DEMO: dashboard thông gió dữ liệu fixture cô lập. Không datasource, "
                       "không telemetry, không RPC. Nguồn: repo SIBA-IOT-SYS-THONGGIO.",
        "descriptor": {
            "type": "static",
            "sizeX": 24,
            "sizeY": 24,
            "resources": [],
            "templateHtml": '<div class="vent-demo-root"></div>',
            "templateCss": build_css(),
            "controllerScript": build_controller(),
            "settingsSchema": "",
            "dataKeySettingsSchema": "",
            "defaultConfig": json.dumps(default_config, ensure_ascii=False),
        },
    }


def widget_instance(state):
    wid = str(uuid.uuid5(UUID_NS, "widget:" + state))
    return wid, {
        "id": wid,
        "typeFullFqn": WIDGET_FULL_FQN,
        "type": "static",
        "sizeX": 24, "sizeY": 24, "row": 0, "col": 0,
        "config": {
            "configMode": "basic",
            "title": "Thông gió DEMO · " + state,
            "showTitle": False,
            "showTitleIcon": False,
            "dropShadow": False,
            "enableFullscreen": False,
            "enableDataExport": False,
            "backgroundColor": BG,
            "color": "#edf5f9",
            "padding": "0px",
            "margin": "0px",
            "borderRadius": "0px",
            "widgetStyle": {},
            "actions": {},
            "settings": {"viewState": state},
            "datasources": [],
            "widgetCss": ":host ::ng-deep .tb-widget { background: transparent !important; border: none !important; box-shadow: none !important; }",
            "mobileHeight": 12,
        },
    }


def dashboard_payload():
    widgets, states = {}, {}
    for state in STATES:
        wid, widget = widget_instance(state)
        widgets[wid] = widget
        states[state] = {
            "name": STATE_NAMES[state],
            "root": state == "default",
            "layouts": {"main": {
                "widgets": {wid: {"sizeX": 24, "sizeY": 24, "row": 0, "col": 0}},
                "gridSettings": {"layoutType": "default", "backgroundColor": BG, "columns": 24, "margin": 0,
                                 "outerMargin": False, "backgroundSizeMode": "100%", "autoFillHeight": True,
                                 "mobileAutoFillHeight": True, "mobileRowHeight": 70},
            }},
        }
    dashboard_css = (
        ".tb-dashboard-page{background:%s}\n"
        ".tb-dashboard-page .tb-widget-container>.tb-widget{background:%s!important;border:0!important;"
        "border-radius:0!important;box-shadow:none!important;padding:0!important}\n" % (BG, BG)
    )
    return {
        "title": DASHBOARD_TITLE,
        "name": DASHBOARD_TITLE,
        "configuration": {
            "description": "VENT-006 DEMO · thông gió · dữ liệu fixture cô lập. Không PLC, không telemetry, "
                           "không RPC. Không phải bằng chứng runtime.",
            "widgets": widgets,
            "states": states,
            "entityAliases": {},
            "filters": {},
            "timewindow": {"realtime": {"timewindowMs": 3600000}},
            "settings": {
                "stateControllerId": "default",
                "showTitle": False,
                "showDashboardsSelect": False,
                "showEntitiesSelect": False,
                "showDashboardTimewindow": False,
                "showDashboardExport": False,
                "toolbarAlwaysOpen": False,
                "hideToolbar": False,
                "showFilters": False,
                "dashboardCss": dashboard_css,
            },
        },
    }


def validate(widget, dashboard):
    problems = []
    d = widget["descriptor"]
    # Live TB 4.3.1.2 rejects a descriptor exceeding varchar(1000000).
    # Keep margin for serialization/normalization, and block BEFORE any network write.
    if len(json.dumps(d, ensure_ascii=False)) > 900000:
        problems.append("descriptor exceeds safe 900000-character embedding budget")
    if widget["fqn"] != WIDGET_FQN or d["type"] != "static" or "id" in widget:
        problems.append("widget identity/type")
    js = d["controllerScript"]
    for forbidden in ("/api/", "sendOneWayRpc", "sendTwoWayRpc", "controlApi", "attributeService",
                      "saveEntityAttributes", "subscriptionApi", "fetch(", "WebSocket", "TB_PASSWORD"):
        if forbidden in js:
            problems.append("controller contains " + forbidden)
    # location.hash chỉ còn trong nhánh standalone, nhánh này return sớm khi root !== window.
    if "if (root !== window) return;" not in js:
        problems.append("standalone guard missing")
    if "ctx.stateController.openState(next, params || {}, false)" not in js:
        problems.append("navigation must use stateController.openState")
    if ":root,.vent-demo-root{" not in d["templateCss"] or "tb-preview" in d["templateCss"] or "tb-topbar" in d["templateCss"]:
        problems.append("css scope / preview shell")
    c = dashboard["configuration"]
    if dashboard["title"] != DASHBOARD_TITLE or "id" in dashboard or dashboard.get("assignedCustomers"):
        problems.append("dashboard identity")
    if list(c["states"]) != STATES or [s for s, v in c["states"].items() if v["root"]] != ["default"]:
        problems.append("states")
    if c["entityAliases"] or c["filters"]:
        problems.append("aliases/filters must be empty")
    for w in c["widgets"].values():
        if w["typeFullFqn"] != WIDGET_FULL_FQN or w["config"]["datasources"] or w["config"].get("actions"):
            problems.append("widget instance " + w["id"])
    viewstates = sorted(w["config"]["settings"]["viewState"] for w in c["widgets"].values())
    if viewstates != sorted(STATES):
        problems.append("viewState coverage")
    if c["settings"]["stateControllerId"] != "default":
        problems.append("state controller")
    return problems


def main():
    widget, dashboard = widget_type_payload(), dashboard_payload()
    problems = validate(widget, dashboard)
    if problems:
        raise SystemExit("payload không hợp lệ: " + "; ".join(problems))
    targets = {BUILD_DIR / "widget_type.json": widget, BUILD_DIR / "dashboard.json": dashboard}
    if "--check" in sys.argv:
        stale = [p.name for p, data in targets.items()
                 if not p.is_file() or json.loads(p.read_text(encoding="utf-8")) != data]
        if stale:
            raise SystemExit("build lệch nguồn: " + ", ".join(stale))
        print("build khớp nguồn")
        return
    for path, data in targets.items():
        write_json(path, data)
        print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
