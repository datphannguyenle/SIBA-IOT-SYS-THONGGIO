#!/usr/bin/env python3
"""VENT-006 — gỡ ĐÚNG hai object do lần deploy này tạo (theo vent006_manifest.json).

  python3 rollback_vent_demo.py              # chạy thử: chỉ GET, in kế hoạch xóa
  python3 rollback_vent_demo.py --confirm-delete

Thứ tự: dashboard -> xác nhận không dashboard nào còn tham chiếu tenant.siba_vent_demo.* -> widget type.
Chỉ xóa khi ID + tiêu đề/fqn khớp chính xác manifest. Không bao giờ xóa object có sẵn từ trước.
"""
import datetime
import json
import sys

from deploy_vent_demo import dashboards_referencing_namespace
from vent_demo_common import (DASHBOARD_TITLE, EVIDENCE_DIR, MANIFEST, WIDGET_FQN, GuardedTB, write_json)


def main():
    confirm = "--confirm-delete" in sys.argv
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    created = manifest.get("created", {})
    dash = created.get("dashboard")
    widget = created.get("widget_type")
    ids = {x["id"] for x in (dash, widget) if x}
    reader = GuardedTB()
    deleter = GuardedTB(allow_delete_ids=ids if confirm else ())
    deleter._token = reader.token
    log = {"at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "confirm": confirm, "steps": []}

    if dash:
        status, body = reader.get("/api/dashboard/" + dash["id"])
        if status == 404:
            log["steps"].append({"dashboard": dash["id"], "result": "already absent"})
        elif status != 200 or body.get("title") != DASHBOARD_TITLE or dash.get("title") != DASHBOARD_TITLE:
            raise SystemExit("STOP: dashboard %s không khớp manifest; không xóa" % dash["id"])
        elif confirm:
            st, _ = deleter.request("/api/dashboard/" + dash["id"], "DELETE")
            log["steps"].append({"dashboard": dash["id"], "delete_status": st})
            if st != 200:
                raise SystemExit("STOP: DELETE dashboard -> %s" % st)
        else:
            log["steps"].append({"dashboard": dash["id"], "would_delete": True})

    if widget:
        refs = dashboards_referencing_namespace(reader)
        if confirm and refs:
            raise SystemExit("STOP: còn dashboard tham chiếu widget: %s" % refs)
        status, body = reader.get("/api/widgetType/" + widget["id"])
        if status == 404:
            log["steps"].append({"widget_type": widget["id"], "result": "already absent"})
        elif status != 200 or body.get("fqn") != WIDGET_FQN or widget.get("fqn") != WIDGET_FQN:
            raise SystemExit("STOP: widget type %s không khớp manifest; không xóa" % widget["id"])
        elif confirm:
            st, _ = deleter.request("/api/widgetType/" + widget["id"], "DELETE")
            log["steps"].append({"widget_type": widget["id"], "delete_status": st})
            if st != 200:
                raise SystemExit("STOP: DELETE widgetType -> %s" % st)
        else:
            log["steps"].append({"widget_type": widget["id"], "would_delete": True, "references": refs})

    log["guard_mutation_log"] = deleter.mutations
    if confirm:
        write_json(EVIDENCE_DIR / "vent006_rollback_log.json", log)
    print(json.dumps(log, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
