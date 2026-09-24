"""VENT-012 UI/data boundaries in the local Firefox harness; no ThingsBoard connection."""
import json
import unittest

try:
    from webdriver_support import ROOT, Browser, StaticServer, geckodriver_path
except ModuleNotFoundError:
    from tests.webdriver_support import ROOT, Browser, StaticServer, geckodriver_path


@unittest.skipUnless(geckodriver_path(), "geckodriver chưa có trong môi trường kiểm thử")
class Vent012UiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / "fixtures/ventilation/demo.json").read_text())
        cls.scripts = [(ROOT / path).read_text() for path in (
            "widgets/ventilation-contract-v03.js", "widgets/ventilation-adapter.js",
            "widgets/ventilation-source.js", "dashboard/modular.js")]
        cls.server = StaticServer().__enter__()
        cls.browser = Browser()
        cls.browser._session("POST", "/url", {"url": cls.server.base_url + "/tests/tb_widget_harness.html"})

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.__exit__(None, None, None)

    def source(self, ctx, settings):
        return self.browser.run("""
          window.VentilationContract=undefined; window.VentilationAdapter=undefined; window.VentilationSource=undefined;
          arguments[0].slice(0,3).forEach(function(source){ new Function('window', source)(window); });
          return window.VentilationSource.createViewModel(arguments[1], arguments[2], arguments[3]);
        """, self.scripts, ctx, settings, self.fixture)

    def render(self, vm, component, state="vent_detail"):
        return self.browser.run("""
          window.VentilationModular=undefined; new Function('window', arguments[0][3])(window);
          var host=document.getElementById('tb-widget'); host.innerHTML=''; host.className='';
          window.VentilationModular.render(host, arguments[1], arguments[2], function(){}, {state:arguments[3]});
          return {text:host.innerText, html:host.innerHTML};
        """, self.scripts, vm, component, state)

    def test_missing_and_zero_remain_distinct(self):
        vm = self.source({"data": [
            {"dataKey": {"name": "stage"}, "data": [[1, "0"]]},
            {"dataKey": {"name": "temp"}, "data": [[1, ""]]},
        ]}, {"keyMap": {"fanStage": "stage", "indoorTemperatureAvg": "temp"}})
        self.assertEqual(vm["metrics"]["fanStage"]["value"], 0)
        self.assertIsNone(vm["metrics"]["indoorTemperatureAvg"]["value"])

    def test_alarm_object_is_readable_escaped_and_all_tb_severities_are_labeled(self):
        severities = ["CRITICAL", "MAJOR", "MINOR", "WARNING", "INDETERMINATE"]
        alarms = [{"id": severity, "status": "ACTIVE_UNACK", "severity": severity,
                   "type": "Kiểm thử", "details": {"note": "<img src=x>", "level": severity}}
                  for severity in severities]
        vm = self.source({"defaultSubscription": {"alarms": {"data": alarms}}},
                         {"provenance": {"kind": "SIM", "note": "mô phỏng kiểm thử"}})
        self.assertNotIn("[object Object]", [alarm["message"] for alarm in vm["alarms"]])
        rendered = self.render(vm, "alarms", "vent_alarms")
        for label in ("Nghiêm trọng", "Cao", "Thấp", "Cảnh báo", "Không xác định"):
            self.assertIn(label, rendered["text"])
        self.assertIn("note: &lt;img src=x&gt;", rendered["html"])
        self.assertNotIn("<img src=x>", rendered["html"])
        self.assertIn("SIM · Dữ liệu mô phỏng · mô phỏng kiểm thử", rendered["text"])

    def test_historical_observation_is_not_stale_and_keeps_zero(self):
        vm = self.source({"data": [
            {"dataKey": {"name": "indoor"}, "data": [[1, 0]]},
            {"dataKey": {"name": "outdoor"}, "data": [[1, 31]]},
        ]}, {"keyMap": {"indoorTemperatureAvg": "indoor", "outdoorTemperature": "outdoor"},
             "freshnessMs": {"indoorTemperatureAvg": 1, "outdoorTemperature": 1}, "provenance": "SIM"})
        self.assertEqual(vm["history"][0]["quality"], "HISTORICAL")
        self.assertEqual(vm["history"][0]["indoorTemperatureAvg"], 0)
        rendered = self.render(vm, "history", "vent_history")
        self.assertIn("Lịch sử", rendered["text"])
        self.assertNotIn("Dữ liệu cũ", rendered["text"])
        self.assertIn("SIM · Dữ liệu mô phỏng", rendered["text"])

    def test_simulation_invalid_keys_mask_retained_latest_value_but_not_history(self):
        vm = self.source({"data": [
            {"dataKey": {"name": "indoor"}, "data": [[1, 22], [2, 29]]},
            {"dataKey": {"name": "simInvalidKeys"}, "data": [[2, '["indoorTemperatureAvg"]']]},
        ]}, {"simulation": True, "keyMap": {"indoorTemperatureAvg": "indoor"},
             "freshnessMs": {"indoorTemperatureAvg": 999999999999}})
        self.assertEqual(vm["provenance"]["kind"], "SIM")
        self.assertIsNone(vm["metrics"]["indoorTemperatureAvg"]["value"])
        self.assertEqual(vm["metrics"]["indoorTemperatureAvg"]["quality"], "UNKNOWN")
        self.assertEqual(vm["history"][-1]["indoorTemperatureAvg"], 29)
        self.assertEqual(vm["mapping"]["invalidKeys"], ["indoorTemperatureAvg"])

    def test_overview_masks_retained_values_per_simulated_entity(self):
        datasource = {"entityId": {"entityType": "DEVICE", "id": "sim-1"},
                      "entityName": "ND2-1"}
        vm = self.source({"data": [
            {"datasource": datasource, "dataKey": {"name": "stage"}, "data": [[2, 5]]},
            {"datasource": datasource, "dataKey": {"name": "mode"}, "data": [[2, 1]]},
            {"datasource": datasource, "dataKey": {"name": "simInvalidKeys"},
             "data": [[2, '["fanStage","operatingMode"]']]},
        ]}, {"component": "overview", "simulation": True,
             "keyMap": {"fanStage": "stage", "operatingMode": "mode"}})
        self.assertEqual(len(vm["barns"]), 1)
        self.assertIsNone(vm["barns"][0]["stage"])
        self.assertEqual(vm["barns"][0]["mode"], "UNKNOWN")

    def test_provenance_default_and_sim_are_visible_in_header_and_cards(self):
        live = self.source({}, {})
        demo = self.source({}, {"sourceMode": "demo"})
        sim = self.source({}, {"simulation": True, "provenance": {"kind": "SIM", "label": "Mô phỏng thiết bị"}})
        self.assertEqual((live["provenance"]["kind"], demo["provenance"]["kind"], sim["provenance"]["kind"]),
                         ("LIVE", "DEMO", "SIM"))
        header = self.render(sim, "header")
        self.assertIn("SIM", header["text"])
        overview = self.render({"source": "thingsboard", "demo": False,
                                "provenance": sim["provenance"], "summary": {}, "barns": []}, "overview", "default")
        self.assertIn("SIM · Mô phỏng thiết bị", overview["text"])


if __name__ == "__main__":
    unittest.main()
