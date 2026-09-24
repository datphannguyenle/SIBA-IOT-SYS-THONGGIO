#!/usr/bin/env python3
"""VENT-012 preflight chỉ đọc.

Chỉ cho phép GET ThingsBoard và POST /api/auth/login. Báo cáo không chứa mật
khẩu, JWT, access token, địa chỉ PLC, hay nội dung cấu hình Gateway.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from vent_demo_common import GuardedTB, TB_URL  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/ventilation/deployment/vent012_preflight.json"
NAMES = ["SIM-VEN-ND2-%d" % i for i in range(1, 5)] + [
    "tb-gateway-ventilation", "SIM-VEN-GATEWAY-012"]
BARNS = ["abc-dong-anh/ND2-%d" % i for i in range(1, 5)]


def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def docker(*args):
    try:
        return subprocess.check_output(["docker", *args], text=True,
                                       stderr=subprocess.DEVNULL, timeout=20).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return {"_error": type(exc).__name__}


def entity_id(value):
    return value.get("id") if isinstance(value, dict) else value


def page(tb, path):
    return tb.pages(path)


def get(tb, path):
    status, body = tb.get(path)
    if status != 200:
        return {"_http": status}
    return body


def gateway():
    image_id = docker("inspect", "--format", "{{.Image}}", "tb-gateway")
    image_ref = docker("inspect", "--format", "{{.Config.Image}}", "tb-gateway")
    version = docker("exec", "tb-gateway", "python3", "-c",
                     "import thingsboard_gateway.version as v; print(v.VERSION)")
    # The active connector is named only by tb_gateway.json. Hash the active
    # file inside the container; never copy its potentially sensitive content.
    code = r'''
import hashlib,json,pathlib
c=json.load(open('/thingsboard_gateway/config/tb_gateway.json')).get('connectors',[])
m=[x for x in c if x.get('type') == 'modbus']
out=[]
for x in m:
 p=pathlib.Path('/thingsboard_gateway/config') / x['configuration']
 q=json.load(open(p)); slaves=q.get('master',{}).get('slaves',[])
 out.append({'name':x.get('name'),'configuration':x.get('configuration'),
  'sha256':hashlib.sha256(p.read_bytes()).hexdigest(), 'topLevelKeys':sorted(q),
  'slaveCount':len(slaves),'rpcCounts':[len(s.get('rpc',[]) or []) for s in slaves],
  'attributeUpdateCounts':[len(s.get('attributeUpdates',[]) or []) for s in slaves]})
print(json.dumps(out,sort_keys=True))
'''
    active = docker("exec", "tb-gateway", "python3", "-c", code)
    try:
        active = json.loads(active)
    except (TypeError, json.JSONDecodeError):
        active = {"_error": "cannot_read_active_connector_schema"}
    source = docker("exec", "tb-gateway", "python3", "-c", r'''
import json
p='/thingsboard_gateway/connectors/modbus/modbus_connector.py'; s=open(p).read()
print(json.dumps({'path':p,'serverSideHandler': 'server_side_rpc_handler' in s,
 'reservedPath': '__process_reserved_rpc_request' in s,
 'connectorPath': '__process_connector_rpc_request' in s,
 'writeFunctionCodes': [5,6,15,16] if "in (5, 6, 15, 16)" in s else [],
 'attributeUpdateHandler': '__process_attribute_update' in s}))
''')
    try:
        source = json.loads(source)
    except (TypeError, json.JSONDecodeError):
        source = {"_error": "cannot_inspect_connector_source"}
    return {"container": "tb-gateway", "imageReference": image_ref,
            "imageId": image_id, "runtimeVersion": version,
            "activeModbusConnectors": active, "sourceCapabilities": source,
            "downlinkVerdict": {
                "configuredMappingsEmpty": bool(isinstance(active, list) and all(
                    not any(x["rpcCounts"]) and not any(x["attributeUpdateCounts"]) for x in active)),
                "safeAgainstReservedOrConnectorRpc": False,
                "reason": "Installed handler supports RESERVED and CONNECTOR paths; empty device rpc mappings do not prove downlink is impossible.",
                "requiredBeforeAlarmEmission": "Deploy and verify a read-only connector subclass that no-ops server_side_rpc_handler and on_attributes_update."
            }}


def relation(tb, ident, direction, entity_type="ASSET"):
    rows = get(tb, "/api/relations/info?%sId=%s&%sType=%s" %
               (direction, ident, direction, entity_type))
    if not isinstance(rows, list):
        return rows
    return [{"type": r.get("type"),
             "from": {"entityType": r.get("from", {}).get("entityType"),
                      "id": entity_id(r.get("from")), "name": r.get("fromName")},
             "to": {"entityType": r.get("to", {}).get("entityType"),
                    "id": entity_id(r.get("to")), "name": r.get("toName")}}
            for r in rows]


def main():
    tb = GuardedTB()
    devices, assets = page(tb, "/api/tenant/devices"), page(tb, "/api/tenant/assets")
    profiles, chains = page(tb, "/api/deviceProfiles"), page(tb, "/api/ruleChains")
    profile = next((p for p in profiles if p.get("name") == "SIM-VentController"), None)
    full_profile = get(tb, "/api/deviceProfile/" + profile["id"]["id"]) if profile else None
    barns = []
    area_ids = {}
    for asset in assets:
        if asset.get("name") in BARNS:
            incoming = relation(tb, asset["id"]["id"], "to")
            for r in incoming if isinstance(incoming, list) else []:
                if r["type"] == "AreaToBarn": area_ids[r["from"]["id"]] = r["from"]["name"]
            barns.append({"name": asset["name"], "id": asset["id"]["id"], "type": asset.get("type"),
                          "tenantId": entity_id(asset.get("tenantId")), "customerId": asset.get("customerId"),
                          "incoming": incoming, "outgoing": relation(tb, asset["id"]["id"], "from")})
    ancestors = {name: relation(tb, ident, "to") for ident, name in area_ids.items()}
    root = next((c for c in chains if c.get("root")), None)
    root_md = get(tb, "/api/ruleChain/%s/metadata" % root["id"]["id"]) if root else None
    chain_nodes, chain_connections = [], []
    if isinstance(root_md, dict):
        chain_nodes = [{"index": i, "name": n.get("name"), "type": n.get("type")}
                       for i, n in enumerate(root_md.get("nodes", []))]
        chain_connections = [{"fromIndex": c.get("fromIndex"), "toIndex": c.get("toIndex"),
                              "messageType": c.get("type")} for c in root_md.get("connections", [])]
    rules, targets = page(tb, "/api/notification/rules"), page(tb, "/api/notification/targets")
    alarm_rules = []
    for r in rules:
        full = get(tb, "/api/notification/rule/" + r["id"]["id"])
        if isinstance(full, dict) and full.get("triggerConfig", {}).get("triggerType") == "ALARM":
            template = get(tb, "/api/notification/template/" + full["templateId"]["id"])
            methods = []
            if isinstance(template, dict):
                d = template.get("configuration", {}).get("deliveryMethodsTemplates", {})
                methods = sorted(d) if isinstance(d, dict) else []
            alarm_rules.append({"id": r["id"]["id"], "name": full.get("name"), "enabled": full.get("enabled"),
                                "targetCount": len(full.get("targets") or []),
                                "trigger": full.get("triggerConfig", {}).get("notifyOn"),
                                "deliveryMethods": methods})
    dashboards = page(tb, "/api/tenant/dashboards")
    bundles = page(tb, "/api/widgetsBundles?tenantOnly=true")
    bundle = next((b for b in bundles if b.get("alias") == "siba_custom_ui"), None)
    bundle_fqns = get(tb, "/api/widgetsBundle/%s/widgetTypes" % bundle["id"]["id"]) if bundle else []
    collision = {n: [] for n in NAMES}
    for typ, rows in (("DEVICE", devices), ("ASSET", assets)):
        for row in rows:
            if row.get("name") in collision:
                collision[row["name"]].append({"entityType": typ, "id": row["id"]["id"], "type": row.get("type")})
    alarm_defs = []
    if isinstance(full_profile, dict):
        for a in full_profile.get("profileData", {}).get("alarms") or []:
            alarm_defs.append({"type": a.get("alarmType"), "severity": sorted(a.get("createRules", {})),
                               "propagate": a.get("propagate"), "propagateToOwner": a.get("propagateToOwner"),
                               "propagateToTenant": a.get("propagateToTenant")})
    report = {"task": "VENT-012", "checkedAt": now(), "tbUrl": TB_URL,
              "readOnly": {"api": "GET plus auth login only", "mutationsSent": tb.mutations},
              "gateway": gateway(),
              "profile": {"name": "SIM-VentController", "id": entity_id(profile.get("id")) if profile else None,
                          "defaultRuleChainId": profile.get("defaultRuleChainId") if profile else None,
                          "alarms": alarm_defs},
              "rootRuleChain": {"id": entity_id(root.get("id")) if root else None, "name": root.get("name") if root else None,
                                "nodes": chain_nodes, "connections": chain_connections,
                                "metadataSha256": sha(root_md) if isinstance(root_md, dict) else None},
              "notifications": {"alarmRules": alarm_rules,
                                "allTargetKinds": sorted({t.get("configuration", {}).get("type") for t in targets}),
                                "externalNotificationRisk": any(set(x["deliveryMethods"]) & {"EMAIL", "SMS", "SLACK", "WEBHOOK"} and x["targetCount"] for x in alarm_rules),
                                "verdict": "NO_CONFIGURED_EXTERNAL_PATH" if all(x["targetCount"] == 0 and set(x["deliveryMethods"]) <= {"WEB"} for x in alarm_rules) else "STOP_BEFORE_ALARM_EMISSION"},
              "barnGraph": {"barns": barns, "areaAncestors": ancestors}, "collisions": collision,
              "protectedFingerprints": {"dashboards": [{"id": d["id"]["id"], "title": d.get("title"), "version": d.get("version"),
                                                            "configurationSha256": sha(get(tb, "/api/dashboard/" + d["id"]["id"]).get("configuration"))}
                                                          for d in dashboards],
                                      "dashboardListSha256": sha([{k: d.get(k) for k in ("id", "title", "version")} for d in dashboards]),
                                      "bundle": {"id": entity_id(bundle.get("id")) if bundle else None, "alias": "siba_custom_ui",
                                                 "widgetFqnsSha256": sha(sorted(x.get("fqn") for x in bundle_fqns)) if isinstance(bundle_fqns, list) else None}},
              "_uncertain": ["Notification finding is a point-in-time API snapshot; re-run immediately before any alarm emission."]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS read-only report:", OUT)


if __name__ == "__main__":
    main()
