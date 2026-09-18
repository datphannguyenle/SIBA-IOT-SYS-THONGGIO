"""Sinh widgets/ventilation-contract-v03.js từ contract JSON gốc + file quyết định (VENT-007).

Chạy: python3 tools/build_contract_module.py [--check]
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/ventilation/contract/SIBA_Ventilation_Agent_DataContract_v0.3.json"
DECISIONS = ROOT / "docs/ventilation/contract/contract_v0.3_decisions.json"
OUT = ROOT / "widgets/ventilation-contract-v03.js"


def build():
    raw = CONTRACT.read_bytes()
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))
    sha = hashlib.sha256(raw).hexdigest()
    if sha != decisions["contractSha256"]:
        raise SystemExit("contract sha256 khác file quyết định: %s" % sha)
    contract = json.loads(raw)
    org = contract["dashboard_organization"]
    module = {
        "version": contract["version"],
        "sha256": sha,
        "groups": [{"name": g["name"], "role": g["role"]} for g in contract["groups"]],
        # [key, group, role, status, label_vi, unit, logical type]
        "variables": [[v["key"], v["group"], v["role"], v["status"], v["label_vi"], v["unit"], v["data_type"]["logical"]]
                      for v in contract["variables"]],
        "organization": {k: org[k] for k in ("overview_or_detail_primary", "equipment_status", "history_candidates", "alarm_candidates")},
        "enums": decisions["enums"],
        "settingEnumAliases": decisions["settingEnumAliases"],
        "equipmentRunCodes": decisions["equipmentRunCodes"],
        "flagDisplayCodes": decisions["flagDisplayCodes"],
        "platformDerived": decisions["platformDerived"],
        "removedFromDashboardModel": decisions["removedFromDashboardModel"],
    }
    body = json.dumps(module, ensure_ascii=False, separators=(",", ":"))
    return ("// SINH TỰ ĐỘNG bởi tools/build_contract_module.py từ Data Contract v0.3 + contract_v0.3_decisions.json.\n"
            "// KHÔNG sửa tay. Đây là mẫu giao diện dự án, chưa phải mapping PLC đã xác minh runtime.\n"
            "(function (root) {\n  \"use strict\";\n  root.VentilationContract = " + body + ";\n}(window));\n")


def main():
    text = build()
    if "--check" in sys.argv:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != text:
            raise SystemExit("widgets/ventilation-contract-v03.js lệch nguồn; chạy tools/build_contract_module.py")
        print("contract module khớp nguồn")
        return
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT), len(text), "bytes")


if __name__ == "__main__":
    main()
