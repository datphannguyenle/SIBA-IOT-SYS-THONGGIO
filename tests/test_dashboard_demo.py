import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class DashboardDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / "fixtures/ventilation/demo.json").read_text())
        cls.app = (ROOT / "dashboard/app.js").read_text()
        cls.adapter = (ROOT / "widgets/ventilation-adapter.js").read_text()
        cls.html = (ROOT / "dashboard/index.html").read_text()
        cls.css = (ROOT / "dashboard/dashboard.css").read_text()

    def test_fixture_is_explicit_and_covers_quality_states(self):
        self.assertIs(self.fixture["demo"], True)
        qualities = {x["freshness"] for x in self.fixture["barns"]}
        self.assertTrue({"CURRENT", "STALE", "UNKNOWN"}.issubset(qualities))
        connectivity = {x["connectivity"] for x in self.fixture["barns"]}
        self.assertTrue({"ONLINE", "OFFLINE", "UNKNOWN"}.issubset(connectivity))
        self.assertIsNone(self.fixture["latest"]["air_flow"]["value"])

    def test_all_canonical_keys_exist(self):
        contract = json.loads((ROOT / "config/ventilation_data_contract.json").read_text())
        expected = {field["key"] for field in contract["fields"]}
        self.assertEqual(expected, set(self.fixture["latest"]))

    def test_four_states_and_persistent_badge(self):
        for state in ("default", "vent_detail", "vent_history", "vent_alarms"):
            self.assertIn(state, self.app)
        self.assertEqual(self.fixture["badgeLabel"], "DEMO DATA")
        self.assertIn("vm.badgeLabel", self.app)

    def test_one_preview_sidebar_no_dashboard_sidebar(self):
        self.assertEqual(self.html.count('class="tb-preview-sidebar"'), 1)
        self.assertNotIn("dashboard-sidebar", self.html + self.app)

    def test_source_boundary_is_explicit(self):
        self.assertIn("FixtureSource", self.adapter)
        self.assertIn("ThingsBoardSource", self.adapter)
        self.assertIn("intentionally unconfigured", self.adapter)

    def test_no_mutating_or_secret_surface(self):
        text = "\n".join([self.app, self.adapter, self.html])
        forbidden = [r"/api/rpc", r"/api/plugins/telemetry", r"TB_PASSWORD", r"refreshToken", r"X-Authorization", r"method\s*:\s*['\"](?:POST|PUT|PATCH|DELETE)"]
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, text, re.I), pattern)

    def test_responsive_and_local_overflow(self):
        self.assertIn("@media(max-width:700px)", self.css)
        self.assertIn("overflow-x:auto", self.css)
        self.assertIn(".tb-preview-sidebar{display:none}", self.css)


if __name__ == "__main__":
    unittest.main()
