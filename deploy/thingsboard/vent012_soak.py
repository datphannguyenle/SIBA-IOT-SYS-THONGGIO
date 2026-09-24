#!/usr/bin/env python3
"""Theo dõi VENT-012 trong 24 giờ bằng GET/auth-only, không đổi ThingsBoard.

State được ghi ngoài repository để tiến trình nền không làm worktree thay đổi.
Lệnh ``export`` chỉ được chạy thủ công sau khi soak kết thúc.
"""
import argparse
import datetime
import json
import os
import pathlib
import subprocess
import time

from vent_demo_common import GuardedTB

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "deploy/thingsboard/vent012_manifest.json"
DEFAULT_STATE = pathlib.Path.home() / ".config/siba-vent012-soak.json"
DEFAULT_OUTPUT = ROOT / "docs/ventilation/deployment/evidence/vent012_soak_24h.json"


def iso_now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def container(name, include_log_errors=False):
    raw = subprocess.check_output(["docker", "inspect", name], text=True)
    item = json.loads(raw)[0]
    state = item["State"]
    result = {"id": item["Id"], "image": item["Image"], "startedAt": state["StartedAt"],
              "restartCount": item["RestartCount"], "status": state["Status"],
              "health": state.get("Health", {}).get("Status")}
    if include_log_errors:
        # Không lưu log thô vì log có thể chứa nội dung nhạy cảm; chỉ đếm dấu hiệu lỗi.
        logs = subprocess.run(["docker", "logs", "--since", "70s", name], text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              timeout=20, check=False).stdout.lower()
        result["recentErrorLineCount"] = sum(
            1 for line in logs.splitlines() if "error" in line or "exception" in line)
    return result


def latest(tb, entity_id):
    keys = "simSourceTimestamp,simSequence,simInvalidKeys"
    status, body = tb.get("/api/plugins/telemetry/DEVICE/%s/values/timeseries?keys=%s&useStrictDataTypes=true" %
                          (entity_id, keys))
    if status == 401:
        tb = GuardedTB()
        status, body = tb.get("/api/plugins/telemetry/DEVICE/%s/values/timeseries?keys=%s&useStrictDataTypes=true" %
                              (entity_id, keys))
    if status != 200 or not isinstance(body, dict):
        return tb, {"http": status, "ok": False}
    try:
        source = body["simSourceTimestamp"][0]
        sequence = body["simSequence"][0]
        invalid = body["simInvalidKeys"][0]
        invalid_count = len(json.loads(invalid["value"]))
        now_ms = int(time.time() * 1000)
        return tb, {"http": 200, "ok": True, "sourceAgeSec": round((now_ms - int(source["value"])) / 1000, 3),
                    "envelopeAgeSec": round((now_ms - int(source["ts"])) / 1000, 3),
                    "sequence": int(sequence["value"]), "invalidKeyCount": invalid_count}
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
        return tb, {"http": 200, "ok": False, "parseError": True}


def summarize(samples, expected):
    ages = [v["sourceAgeSec"] for sample in samples for v in sample.get("devices", {}).values()
            if v.get("ok") and isinstance(v.get("sourceAgeSec"), (int, float))]
    invalid = sum(v.get("invalidKeyCount", 0) for sample in samples
                  for v in sample.get("devices", {}).values() if v.get("ok"))
    failures = sum(1 for sample in samples if not sample.get("ok"))
    return {"sampleCount": len(samples), "expectedSampleCount": expected,
            "failedSamples": failures, "maxSourceAgeSec": max(ages) if ages else None,
            "averageSourceAgeSec": round(sum(ages) / len(ages), 3) if ages else None,
            "invalidKeyObservations": invalid,
            "pass": len(samples) >= expected and failures == 0 and invalid == 0 and bool(ages)}


def run(args):
    manifest = json.loads(MANIFEST.read_text())
    baseline = {name: container(name) for name in ("tb-gateway", "tb-gateway-ventilation", "ventilation-plc-sim")}
    started = time.time(); end = started + args.hours * 3600; expected = max(1, int(args.hours * 3600 / args.interval))
    state = {"task": "VENT-012", "mode": "GET/auth-only soak", "startedAt": iso_now(),
             "plannedHours": args.hours, "intervalSec": args.interval, "baseline": baseline,
             "samples": [], "completed": False}
    args.state.parent.mkdir(parents=True, exist_ok=True)
    tb = GuardedTB()
    while time.time() < end:
        sample = {"at": iso_now(), "devices": {}, "ok": True}
        try:
            sample["containers"] = {
                name: container(name, include_log_errors=(name == "tb-gateway-ventilation"))
                for name in ("tb-gateway", "tb-gateway-ventilation", "ventilation-plc-sim")}
            for barn, entity_id in manifest["controllers"].items():
                tb, sample["devices"][barn] = latest(tb, entity_id)
            protected = sample["containers"]["tb-gateway"]
            sample["protectedGatewayUnchanged"] = all(
                protected[k] == baseline["tb-gateway"][k]
                for k in ("id", "image", "startedAt", "restartCount"))
            sample["ok"] = (sample["protectedGatewayUnchanged"] and
                            sample["containers"]["tb-gateway-ventilation"].get("health") == "healthy" and
                            sample["containers"]["ventilation-plc-sim"].get("health") == "healthy" and
                            all(v.get("ok") and v.get("sourceAgeSec", 10**9) <= 30 and
                                v.get("invalidKeyCount") == 0 for v in sample["devices"].values()))
        except (OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError) as error:
            sample.update(ok=False, monitorError=type(error).__name__)
        state["samples"].append(sample)
        state["summary"] = summarize(state["samples"], expected)
        temporary = args.state.with_suffix(args.state.suffix + ".tmp")
        temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
        temporary.replace(args.state)
        remaining = end - time.time()
        if remaining > 0:
            time.sleep(min(args.interval, remaining))
    state["completed"] = True; state["completedAt"] = iso_now()
    state["summary"] = summarize(state["samples"], expected)
    args.state.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    return 0 if state["summary"]["pass"] else 1


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    execute = sub.add_parser("run"); execute.add_argument("--hours", type=float, default=24)
    execute.add_argument("--interval", type=int, default=60)
    execute.add_argument("--state", type=pathlib.Path, default=DEFAULT_STATE)
    status = sub.add_parser("status"); status.add_argument("--state", type=pathlib.Path, default=DEFAULT_STATE)
    export = sub.add_parser("export"); export.add_argument("--state", type=pathlib.Path, default=DEFAULT_STATE)
    export.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.command == "run":
        raise SystemExit(run(args))
    state = json.loads(args.state.read_text())
    if args.command == "status":
        print(json.dumps({k: state.get(k) for k in ("startedAt", "plannedHours", "completedAt", "completed", "summary")},
                         ensure_ascii=False, indent=2))
        return
    if not state.get("completed"):
        raise SystemExit("Soak chưa hoàn thành; không xuất bằng chứng cuối")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    print("Wrote", args.output)


if __name__ == "__main__":
    main()
