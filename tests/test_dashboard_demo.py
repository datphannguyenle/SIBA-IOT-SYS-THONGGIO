"""Kiểm tĩnh demo thông gió theo Data Contract v0.3 (VENT-007)."""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "docs/ventilation/contract/SIBA_Ventilation_Agent_DataContract_v0.3.json").read_text())
CONTRACT_KEYS = {v["key"]: v for v in CONTRACT["variables"]}
REMOVED = {"stageCount", *(f"fan{i:02d}Fault" for i in range(1, 7)), "coolingPump01Fault", "coolingPump02Fault"}
LEGACY_SNAKE = ("temperature_indoor", "temperature_outdoor", "temperature_feel", "air_speed", "air_flow",
                "water_consumption", "operation_mode", "fan_control_mode", "ventilation_stage", "controller_online",
                "data_quality", "fan_01_run", "pump_01_run", "roof_louver_position")


class DashboardDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / "fixtures/ventilation/demo.json").read_text())
        cls.app = (ROOT / "dashboard/app.js").read_text()
        cls.adapter = (ROOT / "widgets/ventilation-adapter.js").read_text()
        cls.html = (ROOT / "dashboard/index.html").read_text()
        cls.css = (ROOT / "dashboard/dashboard.css").read_text() + (ROOT / "dashboard/preview-shell.css").read_text()

    def test_fixture_is_explicit_demo_v2_bound_to_contract(self):
        self.assertIs(self.fixture["demo"], True)
        self.assertEqual(self.fixture["fixtureVersion"], "2.0.0")
        self.assertEqual(self.fixture["contract"]["version"], "0.3")
        self.assertEqual([b["label"] for b in self.fixture["barns"][:4]], ["ND2-1", "ND2-2", "ND2-3", "ND2-4"])
        self.assertEqual([b["identity"] for b in self.fixture["barns"]],
                         ["PILOT"] + ["LIVE_BARN_SIMULATED_STATE"] * 3 + ["SYNTHETIC"] * 2)
        self.assertNotIn("VEN-PLC-01", json.dumps(self.fixture, ensure_ascii=False))

    def test_latest_uses_contract_keys_and_plc_encodings(self):
        latest = self.fixture["latest"]
        for key, sample in latest.items():
            self.assertIn(key, CONTRACT_KEYS, key)
            self.assertNotEqual(CONTRACT_KEYS[key]["role"], "setting", key)
            value = sample["value"]
            if value is None:
                continue
            if CONTRACT_KEYS[key]["data_type"]["logical"] == "uint16":
                self.assertTrue(isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 65535, key)
            else:
                self.assertTrue(isinstance(value, (int, float)) and not isinstance(value, bool), key)
        for key in REMOVED | set(self.fixture["platform"]):
            self.assertNotIn(key, latest)
        for barn in self.fixture["barns"]:
            self.assertNotIn("stageCount", barn)

    def test_platform_derived_block_is_separate(self):
        platform = {k for k in self.fixture["platform"] if not k.startswith("_")}
        self.assertEqual(platform, {"controllerOnline", "dataQuality"})
        self.assertTrue(platform.isdisjoint(CONTRACT_KEYS))

    def test_not_configured_mapping_is_explicit_and_valid(self):
        nc = self.fixture["mapping"]["notConfigured"]
        self.assertTrue(set(nc) <= set(CONTRACT_KEYS))
        self.assertIn("coolingPump02Run", nc)
        # Thiếu telemetry (fan05Run null) KHÔNG nằm trong danh sách N/A.
        self.assertIsNone(self.fixture["latest"]["fan05Run"]["value"])
        self.assertNotIn("fan05Run", nc)
        for key in nc:
            self.assertNotIn(key, self.fixture["latest"])

    def test_no_per_device_fault_demo_system_fault_only(self):
        text = json.dumps(self.fixture, ensure_ascii=False)
        self.assertNotIn("Quạt 06 báo lỗi", text)
        self.assertEqual(self.fixture["latest"]["equipmentFaultActive"]["value"], 1)
        self.assertEqual({a["source"] for a in self.fixture["alarms"]}, {"PLC", "PLATFORM"})
        self.assertTrue(all(re.fullmatch(r"[A-Z][A-Z0-9_]+", a["type"]) for a in self.fixture["alarms"]))
        self.assertTrue(all("demo" in a["message"] for a in self.fixture["alarms"]))

    def test_history_has_seven_series_and_no_fabricated_air_water(self):
        for row in self.fixture["history"]:
            self.assertEqual(set(row) - {"ts", "quality"}, set(CONTRACT["dashboard_organization"]["history_candidates"]))
            for key in ("airSpeed", "airFlow", "waterConsumptionTotal"):
                self.assertIsNone(row[key])
        self.assertTrue(any(row["indoorTemperatureAvg"] is None for row in self.fixture["history"]))

    def test_settings_default_empty(self):
        self.assertEqual(self.fixture["settings"], {})

    def test_dashboard_model_has_no_removed_or_legacy_keys(self):
        for source in (self.app, self.adapter):
            for key in REMOVED:
                self.assertNotIn(key, source, key)
            for key in LEGACY_SNAKE:
                self.assertNotIn(key, source, key)
        self.assertNotIn("CANONICAL_MAP", self.adapter)
        self.assertIsNone(re.search(r"\d+ / \d+", self.app))

    def test_false_zero_null_not_coerced(self):
        for source in (self.adapter, self.app):
            self.assertIsNone(re.search(r"\.value\s*\|\|", source))
            self.assertIsNone(re.search(r"\|\|\s*['\"](UNKNOWN|STOPPED|--|0)['\"]", source))

    def test_five_states_badge_and_single_sidebar(self):
        for state in ("default", "vent_detail", "vent_history", "vent_alarms", "vent_settings"):
            self.assertIn('"%s"' % state, self.app)
        self.assertIn('vent_settings: "Cài đặt"', self.app)
        self.assertEqual(self.fixture["badgeLabel"], "DEMO DATA")
        self.assertEqual(self.html.count('class="tb-preview-sidebar"'), 1)
        self.assertLess(self.html.index("ventilation-contract-v03.js"), self.html.index("ventilation-adapter.js"))

    def test_source_boundary_remains_unconfigured(self):
        self.assertIn("FixtureSource", self.adapter)
        self.assertIn("intentionally unconfigured", self.adapter)

    def test_no_mutating_secret_or_alarm_action_surface(self):
        text = "\n".join([self.app, self.adapter, self.html])
        forbidden = [r"/api/rpc", r"/api/plugins/telemetry", r"TB_PASSWORD", r"accessToken", r"refreshToken",
                     r"X-Authorization", r"method\s*:\s*['\"](?:POST|PUT|PATCH|DELETE)",
                     r"acknowledgeAlarm", r"clearAlarm", r"shelveAlarm", r"assignAlarm",
                     r"\.open\(\s*['\"](?!GET)", r"\bfetch\(", r"WebSocket", r"sendBeacon",
                     r"/api/(?:alarm|device|asset|dashboard|entity|relation)", r"sendOneWayRpc|sendTwoWayRpc",
                     r"saveEntityAttributes|attributeService|controlApi", r"password", r"\btoken\b",
                     r"<input|<select|<textarea|<form", r"\bD1[0-4]\d\d\b"]
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, text, re.I), pattern)

    def test_responsive_and_local_overflow(self):
        self.assertIn("@media(max-width:700px)", self.css)
        self.assertIn("overflow-x:auto", self.css)
        self.assertIn(".tb-preview-sidebar{display:none}", self.css)


if __name__ == "__main__":
    unittest.main()
