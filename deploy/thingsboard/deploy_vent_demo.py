#!/usr/bin/env python3
"""VENT-006 — deploy dashboard thông gió DEMO cô lập, có rào chắn.

  python3 deploy_vent_demo.py preflight                 # chỉ GET; ghi evidence/vent006_preflight.json
  python3 deploy_vent_demo.py execute --confirm-create  # preflight lại rồi tạo ĐÚNG 2 object
  python3 deploy_vent_demo.py regression                # chỉ GET; so với mốc trước khi ghi
  python3 deploy_vent_demo.py refine --confirm-update   # refinement: CẬP NHẬT đúng ID trong manifest
  python3 deploy_vent_demo.py refine-regression         # chỉ GET; so với mốc trước refinement

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


REFINE_BASELINE = EVIDENCE_DIR / "vent006_refinement_baseline.json"
DEPLOY_REGRESSION = EVIDENCE_DIR / "vent006_regression.json"
WIDGET_TOP_LEVEL = ("name", "description", "deprecated", "scada")


def descriptor_key(descriptor):
    """So descriptor theo ngữ nghĩa: TB lưu defaultConfig dạng JSON nén, nội dung vẫn như payload."""
    d = dict(descriptor)
    if isinstance(d.get("defaultConfig"), str):
        d["defaultConfig"] = json.loads(d["defaultConfig"])
    return d


def refine_preflight(tb, manifest):
    report = {"at": now(), "stop": [], "checks": {}}
    wid = manifest["created"]["widget_type"]["id"]
    did = manifest["created"]["dashboard"]["id"]
    widget = tb.get_ok("/api/widgetType/" + wid)
    status, by_fqn = tb.get("/api/widgetType?fqn=" + WIDGET_FULL_FQN)
    dashboard = tb.get_ok("/api/dashboard/" + did)
    report["checks"]["widget"] = {"id": widget["id"]["id"], "fqn": widget.get("fqn"), "version": widget.get("version"),
                                  "fqn_lookup_status": status, "fqn_lookup_id": (by_fqn or {}).get("id", {}).get("id") if status == 200 else None}
    report["checks"]["dashboard"] = {"id": dashboard["id"]["id"], "title": dashboard.get("title"), "version": dashboard.get("version"),
                                     "sha16": config_sha(dashboard["configuration"])[:16],
                                     "assignedCustomers": dashboard.get("assignedCustomers")}
    if widget["id"]["id"] != wid or widget.get("fqn") != WIDGET_FQN or report["checks"]["widget"]["fqn_lookup_id"] != wid:
        report["stop"].append("widget identity mismatch")
    if dashboard["id"]["id"] != did or dashboard.get("title") != DASHBOARD_TITLE or dashboard.get("assignedCustomers"):
        report["stop"].append("dashboard identity mismatch")
    snap = snapshot(tb)
    report["baseline"] = snap
    for pid, expect in PROTECTED_DASHBOARDS.items():
        got = snap["dashboards"][pid]
        if (got["title"], got["version"], got["sha16"]) != (expect["title"], expect["version"], expect["sha16"]):
            report["stop"].append("protected dashboard changed: %s" % expect["title"])
    if (snap["bundle"]["count"], snap["bundle"]["sha16"]) != (PROTECTED_BUNDLE["count"], PROTECTED_BUNDLE["sha16"]):
        report["stop"].append("siba_custom_ui bundle changed")
    after_deploy = json.loads(DEPLOY_REGRESSION.read_text(encoding="utf-8"))["counts"]
    for key in ("assets", "devices", "dashboards", "tenant_widget_types"):
        if snap["counts"][key] != after_deploy[key]["after"]:
            report["stop"].append("%s count changed since deployment (%s -> %s)" % (key, after_deploy[key]["after"], snap["counts"][key]))
    report["ok"] = not report["stop"]
    return report, widget, dashboard


def refine():
    if "--confirm-update" not in sys.argv:
        raise SystemExit("Cần --confirm-update")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    head, dirty = git_state()
    if dirty:
        raise SystemExit("STOP: nguồn deploy có thay đổi chưa commit:\n" + dirty)
    widget_payload, dashboard_payload = load_payloads()
    reader = GuardedTB()
    pre, live_widget, live_dashboard = refine_preflight(reader, manifest)
    write_json(REFINE_BASELINE, pre)
    if not pre["ok"]:
        raise SystemExit("STOP refine preflight: " + "; ".join(pre["stop"]))

    wid, did = live_widget["id"]["id"], live_dashboard["id"]["id"]
    record = {"task": "VENT-006 visual refinement", "approval": "APPROVED — VENT-006 CONTROLLED VISUAL REFINEMENT UPDATE",
              "repository_commit": head, "started_at": now(), "mutations": [], "results": {}}
    widget_needed = descriptor_key(live_widget["descriptor"]) != descriptor_key(widget_payload["descriptor"]) or any(
        live_widget.get(k) != widget_payload[k] for k in WIDGET_TOP_LEVEL)
    dashboard_needed = config_sha(live_dashboard["configuration"]) != config_sha(dashboard_payload["configuration"])
    record["results"]["widget_type"] = {"update_needed": widget_needed, "version_before": live_widget.get("version")}
    record["results"]["dashboard"] = {"update_needed": dashboard_needed, "version_before": live_dashboard.get("version")}
    updater = GuardedTB(allow_update_ids={x for x, needed in ((wid, widget_needed), (did, dashboard_needed)) if needed})
    updater._token = reader.token

    if widget_needed:
        body = json.loads(json.dumps(live_widget))
        for k in WIDGET_TOP_LEVEL:
            body[k] = widget_payload[k]
        body["descriptor"] = dict(widget_payload["descriptor"])
        if descriptor_key({"defaultConfig": live_widget["descriptor"]["defaultConfig"]}) == descriptor_key(
                {"defaultConfig": widget_payload["descriptor"]["defaultConfig"]}):
            body["descriptor"]["defaultConfig"] = live_widget["descriptor"]["defaultConfig"]   # giữ nguyên chuỗi đang có
        record["results"]["widget_type"]["descriptor_fields_changed"] = sorted(
            k for k in body["descriptor"] if live_widget["descriptor"].get(k) != body["descriptor"][k])
        status, res = updater.request("/api/widgetType", "POST", body)
        record["mutations"].append({"method": "POST", "path": "/api/widgetType", "id": wid, "status": status, "at": now()})
        if status != 200:
            manifest.setdefault("refinements", []).append(record); write_json(MANIFEST, manifest)
            raise SystemExit("STOP: update widgetType -> %s: %s" % (status, str(res)[:200]))
        after = reader.get_ok("/api/widgetType/" + wid)
        _, by_fqn = reader.get("/api/widgetType?fqn=" + WIDGET_FULL_FQN)
        problems = []
        if after["id"]["id"] != wid or after.get("fqn") != WIDGET_FQN or (by_fqn or {}).get("id", {}).get("id") != wid:
            problems.append("identity")
        if after.get("version") != (live_widget.get("version") or 0) + 1:
            problems.append("version %s -> %s" % (live_widget.get("version"), after.get("version")))
        if descriptor_key(after["descriptor"]) != descriptor_key(widget_payload["descriptor"]):
            problems.append("descriptor round-trip")
        for k in ("tenantId", "createdTime") + WIDGET_TOP_LEVEL:
            if after.get(k) != body.get(k):
                problems.append("field " + k)
        record["results"]["widget_type"].update(version_after=after.get("version"), verification=problems or "ok")
        if problems:
            manifest.setdefault("refinements", []).append(record); write_json(MANIFEST, manifest)
            raise SystemExit("STOP: xác minh widget sau update lỗi: %s" % problems)
    if dashboard_needed:
        record["results"]["dashboard"]["note"] = "not performed: dashboard update requires a separately reviewed code path"
        manifest.setdefault("refinements", []).append(record); write_json(MANIFEST, manifest)
        raise SystemExit("STOP: dashboard khác build; không nằm trong refinement dự kiến")

    dash_after = reader.get_ok("/api/dashboard/" + did)
    record["results"]["dashboard"].update(version_after=dash_after.get("version"),
                                          unchanged=config_sha(dash_after["configuration"]) == config_sha(live_dashboard["configuration"])
                                          and dash_after.get("version") == live_dashboard.get("version"))
    record["finished_at"] = now()
    record["guard_mutation_log"] = updater.mutations
    manifest.setdefault("refinements", []).append(record)
    write_json(MANIFEST, manifest)
    print(json.dumps(record, ensure_ascii=False, indent=1))


def refine_regression():
    tb = GuardedTB()
    pre = json.loads(REFINE_BASELINE.read_text(encoding="utf-8"))["baseline"]
    post = snapshot(tb)
    result = {"at": now(), "dashboards": {}, "counts": {}}
    for pid, before in pre["dashboards"].items():
        after = post["dashboards"][pid]
        result["dashboards"][pid] = {"title": before["title"], "version": [before["version"], after["version"]],
                                     "unchanged": (before["version"], before["sha256"]) == (after["version"], after["sha256"])}
    result["bundle"] = {"count": [pre["bundle"]["count"], post["bundle"]["count"]],
                        "unchanged": (pre["bundle"]["count"], pre["bundle"]["sha256"]) == (post["bundle"]["count"], post["bundle"]["sha256"])}
    for key in ("assets", "devices", "dashboards", "tenant_widget_types"):
        result["counts"][key] = {"before": pre["counts"][key], "after": post["counts"][key],
                                 "ok": pre["counts"][key] == post["counts"][key]}
    result["tenant_bundle_count"] = [pre["tenant_bundle_count"], post["tenant_bundle_count"]]
    result["ok"] = (all(x["unchanged"] for x in result["dashboards"].values()) and result["bundle"]["unchanged"]
                    and all(x["ok"] for x in result["counts"].values())
                    and pre["tenant_bundle_count"] == post["tenant_bundle_count"]
                    and post["counts"]["dashboards"] == 10 and post["counts"]["tenant_widget_types"] == 20)
    write_json(EVIDENCE_DIR / "vent006_refinement_regression.json", result)
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
    elif cmd == "refine":
        refine()
    elif cmd == "refine-regression":
        refine_regression()
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
