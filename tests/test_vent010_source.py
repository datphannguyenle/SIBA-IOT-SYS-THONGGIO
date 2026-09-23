"""VENT-010 source boundary executed in the local Firefox harness, never against ThingsBoard."""
import json
import unittest

try:
    from webdriver_support import ROOT, Browser, StaticServer, geckodriver_path
except ModuleNotFoundError:  # unittest invoked from repository root
    from tests.webdriver_support import ROOT, Browser, StaticServer, geckodriver_path


@unittest.skipUnless(geckodriver_path(), "geckodriver chưa có trong môi trường kiểm thử")
class Vent010SourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / "fixtures/ventilation/demo.json").read_text())
        cls.scripts = [(ROOT / path).read_text() for path in (
            "widgets/ventilation-contract-v03.js", "widgets/ventilation-adapter.js", "widgets/ventilation-source.js")]
        cls.server = StaticServer().__enter__()
        cls.browser = Browser()
        cls.browser._session("POST", "/url", {"url": cls.server.base_url + "/tests/tb_widget_harness.html"})

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.__exit__(None, None, None)

    def run_source(self, ctx, settings, fixture=None):
        return self.browser.run("""
          window.VentilationContract = undefined; window.VentilationAdapter = undefined; window.VentilationSource = undefined;
          arguments[0].forEach(function (source) { new Function('window', source)(window); });
          return window.VentilationSource.createViewModel(arguments[1], arguments[2], arguments[3]);
        """, self.scripts, ctx, settings, fixture)

    def test_live_default_leaves_unmapped_values_unknown_not_na(self):
        vm = self.run_source({"data": [{"dataKey": {"name": "raw_temp"}, "data": [[1, 0]]}]}, {})
        self.assertEqual(vm["sourceMode"], "live")
        self.assertFalse(vm["demo"])
        self.assertEqual(vm["badgeLabel"], "")
        self.assertEqual(vm["mapping"]["status"], "UNRESOLVED")
        metric = vm["metrics"]["indoorTemperatureAvg"]
        self.assertTrue(metric["configured"])
        self.assertIsNone(metric["value"])
        self.assertEqual(metric["quality"], "UNKNOWN")

    def test_subscription_keeps_real_zero_and_empty_is_not_zero(self):
        ctx = {"data": [
            {"dataKey": {"name": "temp"}, "data": [[1000, ""]]},
            {"dataKey": {"name": "stage"}, "data": [[1000, "0"]]},
        ], "latestData": {"temp": {"value": None, "ts": 1001}}}
        vm = self.run_source(ctx, {"keyMap": {"indoorTemperatureAvg": "temp", "fanStage": "stage"}})
        self.assertIsNone(vm["metrics"]["indoorTemperatureAvg"]["value"])
        self.assertEqual(vm["metrics"]["fanStage"]["value"], 0)
        self.assertEqual(vm["controller"]["stageDisplay"], "0")

    def test_on_data_updated_rebuilds_same_live_context(self):
        settings = {"keyMap": {"fanStage": "stage"}}
        before = self.run_source({"data": [{"dataKey": {"name": "stage"}, "data": [[1, 1]]}]}, settings)
        after = self.run_source({"data": [{"dataKey": {"name": "stage"}, "data": [[2, 2]]}]}, settings)
        self.assertEqual(before["controller"]["stageDisplay"], "1")
        self.assertEqual(after["controller"]["stageDisplay"], "2")

    def test_stale_never_means_offline_and_future_timestamp_is_unknown(self):
        ctx = {"data": [{"dataKey": {"name": "temp"}, "data": [[0, 28.5]]}]}
        no_threshold = self.run_source(ctx, {"keyMap": {"indoorTemperatureAvg": "temp"}})
        self.assertEqual(no_threshold["metrics"]["indoorTemperatureAvg"]["quality"], "UNKNOWN")
        stale = self.run_source(ctx, {"keyMap": {"indoorTemperatureAvg": "temp"}, "freshnessMs": {"indoorTemperatureAvg": 1}})
        self.assertEqual(stale["metrics"]["indoorTemperatureAvg"]["quality"], "STALE")
        self.assertEqual(stale["controller"]["online"], "UNKNOWN")
        future = self.run_source({"data": [{"dataKey": {"name": "temp"}, "data": [[9999999999999, 28.5]]}]},
                                 {"keyMap": {"indoorTemperatureAvg": "temp"}, "freshnessMs": {"indoorTemperatureAvg": 1}})
        self.assertEqual(future["metrics"]["indoorTemperatureAvg"]["quality"], "UNKNOWN")

    def test_boolean_controller_value_is_preserved_and_invalid_enum_is_unknown(self):
        ctx = {"data": [
            {"dataKey": {"name": "online"}, "data": [[1, False]]},
            {"dataKey": {"name": "mode"}, "data": [[1, 7]]},
        ]}
        vm = self.run_source(ctx, {"keyMap": {"controllerOnline": "online", "operatingMode": "mode"},
                                   "freshnessMs": {"controllerOnline": 999999999999, "operatingMode": 999999999999}})
        self.assertIs(vm["metrics"]["controllerOnline"]["value"], False)
        self.assertEqual(vm["controller"]["online"], "OFFLINE")
        self.assertEqual(vm["metrics"]["operatingMode"]["value"], "UNKNOWN")
        self.assertEqual(vm["metrics"]["operatingMode"]["quality"], "UNKNOWN")

    def test_live_settings_history_and_active_alarm_normalization(self):
        ctx = {"data": [
            {"dataKey": {"name": "set"}, "data": [[1000, 0]]},
            {"dataKey": {"name": "indoor"}, "data": [[1000, 25], [2000, 26]]},
            {"dataKey": {"name": "outdoor"}, "data": [[1000, 30], [2000, 31]]},
        ], "defaultSubscription": {"alarms": {"data": [
            {"id": "a", "status": "ACTIVE_ACK"}, {"id": "b", "status": "CLEARED_ACK"}]}}}
        vm = self.run_source(ctx, {"keyMap": {"settingControlBasis": "set", "indoorTemperatureAvg": "indoor", "outdoorTemperature": "outdoor"}})
        settings = {item["key"]: item for group in vm["settings"] for item in group["items"]}
        self.assertEqual(settings["settingControlBasis"]["value"], "ACTUAL_TEMPERATURE")
        self.assertEqual([(row["ts"], row["indoorTemperatureAvg"], row["outdoorTemperature"]) for row in vm["history"]],
                         [(1000, 25, 30), (2000, 26, 31)])
        self.assertEqual([(alarm["id"], alarm["status"], alarm["rawStatus"], alarm["active"], alarm["acknowledged"])
                          for alarm in vm["alarms"]],
                         [("a", "ACTIVE", "ACTIVE_ACK", True, True), ("b", "RECOVERED", "CLEARED_ACK", False, True)])
        self.assertEqual(vm["alarmsSource"]["status"], "LOADED")

    def test_context_is_explicit_only_and_latest_uses_max_timestamp(self):
        rows = [{"dataKey": {"name": "temp"}, "data": [[20, 22], [10, 11], [30, 33]]}]
        unknown = self.run_source({"data": rows}, {"keyMap": {"indoorTemperatureAvg": "temp"}})
        configured = self.run_source({"data": rows, "stateController": {}},
                                     {"keyMap": {"indoorTemperatureAvg": "temp"},
                                      "context": {"farm": "Trại A", "area": "Khu 1", "barnLabel": "N1", "barnId": "n1"},
                                      "alarmScope": "Nhà N1"})
        self.assertEqual(unknown["metrics"]["indoorTemperatureAvg"]["value"], 33)
        self.assertEqual(unknown["scope"]["status"], "UNKNOWN")
        self.assertEqual(configured["scope"], {"farm": "Trại A", "area": "Khu 1", "selectedBarn": "N1",
                                                "selectedBarnId": "n1", "selectedControllerId": None, "status": "CONFIGURED"})
        self.assertEqual(configured["alarmsSource"]["scope"], "Nhà N1")

    def test_live_alarm_without_subscription_is_not_reported_as_zero(self):
        vm = self.run_source({}, {})
        self.assertEqual(vm["alarms"], [])
        self.assertEqual(vm["alarmsSource"], {"status": "NOT_LOADED", "loaded": False, "display": "-- / chưa nạp",
                                               "scope": "Chưa xác minh phạm vi"})

    def test_scope_identity_selects_one_controller_and_rejects_merged_rows(self):
        rows = [
            {"datasource": {"entityId": "A"}, "dataKey": {"name": "temp"}, "data": [[1, 21]]},
            {"datasource": {"entityId": "B"}, "dataKey": {"name": "temp"}, "data": [[2, 31]]},
        ]
        selected = self.run_source({"data": rows}, {"sourceIdentity": "A", "keyMap": {"indoorTemperatureAvg": "temp"}})
        rejected = self.run_source({"data": rows}, {"keyMap": {"indoorTemperatureAvg": "temp"}})
        self.assertEqual(selected["metrics"]["indoorTemperatureAvg"]["value"], 21)
        self.assertEqual(selected["mapping"]["scope"], "SELECTED")
        self.assertIsNone(rejected["metrics"]["indoorTemperatureAvg"]["value"])
        self.assertEqual(rejected["mapping"]["scope"], "MULTIPLE_ENTITIES_REJECTED")

    def test_demo_fixture_and_explicit_subscription_override(self):
        fixture_vm = self.run_source({}, {"sourceMode": "demo"}, self.fixture)
        self.assertEqual(fixture_vm["sourceMode"], "demo")
        self.assertEqual(fixture_vm["metrics"]["fanStage"]["value"], 4)
        self.assertEqual(fixture_vm["history"], self.fixture["history"])
        override = self.run_source({"data": [{"dataKey": {"name": "fanStage"}, "data": [[1, 2]]}]},
                                   {"sourceMode": "demo", "demoUseSubscription": True}, self.fixture)
        self.assertEqual(override["metrics"]["fanStage"]["value"], 2)
        self.assertIsNone(override["metrics"]["indoorTemperatureAvg"]["value"])


    # --- Danh sách nhà từ nhiều entity (màn Tổng quan) ---
    def overview_ctx(self):
        def rows(entity, label, stage, mode, online, fault):
            ds = {"entityId": {"entityType": "DEVICE", "id": entity}, "entityName": entity, "entityLabel": label}
            data = [("vent_stage", stage), ("vent_mode", mode), ("vent_online", online), ("vent_fault", fault)]
            # Entity có datasource nhưng chưa có telemetry vẫn gửi hàng rỗng, giống ThingsBoard.
            return [{"datasource": ds, "dataKey": {"name": key},
                     "data": [] if value is None else [[1_700_000_000_000, value]]}
                    for key, value in data]
        return {"data": rows("dev-1", "ND2-1", 4, 1, True, 0) + rows("dev-2", "ND2-2", 2, 0, False, 1)
                        + rows("dev-3", "ND2-3", None, None, None, None)}

    OVERVIEW_SETTINGS = {"component": "overview", "keyMap": {
        "fanStage": "vent_stage", "operatingMode": "vent_mode", "controllerOnline": "vent_online",
        "equipmentFaultActive": "vent_fault"}}

    def test_overview_lists_every_entity_without_merging(self):
        vm = self.run_source(self.overview_ctx(), self.OVERVIEW_SETTINGS)
        barns = {b["label"]: b for b in vm["barns"]}
        self.assertEqual(sorted(barns), ["ND2-1", "ND2-2", "ND2-3"])
        self.assertEqual(barns["ND2-1"]["id"], "dev-1")
        self.assertEqual((barns["ND2-1"]["stage"], barns["ND2-1"]["mode"], barns["ND2-1"]["connectivity"]), (4, "AUTO", "ONLINE"))
        self.assertEqual((barns["ND2-2"]["stage"], barns["ND2-2"]["mode"], barns["ND2-2"]["connectivity"]), (2, "MANUAL", "OFFLINE"))
        self.assertEqual(barns["ND2-1"]["alarm"], "NONE")
        self.assertEqual(barns["ND2-2"]["alarm"], "MAJOR")
        self.assertTrue(all(b["identity"] == "LIVE_ENTITY" and b["synthetic"] is False for b in vm["barns"]))
        self.assertEqual(vm["mapping"]["scope"], "MULTI_ENTITY_LIST")

    def test_overview_entity_without_telemetry_stays_unknown(self):
        vm = self.run_source(self.overview_ctx(), self.OVERVIEW_SETTINGS)
        empty = [b for b in vm["barns"] if b["label"] == "ND2-3"][0]
        self.assertEqual((empty["connectivity"], empty["mode"], empty["alarm"]), ("UNKNOWN", "UNKNOWN", "UNKNOWN"))
        self.assertIsNone(empty["stage"])
        self.assertEqual(empty["freshness"], "UNKNOWN")

    def test_overview_summary_counts_and_alarm_scope(self):
        vm = self.run_source(self.overview_ctx(), self.OVERVIEW_SETTINGS)
        summary = vm["summary"]
        self.assertEqual((summary["barns"], summary["online"], summary["attention"]), (3, 1, 3))
        # Số cảnh báo đang mở thuộc alarm nền tảng, không suy từ danh sách nhà.
        self.assertIsNone(summary["activeAlarms"])

    def test_overview_without_datasource_is_empty_not_fixture(self):
        vm = self.run_source({"data": []}, self.OVERVIEW_SETTINGS)
        self.assertEqual(vm["barns"], [])
        self.assertEqual(vm["summary"]["barns"], 0)
        self.assertFalse(vm["demo"])

    def test_detail_component_still_rejects_merged_entities(self):
        vm = self.run_source(self.overview_ctx(), {"component": "kpis", "keyMap": {"fanStage": "vent_stage"}})
        self.assertEqual(vm["mapping"]["scope"], "MULTIPLE_ENTITIES_REJECTED")
        self.assertIsNone(vm["metrics"]["fanStage"]["value"])
        self.assertEqual(vm["barns"], [])


if __name__ == "__main__":
    unittest.main()
