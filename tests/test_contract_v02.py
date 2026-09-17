"""VENT-007: dashboard model phải khớp Data Contract v0.2 và quyết định dự án."""
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/ventilation/contract/SIBA_Ventilation_Agent_DataContract_v0.2.json"
DECISIONS = json.loads((ROOT / "docs/ventilation/contract/contract_v0.2_decisions.json").read_text())


class ContractV02Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = CONTRACT_PATH.read_bytes()
        cls.contract = json.loads(cls.raw)
        cls.keys = {v["key"]: v for v in cls.contract["variables"]}
        cls.adapter = (ROOT / "widgets/ventilation-adapter.js").read_text()

    def test_source_contract_is_unmodified(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), DECISIONS["contractSha256"])
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),
                         "f25cd7ab9608f1fa04560274a4ff5e39c7428b9ee6049f3335fc1392870c60db")

    def test_contract_counts_and_mirror_block(self):
        variables = self.contract["variables"]
        self.assertEqual(len(variables), 265)
        self.assertEqual(sum(v["role"] == "setting" for v in variables), 224)
        used = []
        for v in variables:
            self.assertEqual(v["mirror"]["plc_end"] - v["mirror"]["plc_start"] + 1, v["data_type"]["words"], v["key"])
            used += range(v["mirror"]["plc_start"], v["mirror"]["plc_end"] + 1)
        self.assertEqual(sorted(used), list(range(1000, 1410)))
        self.assertTrue(all(v["plc_source"] == {"tag": None, "domain": None, "source_type": None} for v in variables))

    def test_generated_module_matches_sources(self):
        subprocess.run([sys.executable, "tools/build_contract_module.py", "--check"], cwd=ROOT, check=True, capture_output=True)

    def test_approved_enums_and_codes(self):
        self.assertEqual(DECISIONS["enums"], {
            "operatingMode": {"0": "MANUAL", "1": "AUTO"},
            "controlBasis": {"0": "ACTUAL_TEMPERATURE", "1": "PERCEIVED_TEMPERATURE"},
            "fanControlMode": {"0": "STEP", "1": "VFD"},
            "dehumidificationEnabled": {"0": "DISABLED", "1": "ENABLED"}})
        self.assertEqual(DECISIONS["equipmentRunCodes"], {"0": "STOPPED", "1": "RUNNING"})
        for key in DECISIONS["enums"]:
            self.assertEqual(self.keys[key]["data_type"]["logical"], "uint16")
        for alias, base in DECISIONS["settingEnumAliases"].items():
            self.assertEqual(self.keys[alias]["role"], "setting")
            self.assertIn(base, DECISIONS["enums"])

    def test_platform_derived_and_removed_keys_are_not_plc_variables(self):
        for key in DECISIONS["platformDerived"] + DECISIONS["removedFromDashboardModel"]:
            self.assertNotIn(key, self.keys)

    def test_adapter_hardcoded_keys_exist_in_contract(self):
        for name in ("RUN_KEYS", "FLAG_KEYS", "HISTORY_KEYS"):
            block = re.search(r"var %s = \[(.*?)\];" % name, self.adapter, re.S).group(1)
            for key in re.findall(r'"(\w+)"', block):
                self.assertIn(key, self.keys, key)
        org = self.contract["dashboard_organization"]
        run_keys = re.findall(r'"(\w+)"', re.search(r"var RUN_KEYS = \[(.*?)\];", self.adapter, re.S).group(1))
        self.assertEqual(run_keys, org["equipment_status"])
        history = re.findall(r'"(\w+)"', re.search(r"var HISTORY_KEYS = \[(.*?)\];", self.adapter, re.S).group(1))
        self.assertEqual(history, org["history_candidates"])
        flags = re.findall(r'"(\w+)"', re.search(r"var FLAG_KEYS = \[(.*?)\];", self.adapter, re.S).group(1))
        self.assertEqual(sorted(flags), sorted(org["alarm_candidates"]))

    def test_missing_excel_recorded(self):
        self.assertIn("SIBA_Ventilation_PLC_HMI_TB_Mapping_TEMPLATE_v0.2.xlsx", DECISIONS["missingArtifacts"])
        self.assertIn("CHƯA CÓ", (ROOT / "docs/ventilation/contract/README.md").read_text())


if __name__ == "__main__":
    unittest.main()
