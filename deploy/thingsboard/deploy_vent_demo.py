#!/usr/bin/env python3
"""VENT-006 — deploy dashboard thông gió DEMO cô lập, có rào chắn.

  python3 deploy_vent_demo.py preflight                 # chỉ GET; ghi evidence/vent006_preflight.json
  python3 deploy_vent_demo.py execute --confirm-create  # preflight lại rồi tạo ĐÚNG 2 object
  python3 deploy_vent_demo.py regression                # chỉ GET; so với mốc trước khi ghi

Được phép ghi: POST /api/widgetType (fqn siba_vent_demo.vent_demo_view, không id, không
updateExistingByFqn) và POST /api/dashboard (DB-30-VEN-DETAIL-V1-DEMO, không id). Không gì khác.
"""
import datetime
import json
import subprocess
import sys

import build_vent_demo
from vent_demo_common import (BUILD_DIR, CALIBRATION_FQN, DASHBOARD_TITLE, EVIDENCE_DIR, MANIFEST,
                              PROTECTED_BUNDLE, PROTECTED_DASHBOARDS, ROOT, STATES, WIDGET_FQN, WIDGET_FULL_FQN,
                              WIDGET_NAMESPACE_PREFIX, GuardedTB, config_sha, fqn_list_sha, write_json)

PRE_BASELINE = EVIDENCE_DIR / "vent006_baseline_pre_mutation.json"


def now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")


def snapshot(tb):
    """Mốc chỉ đọc của các object được bảo vệ và số lượng toàn tenant."""
    snap = {"dashboards": {}, "bundle": None, "counts": {}}
    for did, expect in PROTECTED_DASHBOARDS.items():
        d = tb.get_ok("/api/dashboard/" + did)
        sha = config_sha(d["configuration"])
        snap["dashboards"][did] = {"title": d["title"], "version": d.get("version"), "sha256": sha, "sha16": sha[:16]}
    bundles = tb.pages("/api/widgetsBundles?tenantOnly=true")
    bundle = next(b for b in bundles if b.get("alias") == PROTECTED_BUNDLE["alias"])
    fqns = [t["fqn"] for t in tb.get_ok("/api/widgetsBundle/%s/widgetTypes" % bundle["id"]["id"])]
    sha = fqn_list_sha(fqns)
    snap["bundle"] = {"alias": bundle["alias"], "id": bundle["id"]["id"], "version": bundle.get("version"),
                      "count": len(fqns), "sha256": sha, "sha16": sha[:16]}
    snap["tenant_bundle_count"] = len(bundles)
    for key, path in (("assets", "/api/tenant/assets"), ("devices", "/api/tenant/devices"),
                      ("dashboards", "/api/tenant/dashboards"), ("tenant_widget_types", "/api/widgetTypes?tenantOnly=true")):
        sep = "&" if "?" in path else "?"
        snap["counts"][key] = tb.get_ok(path + sep + "pageSize=1&page=0")["totalElements"]
    return snap


def dashboards_referencing_namespace(tb):
    hits = []
    for info in tb.pages("/api/tenant/dashboards"):
        d = tb.get_ok("/api/dashboard/" + info["id"]["id"])
        widgets = (d.get("configuration") or {}).get("widgets") or {}
        if any(str(w.get("typeFullFqn", "")).startswith(WIDGET_NAMESPACE_PREFIX) for w in widgets.values()):
            hits.append({"id": info["id"]["id"], "title": info["title"]})
    return hits


def dashboard_title_present(tb):
    return [d["id"]["id"] for d in tb.pages("/api/tenant/dashboards") if d["title"] == DASHBOARD_TITLE]


def widget_lookup_status(tb, full_fqn):
    status, _ = tb.get("/api/widgetType?fqn=" + full_fqn)
    return status


def preflight(tb):
    report = {"at": now(), "checks": {}, "stop": []}
    user = tb.get_ok("/api/auth/user")
    info = tb.get_ok("/api/system/info")
    report["platform"] = {"version": info.get("version"), "type": info.get("type"), "authority": user.get("authority"),
                          "tenantId": user["tenantId"]["id"]}
    calib = widget_lookup_status(tb, CALIBRATION_FQN)
    target = widget_lookup_status(tb, WIDGET_FULL_FQN)
    report["checks"]["widget_lookup_calibration"] = {"fqn": CALIBRATION_FQN, "status": calib}
    report["checks"]["widget_fqn_absent"] = {"fqn": WIDGET_FULL_FQN, "status": target}
    if calib != 200:
        report["stop"].append("calibration lookup did not return 200")
    if target != 404:
        report["stop"].append("target widget lookup is not 404 (%s)" % target)
    tenant_types = [w["fqn"] for w in tb.pages("/api/widgetTypes?tenantOnly=true")]
    if any(f.startswith("siba_vent_demo.") for f in tenant_types):
        report["stop"].append("siba_vent_demo.* widget type already exists")
    present = dashboard_title_present(tb)
    report["checks"]["dashboard_title_absent"] = {"title": DASHBOARD_TITLE, "matches": present}
    if present:
        report["stop"].append("dashboard title already exists")
    refs = dashboards_referencing_namespace(tb)
    report["checks"]["namespace_unreferenced"] = refs
    if refs:
        report["stop"].append("a dashboard already references tenant.siba_vent_demo.*")
    snap = snapshot(tb)
    report["baseline"] = snap
    for did, expect in PROTECTED_DASHBOARDS.items():
        got = snap["dashboards"][did]
        if (got["title"], got["version"], got["sha16"]) != (expect["title"], expect["version"], expect["sha16"]):
            report["stop"].append("protected dashboard changed since plan: %s" % expect["title"])
    b = snap["bundle"]
    if (b["count"], b["sha16"]) != (PROTECTED_BUNDLE["count"], PROTECTED_BUNDLE["sha16"]):
        report["stop"].append("siba_custom_ui bundle changed since plan")
    report["ok"] = not report["stop"]
    return report


def git_state():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "deploy", "widgets", "dashboard", "fixtures"],
                           cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    return head, dirty


def load_payloads():
    widget = json.loads((BUILD_DIR / "widget_type.json").read_text(encoding="utf-8"))
    dashboard = json.loads((BUILD_DIR / "dashboard.json").read_text(encoding="utf-8"))
    if widget != build_vent_demo.widget_type_payload() or dashboard != build_vent_demo.dashboard_payload():
        raise SystemExit("STOP: file build lệch nguồn; chạy build và commit trước")
    problems = build_vent_demo.validate(widget, dashboard)
    if problems:
        raise SystemExit("STOP: payload không hợp lệ: " + "; ".join(problems))
    return widget, dashboard


def rollback_widget(tb_reader, widget_id, reason):
    deleter = GuardedTB(allow_delete_ids={widget_id})
    deleter._token = tb_reader._token
    got = tb_reader.get_ok("/api/widgetType/" + widget_id)
    if got.get("fqn") != WIDGET_FQN:
        return "not deleted: fqn mismatch"
    status, _ = deleter.request("/api/widgetType/" + widget_id, "DELETE")
    return "deleted (%s) because %s" % (status, reason)


def execute():
    if "--confirm-create" not in sys.argv:
        raise SystemExit("Cần --confirm-create")
    if MANIFEST.exists():
        raise SystemExit("STOP: manifest đã tồn tại; không tạo lần hai")
    head, dirty = git_state()
    if dirty:
        raise SystemExit("STOP: nguồn deploy có thay đổi chưa commit:\n" + dirty)
    widget_payload, dashboard_payload = load_payloads()

    reader = GuardedTB()
    pre = preflight(reader)
    write_json(PRE_BASELINE, pre)
    if not pre["ok"]:
        raise SystemExit("STOP preflight: " + "; ".join(pre["stop"]))

    creator = GuardedTB(allow_create=True)
    creator._token = reader.token
    manifest = {"task": "VENT-006", "repository_commit": head, "tb_url_host": "100.86.144.207:8080",
                "tenantId": pre["platform"]["tenantId"], "started_at": now(), "created": {}, "mutations": []}

    # STEP 1 — widget type
    if widget_lookup_status(reader, WIDGET_FULL_FQN) != 404:
        raise SystemExit("STOP: widget fqn không còn 404 ngay trước POST")
    status, body = creator.request("/api/widgetType", "POST", widget_payload)
    manifest["mutations"].append({"method": "POST", "path": "/api/widgetType", "status": status, "at": now()})
    if status != 200 or not isinstance(body, dict):
        write_json(MANIFEST, manifest)
        raise SystemExit("STOP: POST widgetType -> %s: %s" % (status, str(body)[:200]))
    widget_id = body["id"]["id"]
    manifest["created"]["widget_type"] = {"id": widget_id, "fqn": WIDGET_FQN, "full_fqn": WIDGET_FULL_FQN,
                                          "created_at": now()}
    write_json(MANIFEST, manifest)
    by_id = reader.get_ok("/api/widgetType/" + widget_id)
    by_fqn_status, by_fqn = reader.get("/api/widgetType?fqn=" + WIDGET_FULL_FQN)
    problems = []
    if by_id.get("fqn") != WIDGET_FQN or by_id["descriptor"].get("type") != "static":
        problems.append("by-id identity/type")
    if by_id["descriptor"].get("controllerScript") != widget_payload["descriptor"]["controllerScript"]:
        problems.append("controllerScript round-trip")
    if by_id["descriptor"].get("templateCss") != widget_payload["descriptor"]["templateCss"]:
        problems.append("templateCss round-trip")
    if (by_id.get("tenantId") or {}).get("id") != pre["platform"]["tenantId"]:
        problems.append("tenant scope")
    if by_fqn_status != 200 or by_fqn.get("id", {}).get("id") != widget_id:
        problems.append("by-fqn lookup")
    manifest["created"]["widget_type"]["verification"] = problems or "ok"
    if problems:
        manifest["created"]["widget_type"]["rollback"] = rollback_widget(reader, widget_id, ", ".join(problems))
        write_json(MANIFEST, manifest)
        raise SystemExit("STOP: xác minh widget type lỗi: " + ", ".join(problems))
    write_json(MANIFEST, manifest)
    print("widget type created:", widget_id)

    # STEP 2 — dashboard
    if dashboard_title_present(reader):
        write_json(MANIFEST, manifest)
        raise SystemExit("STOP: tiêu đề dashboard đã xuất hiện ngay trước POST; widget type giữ nguyên, xem rollback")
    status, body = creator.request("/api/dashboard", "POST", dashboard_payload)
    manifest["mutations"].append({"method": "POST", "path": "/api/dashboard", "status": status, "at": now()})
    if status != 200 or not isinstance(body, dict):
        write_json(MANIFEST, manifest)
        raise SystemExit("STOP: POST dashboard -> %s: %s" % (status, str(body)[:200]))
    dash_id = body["id"]["id"]
    manifest["created"]["dashboard"] = {"id": dash_id, "title": DASHBOARD_TITLE, "created_at": now()}
    write_json(MANIFEST, manifest)
    d = reader.get_ok("/api/dashboard/" + dash_id)
    c = d["configuration"]
    problems = []
    if d["title"] != DASHBOARD_TITLE:
        problems.append("title")
    if list(c.get("states", {})) != STATES or [s for s, v in c["states"].items() if v.get("root")] != ["default"]:
        problems.append("states")
    fqns = {w.get("typeFullFqn") for w in c.get("widgets", {}).values()}
    if fqns != {WIDGET_FULL_FQN}:
        problems.append("widget fqn set %s" % sorted(fqns))
    if c.get("entityAliases"):
        problems.append("aliases present")
    if any(w["config"].get("datasources") for w in c["widgets"].values()):
        problems.append("datasource present")
    if d.get("assignedCustomers"):
        problems.append("customer assigned")
    # Thông tin: TB có thể chuẩn hóa thêm field; không coi là lỗi an toàn.
    manifest["created"]["dashboard"]["configuration_roundtrip_identical"] = config_sha(c) == config_sha(dashboard_payload["configuration"])
    manifest["created"]["dashboard"]["verification"] = problems or "ok"
    manifest["created"]["dashboard"]["version"] = d.get("version")
    manifest["finished_at"] = now()
    manifest["guard_mutation_log"] = creator.mutations
    write_json(MANIFEST, manifest)
    if problems:
        raise SystemExit("STOP: xác minh dashboard lỗi: %s (không tự rollback; xem rollback_vent_demo.py)" % problems)
    print("dashboard created:", dash_id)
    print("url: http://100.86.144.207:8080/dashboards/" + dash_id)


def regression():
    tb = GuardedTB()
    pre = json.loads(PRE_BASELINE.read_text(encoding="utf-8"))["baseline"]
    post = snapshot(tb)
    result = {"at": now(), "dashboards": {}, "bundle": None, "counts": {}}
    for did, before in pre["dashboards"].items():
        after = post["dashboards"][did]
        result["dashboards"][did] = {"title": before["title"], "version": [before["version"], after["version"]],
                                     "sha16": [before["sha16"], after["sha16"]],
                                     "unchanged": (before["version"], before["sha256"]) == (after["version"], after["sha256"])}
    result["bundle"] = {"count": [pre["bundle"]["count"], post["bundle"]["count"]],
                        "sha16": [pre["bundle"]["sha16"], post["bundle"]["sha16"]],
                        "unchanged": (pre["bundle"]["count"], pre["bundle"]["sha256"]) == (post["bundle"]["count"], post["bundle"]["sha256"])}
    expected_delta = {"assets": 0, "devices": 0, "dashboards": 1, "tenant_widget_types": 1}
    for key, delta in expected_delta.items():
        result["counts"][key] = {"before": pre["counts"][key], "after": post["counts"][key], "expected_delta": delta,
                                 "ok": post["counts"][key] - pre["counts"][key] == delta}
    result["tenant_bundle_count"] = [pre["tenant_bundle_count"], post["tenant_bundle_count"]]
    result["ok"] = (all(x["unchanged"] for x in result["dashboards"].values()) and result["bundle"]["unchanged"]
                    and all(x["ok"] for x in result["counts"].values())
                    and pre["tenant_bundle_count"] == post["tenant_bundle_count"])
    write_json(EVIDENCE_DIR / "vent006_regression.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=1))
    if not result["ok"]:
        raise SystemExit("REGRESSION: có thay đổi ngoài dự kiến — DỪNG và điều tra")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "preflight":
        report = preflight(GuardedTB())
        write_json(EVIDENCE_DIR / "vent006_preflight.json", report)
        print(json.dumps({k: report[k] for k in ("ok", "stop", "checks")}, ensure_ascii=False, indent=1))
        print("baseline:", json.dumps({k: v for k, v in report["baseline"].items()}, ensure_ascii=False)[:900])
    elif cmd == "execute":
        execute()
    elif cmd == "regression":
        regression()
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
