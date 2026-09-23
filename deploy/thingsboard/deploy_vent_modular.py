#!/usr/bin/env python3
"""VENT-010: Deploy modular ventilation dashboard and widgets to ThingsBoard live.

Actions:
  python3 deploy_vent_modular.py preflight
  python3 deploy_vent_modular.py execute --confirm-deploy
  python3 deploy_vent_modular.py rollback --confirm-rollback
  python3 deploy_vent_modular.py verify

Only targets the isolated demo namespace (tenant.siba_vent_demo.modular_*) and the
existing isolated demo dashboard DB-30-VEN-DETAIL-V1-DEMO (b9ff4d70-b26a-11f1-83ad-9912edc644d2).
Never mutates protected dashboards, rule chains, telemetry or production devices.
"""
import argparse
import copy
import datetime
import json
import pathlib
import sys

from deploy_vent_demo import snapshot
from vent_demo_common import (DASHBOARD_TITLE, EVIDENCE_DIR, GuardedTB, ROOT,
                             STATES, WIDGET_NAMESPACE_PREFIX, write_json)

DASHBOARD_ID = "b9ff4d70-b26a-11f1-83ad-9912edc644d2"
MODULAR_BUILD_DIR = ROOT / "deploy/thingsboard/build/modular"
KINDS = ("static", "latest", "timeseries", "alarm", "overview")
MANIFEST = ROOT / "deploy/thingsboard/vent010_manifest.json"
BACKUP_PATH = EVIDENCE_DIR / "vent010_pre_deploy_dashboard_backup.json"
EXECUTION_RECORD = EVIDENCE_DIR / "vent010_execution.json"


def now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")


def preflight(tb):
    """Check connectivity, existing dashboard, protected snapshot, and widget types."""
    user = tb.get_ok("/api/auth/user")
    tenant = user.get("tenantId", {}).get("id")
    if user.get("authority") != "TENANT_ADMIN" or not tenant:
        raise RuntimeError("Unexpected tenant authority")

    dashboard = tb.get_ok("/api/dashboard/" + DASHBOARD_ID)
    if dashboard.get("title") != DASHBOARD_TITLE:
        raise RuntimeError("Dashboard title mismatch: %s" % dashboard.get("title"))

    # Check modular widget types
    existing_widgets = {}
    for kind in KINDS:
        fqn = "tenant.siba_vent_demo.modular_" + kind
        code, body = tb.get("/api/widgetType?fqn=" + fqn)
        if code == 200:
            existing_widgets[kind] = {"id": body["id"]["id"], "version": body.get("version")}
        else:
            existing_widgets[kind] = None

    snap = snapshot(tb)
    return {
        "task": "VENT-010",
        "captured_at": now(),
        "tenant_id": tenant,
        "dashboard": {"id": DASHBOARD_ID, "title": dashboard["title"], "version": dashboard.get("version"),
                      "current_states": list(dashboard.get("configuration", {}).get("states", {}).keys())},
        "existing_modular_widgets": existing_widgets,
        "protected": snap,
    }


def execute():
    reader = GuardedTB()
    before = preflight(reader)
    print("Preflight check passed.")

    # Save backup of current live dashboard before mutation
    live_dashboard = reader.get_ok("/api/dashboard/" + DASHBOARD_ID)
    write_json(BACKUP_PATH, {"task": "VENT-010", "saved_at": now(), "dashboard": live_dashboard})
    print("Saved live dashboard backup to:", BACKUP_PATH.name)

    # Determine allowed update IDs for widgets + dashboard
    allow_update_ids = {DASHBOARD_ID}
    for kind, info in before["existing_modular_widgets"].items():
        if info is not None:
            allow_update_ids.add(info["id"])

    writer = GuardedTB(allow_create=True, allow_update_ids=allow_update_ids)
    writer._token = reader.token

    record = {
        "task": "VENT-010",
        "started_at": now(),
        "created_widgets": {},
        "updated_widgets": {},
        "mutations": [],
    }

    # 1. Deploy or update the 5 modular widget types
    for kind in KINDS:
        payload_file = MODULAR_BUILD_DIR / ("widget_%s.json" % kind)
        payload = json.loads(payload_file.read_text(encoding="utf-8"))
        fqn_full = "tenant." + payload["fqn"]
        code, existing = reader.get("/api/widgetType?fqn=" + fqn_full)

        if code == 200 and isinstance(existing, dict):
            # Update existing widget type
            body = copy.deepcopy(existing)
            for k in ("descriptor", "name", "description", "deprecated", "scada"):
                body[k] = copy.deepcopy(payload[k])
            status, res = writer.request("/api/widgetType", "POST", body)
            if status != 200:
                raise RuntimeError("Failed to update widget %s (status %s)" % (fqn_full, status))
            wid = res["id"]["id"]
            record["updated_widgets"][kind] = {"id": wid, "version": res.get("version")}
            print("Updated widget:", payload["fqn"], "-> ID:", wid)
        else:
            # Create new widget type
            status, res = writer.request("/api/widgetType", "POST", payload)
            if status != 200:
                raise RuntimeError("Failed to create widget %s (status %s)" % (fqn_full, status))
            wid = res["id"]["id"]
            record["created_widgets"][kind] = {"id": wid, "version": res.get("version")}
            print("Created widget:", payload["fqn"], "-> ID:", wid)

    # 2. Update the dashboard with the modular payload
    dash_payload_file = MODULAR_BUILD_DIR / "dashboard.json"
    dash_payload = json.loads(dash_payload_file.read_text(encoding="utf-8"))
    dash_body = copy.deepcopy(live_dashboard)
    dash_body["configuration"] = copy.deepcopy(dash_payload["configuration"])

    status, res_dash = writer.request("/api/dashboard", "POST", dash_body)
    if status != 200:
        raise RuntimeError("Failed to update dashboard (status %s)" % status)
    print("Updated dashboard:", DASHBOARD_ID, "-> Version:", res_dash.get("version"))
    record["dashboard_updated"] = {"id": DASHBOARD_ID, "version": res_dash.get("version")}

    # 3. Verify protected baseline unchanged
    after_protected = snapshot(reader)
    # Protected dashboards and bundle must remain identical
    if after_protected["dashboards"] != before["protected"]["dashboards"]:
        raise RuntimeError("Protected dashboards changed!")
    if after_protected["bundle"] != before["protected"]["bundle"]:
        raise RuntimeError("Protected bundle changed!")
    if after_protected["counts"]["assets"] != before["protected"]["counts"]["assets"] or        after_protected["counts"]["devices"] != before["protected"]["counts"]["devices"]:
        raise RuntimeError("Protected entity counts changed!")
    print("Protected tenant snapshot: UNCHANGED (OK)")

    record["finished_at"] = now()
    record["guard_mutations"] = writer.mutations
    write_json(MANIFEST, record)
    write_json(EXECUTION_RECORD, record)
    print("Deployment recorded to manifest:", MANIFEST.name)
    verify()


def verify():
    reader = GuardedTB()
    dash = reader.get_ok("/api/dashboard/" + DASHBOARD_ID)
    states = list(dash.get("configuration", {}).get("states", {}).keys())
    widgets = dash.get("configuration", {}).get("widgets", {})
    print("Live dashboard verification:")
    print("  Title:", dash["title"])
    print("  Version:", dash.get("version"))
    print("  States (%d):" % len(states), states)
    print("  Widgets count (%d):" % len(widgets))
    for wid, w in list(widgets.items())[:3]:
        print("    - %s (%s, viewState: %s)" % (w.get("typeFullFqn"), w["config"].get("title"),
                                               w["config"].get("settings", {}).get("viewState")))
    assert states == list(STATES), "States mismatch"
    assert len(widgets) == 13, "Widget count mismatch (expected 13, got %d)" % len(widgets)

    for kind in KINDS:
        fqn = "tenant.siba_vent_demo.modular_" + kind
        w = reader.get_ok("/api/widgetType?fqn=" + fqn)
        print("  Verified modular widget:", fqn, "-> ID:", w["id"]["id"], "Version:", w.get("version"))
    print("VERIFICATION COMPLETE: PASS")


def rollback():
    if not BACKUP_PATH.is_file():
        raise RuntimeError("Backup file not found: %s" % BACKUP_PATH)
    backup_data = json.loads(BACKUP_PATH.read_text(encoding="utf-8"))
    backup_dash = backup_data["dashboard"]

    reader = GuardedTB()
    writer = GuardedTB(allow_update_ids={DASHBOARD_ID})
    writer._token = reader.token

    status, res = writer.request("/api/dashboard", "POST", backup_dash)
    if status != 200:
        raise RuntimeError("Rollback failed (HTTP %s)" % status)
    print("Rollback successful. Restored dashboard to version:", res.get("version"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preflight", "execute", "rollback", "verify"))
    parser.add_argument("--confirm-deploy", action="store_true")
    parser.add_argument("--confirm-rollback", action="store_true")
    args = parser.parse_args()

    if args.action == "preflight":
        res = preflight(GuardedTB())
        write_json(EVIDENCE_DIR / "vent010_preflight.json", res)
        print("Preflight complete; no mutations. Evidence saved.")
    elif args.action == "execute":
        if not args.confirm_deploy:
            parser.error("requires --confirm-deploy")
        execute()
    elif args.action == "rollback":
        if not args.confirm_rollback:
            parser.error("requires --confirm-rollback")
        rollback()
    else:
        verify()


if __name__ == "__main__":
    main()
