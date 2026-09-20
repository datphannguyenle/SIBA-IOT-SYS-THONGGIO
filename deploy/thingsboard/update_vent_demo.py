#!/usr/bin/env python3
"""VENT-008: update only the two existing isolated demo objects, never create.

preflight: GET-only (+ authentication), records exact rollback payloads.
execute --confirm-update: requires clean committed sources; rechecks live fingerprints.
verify: GET-only comparison with the built payload and protected tenant baseline.
rollback --confirm-rollback: restore the backup in reverse order, only if the live
object still matches the last verified version written by this run. Never retry a
timed-out write automatically. An indeterminate result needs read-only investigation.
"""
import argparse
import copy
import json
import sys

from deploy_vent_demo import (dashboards_referencing_namespace, descriptor_key,
                             git_state, load_payloads, now, snapshot)
from vent_demo_common import (DASHBOARD_TITLE, EVIDENCE_DIR, GuardedTB, STATES,
                             WIDGET_FQN, WIDGET_FULL_FQN, config_sha, write_json)

WIDGET_ID = "b9fa9280-b26a-11f1-83ad-9912edc644d2"
DASHBOARD_ID = "b9ff4d70-b26a-11f1-83ad-9912edc644d2"
BACKUP = EVIDENCE_DIR / "vent008_before_update.json"
RECORD = EVIDENCE_DIR / "vent008_execution.json"
RESULT = EVIDENCE_DIR / "vent008_regression.json"
TARGETS = (("widget", "/api/widgetType", WIDGET_ID),
           ("dashboard", "/api/dashboard", DASHBOARD_ID))


def identity(tb):
    widget = tb.get_ok("/api/widgetType/" + WIDGET_ID)
    dashboard = tb.get_ok("/api/dashboard/" + DASHBOARD_ID)
    by_fqn = tb.get_ok("/api/widgetType?fqn=" + WIDGET_FULL_FQN)
    user = tb.get_ok("/api/auth/user")
    tenant = user.get("tenantId", {}).get("id")
    if user.get("authority") != "TENANT_ADMIN" or not tenant:
        raise RuntimeError("Unexpected tenant authority")
    if (widget.get("id", {}).get("id") != WIDGET_ID or widget.get("fqn") != WIDGET_FQN
            or by_fqn.get("id", {}).get("id") != WIDGET_ID):
        raise RuntimeError("Widget identity mismatch")
    if (dashboard.get("id", {}).get("id") != DASHBOARD_ID
            or dashboard.get("title") != DASHBOARD_TITLE or dashboard.get("assignedCustomers")):
        raise RuntimeError("Dashboard identity/assignment mismatch")
    for obj in (widget, dashboard):
        if obj.get("tenantId", {}).get("id") != tenant:
            raise RuntimeError("Tenant mismatch")
    refs = dashboards_referencing_namespace(tb)
    if refs != [{"id": DASHBOARD_ID, "title": DASHBOARD_TITLE}]:
        raise RuntimeError("Demo namespace is shared with an unexpected dashboard")
    c = dashboard["configuration"]
    if c.get("entityAliases") or c.get("filters"):
        raise RuntimeError("Unexpected live data bindings")
    if not c.get("widgets") or any(
            w.get("typeFullFqn") != WIDGET_FULL_FQN or w.get("config", {}).get("datasources")
            or w.get("config", {}).get("actions") for w in c["widgets"].values()):
        raise RuntimeError("Dashboard is no longer fixture-isolated")
    return {"widget": widget, "dashboard": dashboard}


def fingerprint(obj):
    """Include version and all fields: concurrent edits/assignments must stop this run."""
    return config_sha(obj)


def content_matches(kind, live, intended):
    if kind == "widget":
        return (descriptor_key(live["descriptor"]) == descriptor_key(intended["descriptor"])
                and all(live.get(k) == intended.get(k)
                        for k in ("name", "description", "deprecated", "scada")))
    return live["configuration"] == intended["configuration"]


def update_body(kind, live, intended):
    """Preserve exact live ownership, identity, version and unrelated metadata."""
    body = copy.deepcopy(live)
    keys = ("descriptor", "name", "description", "deprecated", "scada") if kind == "widget" else ("configuration",)
    for key in keys:
        body[key] = copy.deepcopy(intended[key])
    return body


def preflight(tb):
    objects = identity(tb)
    return {"task": "VENT-008", "captured_at": now(), "objects": objects,
            "fingerprints": {k: fingerprint(v) for k, v in objects.items()},
            "protected": snapshot(tb), "mutations": list(tb.mutations)}


def checked_write(writer, path, payload, entry, record):
    # Persist intent BEFORE sending; a disconnect is not evidence that a write failed.
    entry.update({"status": "sending", "at": now()})
    record["mutations"].append(entry)
    write_json(RECORD, record)
    try:
        status, body = writer.request(path, "POST", payload)
    except Exception:
        entry["status"] = "indeterminate; GET inspection required; do not retry"
        write_json(RECORD, record)
        raise RuntimeError("Write result indeterminate; inspect live object without retry") from None
    entry["http_status"] = status
    entry["status"] = "response received"
    write_json(RECORD, record)
    if status != 200 or not isinstance(body, dict):
        raise RuntimeError("Write returned HTTP %s; no retry" % status)


def execute():
    if RECORD.exists():
        raise RuntimeError("Execution record exists; inspect/verify it, do not repeat the update")
    if BACKUP.exists():
        raise RuntimeError("Backup exists; inspect it before starting a new update")
    head, dirty = git_state()
    if dirty:
        raise RuntimeError("Deployment sources are not committed")
    payloads = dict(zip(("widget", "dashboard"), load_payloads()))
    reader = GuardedTB()
    before = preflight(reader)
    write_json(BACKUP, before)
    writer = GuardedTB(allow_update_ids={WIDGET_ID, DASHBOARD_ID})
    writer._token = reader.token
    record = {"task": "VENT-008", "repository_commit": head, "started_at": now(),
              "authorization": "User authorization to finish current checkpoint; isolated demo only",
              "mutations": [], "written_fingerprints": {}, "results": {}}
    for kind, path, target in TARGETS:
        live = reader.get_ok(path + "/" + target)
        if fingerprint(live) != before["fingerprints"][kind]:
            raise RuntimeError("Concurrent %s edit; stopped before write" % kind)
        if content_matches(kind, live, payloads[kind]):
            record["results"][kind] = "NO-OP; already equivalent"
            continue
        if snapshot(reader) != before["protected"]:
            raise RuntimeError("Protected tenant snapshot changed; stopped before write")
        entry = {"kind": kind, "method": "POST", "path": path, "id": target}
        checked_write(writer, path, update_body(kind, live, payloads[kind]), entry, record)
        current = reader.get_ok(path + "/" + target)
        if not content_matches(kind, current, payloads[kind]):
            raise RuntimeError("%s round-trip mismatch; inspect before any further mutation" % kind)
        record["written_fingerprints"][kind] = fingerprint(current)
        record["results"][kind] = {"verified": True, "version": current.get("version")}
        entry["status"] = "verified"
        write_json(RECORD, record)
    record["finished_at"] = now()
    record["guard_mutations"] = writer.mutations
    write_json(RECORD, record)
    verify()


def verify():
    before = json.loads(BACKUP.read_text(encoding="utf-8"))
    payloads = dict(zip(("widget", "dashboard"), load_payloads()))
    reader = GuardedTB()
    current = identity(reader)
    after = snapshot(reader)
    result = {"at": now(), "payload_match": {k: content_matches(k, v, payloads[k]) for k, v in current.items()},
              "versions": {k: v.get("version") for k, v in current.items()},
              "states": list(current["dashboard"]["configuration"]["states"]),
              "protected_unchanged": before["protected"] == after, "protected_after": after,
              "mutations_during_verification": reader.mutations}
    result["ok"] = (all(result["payload_match"].values()) and result["protected_unchanged"]
                    and result["states"] == STATES and not reader.mutations)
    write_json(RESULT, result)
    print(json.dumps({k: v for k, v in result.items() if k != "protected_after"}, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise RuntimeError("Remote verification failed; stopped")


def rollback():
    before = json.loads(BACKUP.read_text(encoding="utf-8"))
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    reader = GuardedTB()
    identity(reader)
    writer = GuardedTB(allow_update_ids={WIDGET_ID, DASHBOARD_ID})
    writer._token = reader.token
    for kind, path, target in reversed(TARGETS):
        expected = record["written_fingerprints"].get(kind)
        if expected is None:
            if any(x["kind"] == kind and x["status"] != "verified" for x in record["mutations"]):
                raise RuntimeError("Indeterminate %s write; investigate before rollback" % kind)
            continue
        live = reader.get_ok(path + "/" + target)
        if fingerprint(live) != expected:
            raise RuntimeError("%s changed since this run; rollback refused" % kind)
        backup = before["objects"][kind]
        entry = {"kind": kind, "method": "POST", "path": path, "id": target, "action": "rollback"}
        checked_write(writer, path, update_body(kind, live, backup), entry, record)
        restored = reader.get_ok(path + "/" + target)
        if not content_matches(kind, restored, backup):
            raise RuntimeError("Rollback round-trip mismatch")
        entry["status"] = "verified"
        del record["written_fingerprints"][kind]
        write_json(RECORD, record)
    record["rollback_finished_at"] = now()
    record["rollback_protected_unchanged"] = snapshot(reader) == before["protected"]
    write_json(RECORD, record)
    print("Rollback restored previous demo content; inspect UI in a fresh browser.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preflight", "execute", "verify", "rollback"))
    parser.add_argument("--confirm-update", action="store_true")
    parser.add_argument("--confirm-rollback", action="store_true")
    args = parser.parse_args()
    if args.action == "preflight":
        result = preflight(GuardedTB())
        path = EVIDENCE_DIR / "vent008_readonly_preflight.json"
        write_json(path, result)
        print("Read-only preflight passed; no mutations. Evidence:", path.name)
    elif args.action == "execute":
        if not args.confirm_update:
            parser.error("requires --confirm-update and explicit user authorization")
        execute()
    elif args.action == "rollback":
        if not args.confirm_rollback:
            parser.error("requires --confirm-rollback")
        rollback()
    else:
        verify()


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        # Errors contain only locally defined summaries; never dump response bodies.
        print("STOP:", type(exc).__name__, str(exc) if isinstance(exc, RuntimeError) else "inspect sanitized evidence", file=sys.stderr)
        raise SystemExit(1)
