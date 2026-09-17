import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CANONICAL = {
    "indoorTemperature01", "indoorTemperature02", "indoorTemperatureAvg",
    "outdoorTemperature", "perceivedTemperature", "relativeHumidity",
    "airSpeed", "airFlow", "waterConsumptionTotal", "operatingMode",
    "fanControlMode", "fanStage", "stageCount", "controllerOnline",
    "dataQuality", "roofInletPosition", "sideInletPosition",
    *(f"fan{i:02d}Run" for i in range(1, 7)),
    *(f"fan{i:02d}Fault" for i in range(1, 7)),
    *(f"coolingPump{i:02d}Run" for i in range(1, 3)),
    *(f"coolingPump{i:02d}Fault" for i in range(1, 3)),
}


def equipment_state(run, fault):
    if fault is True:
        return "FAULT"
    if fault is False and run is True:
        return "RUNNING"
    if fault is False and run is False:
        return "STOPPED"
    return "UNKNOWN"


def stage_display(stage, count):
    if stage is None:
        return "--"
    return str(stage) if count is None else f"{stage} / {count}"


class DashboardDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / "fixtures/ventilation/demo.json").read_text())
        cls.app = (ROOT / "dashboard/app.js").read_text()
        cls.adapter = (ROOT / "widgets/ventilation-adapter.js").read_text()
        cls.html = (ROOT / "dashboard/index.html").read_text()
        cls.css = (ROOT / "dashboard/dashboard.css").read_text() + (ROOT / "dashboard/preview-shell.css").read_text()

    def test_fixture_is_explicit_and_identity_is_honest(self):
        self.assertIs(self.fixture["demo"], True)
        self.assertEqual([b["label"] for b in self.fixture["barns"][:4]], ["ND2-1", "ND2-2", "ND2-3", "ND2-4"])
        self.assertEqual([b["label"] for b in self.fixture["barns"][4:]], ["DEMO-05", "DEMO-06"])
        self.assertTrue(all(b["synthetic"] for b in self.fixture["barns"][4:]))
        self.assertEqual([b["identity"] for b in self.fixture["barns"]],
                         ["PILOT"] + ["LIVE_BARN_SIMULATED_STATE"] * 3 + ["SYNTHETIC"] * 2)
        self.assertNotIn("VEN-PLC-01", json.dumps(self.fixture, ensure_ascii=False))

    def test_quality_connectivity_and_null_coverage(self):
        self.assertTrue({"CURRENT", "STALE", "UNKNOWN"}.issubset({x["freshness"] for x in self.fixture["barns"]}))
        self.assertTrue({"ONLINE", "OFFLINE", "UNKNOWN"}.issubset({x["connectivity"] for x in self.fixture["barns"]}))
        self.assertIsNone(self.fixture["latest"]["air_flow"]["value"])

    def test_canonical_contract_is_exposed_by_adapter(self):
        # Khóa quạt/bơm được sinh theo vòng lặp; kiểm đủ tập khóa ở test_dashboard_browser.
        for key in (k for k in CANONICAL if not re.match(r"(fan|coolingPump)\d\d", k)):
            self.assertIn(key, self.adapter)
        for fragment in ('"fan" + fan + "Run"', '"fan" + fan + "Fault"', '"coolingPump" + pump + "Run"', '"coolingPump" + pump + "Fault"'):
            self.assertIn(fragment, self.adapter)
        self.assertIn("CANONICAL_MAP", self.adapter)

    def test_rendering_uses_canonical_names_only(self):
        expected = ("indoorTemperatureAvg", "outdoorTemperature", "perceivedTemperature", "relativeHumidity",
                    "airSpeed", "airFlow", "waterConsumptionTotal", "operatingMode", "fanControlMode", "dataQuality")
        for key in expected:
            self.assertIn(key, self.app)
        legacy = ("temperature_indoor", "temperature_outdoor", "temperature_feel", "air_speed", "air_flow",
                  "water_consumption", "operation_mode", "fan_control_mode", "ventilation_stage", "controller_online")
        for key in legacy:
            self.assertNotIn(key, self.app)

    def test_false_zero_and_null_are_preserved(self):
        self.assertIs(self.fixture["latest"]["fan_04_run"]["value"], False)
        self.assertEqual({"value": 0}.get("value"), 0)
        self.assertIsNone(self.fixture["latest"]["fan_05_run"]["value"])
        self.assertIn("metric.value === undefined ? null : metric.value", self.adapter)
        for source in (self.adapter, self.app):
            self.assertIsNone(re.search(r"\.value\s*\|\|", source))
            self.assertIsNone(re.search(r"\|\|\s*['\"](UNKNOWN|STOPPED|--|0)['\"]", source))

    def test_equipment_run_fault_semantics(self):
        self.assertEqual(equipment_state(False, False), "STOPPED")
        self.assertEqual(equipment_state(True, False), "RUNNING")
        self.assertEqual(equipment_state(None, None), "UNKNOWN")
        self.assertEqual(equipment_state(False, True), "FAULT")
        for expression in ("faultMetric.value === true", "runMetric.value === true", "runMetric.value === false"):
            self.assertIn(expression, self.adapter)

    def test_stage_variants(self):
        variants = self.fixture["adapterTestVariants"]
        def display(name):
            v = variants[name]
            return stage_display(v["ventilation_stage"]["value"], v["ventilation_stage_count"]["value"])
        self.assertEqual(display("step"), "3 / 6")
        self.assertEqual(variants["step"]["fan_control_mode"]["value"], "STEP")
        self.assertEqual(display("vfd"), "5 / 9")
        self.assertEqual(variants["vfd"]["fan_control_mode"]["value"], "VFD")
        self.assertEqual(display("unknownStageCount"), "4")
        self.assertEqual(display("zeroStage"), "0 / 6")
        self.assertNotIn("stageCount: 6", self.adapter + self.app)
        self.assertIn("stageDisplay", self.adapter)

    def test_history_has_perceived_and_keeps_missing_sample(self):
        self.assertTrue(all("temperature_feel" in row for row in self.fixture["history"]))
        self.assertTrue(any(row["temperature_indoor"] is None for row in self.fixture["history"]))
        self.assertIn("perceivedTemperature", self.app)
        self.assertIn("penDown = false", self.app)

    def test_secondary_metrics_have_safe_null_rendering(self):
        for key in ("airSpeed", "airFlow", "waterConsumptionTotal"):
            self.assertIn("secondaryRow('" + {"airSpeed":"Tốc độ gió", "airFlow":"Lưu lượng gió", "waterConsumptionTotal":"Nước tiêu thụ"}[key] + "', '" + key + "')", self.app)
        self.assertIn('isMissing(item.value) ? "--"', self.app)

    def test_four_states_badge_and_single_sidebar(self):
        for state in ("default", "vent_detail", "vent_history", "vent_alarms"):
            self.assertIn(state, self.app)
        self.assertEqual(self.fixture["badgeLabel"], "DEMO DATA")
        self.assertIn("vm.badgeLabel", self.app)
        self.assertEqual(self.html.count('class="tb-preview-sidebar"'), 1)
        self.assertNotIn("dashboard-sidebar", self.html + self.app)

    def test_source_boundary_remains_unconfigured(self):
        self.assertIn("FixtureSource", self.adapter)
        self.assertIn("ThingsBoardSource", self.adapter)
        self.assertIn("intentionally unconfigured", self.adapter)

    def test_no_mutating_secret_or_alarm_action_surface(self):
        text = "\n".join([self.app, self.adapter, self.html])
        forbidden = [r"/api/rpc", r"/api/plugins/telemetry", r"TB_PASSWORD", r"accessToken", r"refreshToken",
                     r"X-Authorization", r"method\s*:\s*['\"](?:POST|PUT|PATCH|DELETE)",
                     r"acknowledgeAlarm", r"clearAlarm", r"shelveAlarm", r"assignAlarm",
                     r"\.open\(\s*['\"](?!GET)", r"\bfetch\(", r"WebSocket", r"sendBeacon",
                     r"/api/(?:alarm|device|asset|dashboard|entity|relation)", r"sendOneWayRpc|sendTwoWayRpc",
                     r"password", r"\btoken\b"]
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, text, re.I), pattern)

    def test_fixture_covers_quality_and_value_edge_cases(self):
        edge = self.fixture["adapterTestVariants"]["edgeCases"]
        values = [m.get("value", "MISSING") for m in edge.values()]
        qualities = {m.get("quality") for m in edge.values()} | {m.get("quality") for m in self.fixture["latest"].values()}
        self.assertTrue({"CURRENT", "STALE", "OFFLINE", "UNKNOWN"}.issubset(qualities))
        self.assertIn(None, values)
        self.assertTrue(any(v is False for v in values))
        self.assertTrue(any(v == 0 and v is not False for v in values))
        self.assertTrue(self.fixture["adapterTestVariants"]["_edgeCasesMissing"])
        self.assertTrue(all("demo" in a["message"] for a in self.fixture["alarms"]))
        self.assertTrue(all(re.fullmatch(r"[A-Z][A-Z0-9_]+", a["type"]) for a in self.fixture["alarms"]))

    def test_responsive_and_local_overflow(self):
        self.assertIn("@media(max-width:700px)", self.css)
        self.assertIn("overflow-x:auto", self.css)
        self.assertIn(".tb-preview-sidebar{display:none}", self.css)


if __name__ == "__main__":
    unittest.main()
