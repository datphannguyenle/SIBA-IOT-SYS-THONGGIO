"""Chạy adapter và bốn state thật trong Firefox headless (bỏ qua nếu thiếu geckodriver)."""
import json
import unittest

from webdriver_support import ROOT, Browser, StaticServer, geckodriver_path

FIXTURE = json.loads((ROOT / "fixtures/ventilation/demo.json").read_text())

BUILD_VM = """
var raw = JSON.parse(arguments[0]), patch = arguments[1] || {}, drop = arguments[2] || [];
Object.keys(patch).forEach(function (key) { raw.latest[key] = patch[key]; });
drop.forEach(function (key) { delete raw.latest[key]; });
return VentilationAdapter.createViewModel(raw);
"""


@unittest.skipUnless(geckodriver_path(), "geckodriver không có; bỏ qua test trình duyệt")
class DashboardBrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = StaticServer().__enter__()
        cls.browser = Browser()
        cls.url = cls.server.base_url + "/dashboard/index.html"
        cls.raw = json.dumps(FIXTURE)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.__exit__(None, None, None)

    def open_state(self, state):
        self.browser.open(self.url + "#" + state)
        self.browser.run("location.hash = arguments[0]", state)
        self.browser.wait_for("return !!document.querySelector('.state-tabs a.active[href=\"#%s\"]')" % state)

    def vm(self, patch=None, drop=None):
        return self.browser.run(BUILD_VM, self.raw, patch or {}, drop or [])

    def variant(self, name):
        return {k: v for k, v in FIXTURE["adapterTestVariants"][name].items()}

    # --- Model chuẩn ---
    def test_canonical_view_model_keys(self):
        self.open_state("default")
        keys = set(self.vm()["metrics"].keys())
        expected = {"indoorTemperature01", "indoorTemperature02", "indoorTemperatureAvg", "outdoorTemperature",
                    "perceivedTemperature", "relativeHumidity", "airSpeed", "airFlow", "waterConsumptionTotal",
                    "operatingMode", "fanControlMode", "fanStage", "stageCount", "controllerOnline", "dataQuality",
                    "roofInletPosition", "sideInletPosition",
                    *("fan%02dRun" % i for i in range(1, 7)), *("fan%02dFault" % i for i in range(1, 7)),
                    *("coolingPump%02dRun" % i for i in range(1, 3)), *("coolingPump%02dFault" % i for i in range(1, 3))}
        self.assertEqual(keys, expected)
        self.assertFalse(any("_" in key for key in keys))

    def test_false_zero_null_missing_are_distinct(self):
        self.open_state("default")
        vm = self.vm(self.variant("edgeCases"), FIXTURE["adapterTestVariants"]["_edgeCasesMissing"])
        m = vm["metrics"]
        self.assertEqual(m["sideInletPosition"]["value"], 0)
        self.assertIsNot(m["sideInletPosition"]["value"], False)
        self.assertEqual(m["airFlow"]["value"], 0)
        self.assertIsNone(m["roofInletPosition"]["value"])
        self.assertEqual(m["roofInletPosition"]["quality"], "STALE")
        self.assertIs(m["controllerOnline"]["value"], False)
        self.assertEqual(vm["controller"]["online"], "OFFLINE")
        self.assertIsNone(m["perceivedTemperature"]["value"])
        self.assertEqual(m["perceivedTemperature"]["quality"], "UNKNOWN")
        self.assertIsNone(m["waterConsumptionTotal"]["value"])

    def test_equipment_state_derivation(self):
        self.open_state("default")
        vm = self.vm(self.variant("edgeCases"), FIXTURE["adapterTestVariants"]["_edgeCasesMissing"])
        states = {row["key"]: row for row in vm["equipment"]}
        self.assertEqual(states["fan01"]["state"], "STOPPED")      # false/false giữ STOPPED
        self.assertEqual(states["fan02"]["state"], "FAULT")        # fault thắng run
        self.assertEqual(states["fan03"]["state"], "UNKNOWN")      # run null không thành STOPPED
        self.assertEqual(states["fan04"]["state"], "STOPPED")
        self.assertEqual(states["fan04"]["quality"], "OFFLINE")
        self.assertEqual(states["fan05"]["state"], "UNKNOWN")      # thiếu khóa fault
        self.assertEqual(states["fan06"]["state"], "UNKNOWN")      # 0 không phải boolean
        base = {row["key"]: row["state"] for row in self.vm()["equipment"]}
        self.assertEqual(base["fan04"], "STOPPED")
        self.assertEqual(base["fan06"], "FAULT")
        self.assertEqual(base["coolingPump02"], "UNKNOWN")

    def test_stage_variants(self):
        self.open_state("default")
        cases = {"step": ("STEP", "3 / 6"), "vfd": ("VFD", "5 / 9"), "unknownStageCount": ("STEP", "4")}
        for name, (mode, display) in cases.items():
            vm = self.vm(self.variant(name))
            self.assertEqual(vm["metrics"]["fanControlMode"]["value"], mode)
            self.assertEqual(vm["controller"]["stageDisplay"], display, name)
        self.assertEqual(self.vm(self.variant("zeroStage"))["controller"]["stageDisplay"], "0 / 6")
        self.assertEqual(self.vm({"ventilation_stage": {"value": None}})["controller"]["stageDisplay"], "--")

    def test_history_mapping_keeps_gaps(self):
        self.open_state("default")
        history = self.vm()["history"]
        self.assertTrue(all(isinstance(row["perceivedTemperature"], (int, float)) for row in history))
        self.assertIn(None, [row["indoorTemperatureAvg"] for row in history])
        mapped = self.browser.run("return VentilationAdapter.mapHistory({ts: 1, humidity: 0})")
        self.assertEqual(mapped["relativeHumidity"], 0)
        self.assertIsNone(mapped["indoorTemperatureAvg"])
        self.assertEqual(mapped["quality"], "UNKNOWN")

    def test_non_demo_fixture_rejected_and_tb_source_unconfigured(self):
        self.open_state("default")
        err = self.browser.run("try { VentilationAdapter.createViewModel({demo: false}); return null; } catch (e) { return e.message; }")
        self.assertIn("demo", err)
        self.assertIn("intentionally unconfigured", self.browser.run("return VentilationAdapter.ThingsBoardSource.prototype.load.toString()"))

    # --- DOM từng state ---
    def test_default_state(self):
        self.open_state("default")
        text = self.browser.run("return document.getElementById('app').innerText")
        self.assertIn("DEMO DATA", text)
        tags = self.browser.run("return [...document.querySelectorAll('.barn-card')].map(c => c.querySelector('b').innerText)")
        self.assertIn("PILOT · DEMO", tags[0])
        self.assertTrue(all("DEMO" in tag for tag in tags[1:4]))
        self.assertTrue(all("SYNTHETIC" in tag for tag in tags[4:]))

    def test_detail_state(self):
        self.open_state("vent_detail")
        text = self.browser.run("return document.getElementById('app').innerText")
        for label in ("Nhiệt độ trung bình", "Nhiệt độ ngoài trời", "Nhiệt độ cảm nhận", "Độ ẩm trong nhà",
                      "Kết nối", "Chế độ", "Điều khiển quạt", "Cấp hiện tại", "Chất lượng dữ liệu",
                      "Tốc độ gió", "Lưu lượng gió", "Nước tiêu thụ", "DEMO DATA"):
            self.assertIn(label, text)
        self.assertIn("4 / 6", text)
        secondary = self.browser.run("return [...document.querySelectorAll('.secondary-row b')].map(b => b.innerText)")
        self.assertEqual(secondary, ["--", "--", "--"])
        fans = self.browser.run("return [...document.querySelectorAll('.fan')].map(g => g.getAttribute('class'))")
        self.assertEqual(fans, ["fan RUNNING", "fan RUNNING", "fan RUNNING", "fan STOPPED", "fan UNKNOWN", "fan FAULT"])

    def test_history_state(self):
        self.open_state("vent_history")
        headers = self.browser.run("return [...document.querySelectorAll('.data-table th')].map(th => th.innerText)")
        self.assertEqual(headers, ["Thời gian", "Nhiệt độ trong", "Nhiệt độ ngoài", "Nhiệt độ cảm nhận", "Độ ẩm", "Chất lượng"])
        indoor = self.browser.run("return document.querySelector('.chart .inside').getAttribute('d')")
        perceived = self.browser.run("return document.querySelector('.chart .perceived').getAttribute('d')")
        self.assertEqual(indoor.count("M"), 2, "điểm thiếu phải tạo khoảng trống")
        self.assertEqual(perceived.count("M"), 1)
        cells = self.browser.run("return [...document.querySelectorAll('.data-table tbody td')].map(td => td.innerText)")
        self.assertIn("--", cells)
        self.assertNotIn("0 °C", cells)

    def test_alarms_state_read_only(self):
        self.open_state("vent_alarms")
        self.assertEqual(self.browser.run("return document.querySelectorAll('#app button, #app input, #app form').length"), 0)
        types = self.browser.run("return [...document.querySelectorAll('.data-table tbody b')].map(b => b.innerText)")
        self.assertTrue(types)
        self.assertTrue(all(t == t.upper() and " " not in t for t in types))
        self.assertIn("DEMO DATA", self.browser.run("return document.getElementById('app').innerText"))

    def test_mobile_has_no_page_overflow(self):
        self.browser.resize(390, 844)
        try:
            for state in ("default", "vent_detail", "vent_history", "vent_alarms"):
                self.open_state(state)
                overflow = self.browser.run("return document.documentElement.scrollWidth - document.documentElement.clientWidth")
                self.assertLessEqual(overflow, 0, state)
        finally:
            self.browser.resize(1920, 1080)


if __name__ == "__main__":
    unittest.main()
