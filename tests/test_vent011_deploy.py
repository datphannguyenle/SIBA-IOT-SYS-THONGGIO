"""VENT-011 — rào chắn của script cấp thiết bị và payload dashboard SIM. Không gọi ThingsBoard."""
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "deploy/thingsboard"))
import build_vent_live as live  # noqa: E402
import vent011_deploy as deploy  # noqa: E402
import vent011_sim as sim  # noqa: E402
from vent_demo_common import Blocked  # noqa: E402


class GuardTest(unittest.TestCase):
    """Rào chắn phải chặn TRƯỚC khi gửi, không dựa vào TB từ chối."""

    def blocked(self, client, method, path, body=None):
        with self.assertRaises(Blocked, msg="%s %s đã KHÔNG bị chặn" % (method, path)):
            client._check(method, path, body)

    def test_reader_blocks_every_write(self):
        reader = deploy.SimTB()
        self.blocked(reader, "POST", "/api/device", {"name": "SIM-VEN-NORMAL"})
        self.blocked(reader, "POST", "/api/deviceProfile", {"name": sim.SIM_PROFILE})
        self.blocked(reader, "POST", "/api/dashboard", {"title": live.SIM_DASHBOARD_TITLE})
        self.blocked(reader, "DELETE", "/api/device/abc")
        reader._check("GET", "/api/tenant/devices", None)

    def test_user_session_telemetry_endpoint_is_always_blocked(self):
        """Ghi telemetry qua phiên người dùng không đi qua rule engine — phải chặn tuyệt đối."""
        for client in (deploy.SimTB(), deploy.SimTB(allow_create=True)):
            self.blocked(client, "POST", "/api/plugins/telemetry/DEVICE/abc/timeseries/ANY", {"a": 1})
            self.blocked(client, "POST", "/api/plugins/telemetry/DEVICE/abc/SERVER_SCOPE", {"a": 1})

    def test_rpc_and_attribute_writes_are_blocked(self):
        writer = deploy.SimTB(allow_create=True)
        self.blocked(writer, "POST", "/api/rpc/oneway/abc", {"method": "x"})
        self.blocked(writer, "POST", "/api/rpc/twoway/abc", {"method": "x"})
        self.blocked(writer, "POST", "/api/ruleChain", {"name": "x"})
        self.blocked(writer, "POST", "/api/alarm", {"type": "x"})
        self.blocked(writer, "POST", "/api/asset", {"name": "x"})

    def test_only_sim_prefixed_devices_can_be_created(self):
        writer = deploy.SimTB(allow_create=True)
        writer._check("POST", "/api/device", {"name": "SIM-VEN-NORMAL"})
        self.blocked(writer, "POST", "/api/device", {"name": "abc-dong-anh/ND2-4/P02/O015/FD"})
        self.blocked(writer, "POST", "/api/device", {"name": "VEN-NORMAL"})
        # Sửa thiết bị có sẵn vẫn bị chặn dù tên đúng tiền tố.
        self.blocked(writer, "POST", "/api/device", {"name": "SIM-VEN-NORMAL", "id": {"id": "x"}})

    def test_only_the_sim_profile_name_is_allowed(self):
        writer = deploy.SimTB(allow_create=True)
        writer._check("POST", "/api/deviceProfile", {"name": sim.SIM_PROFILE})
        for name in ("default", "Feeder", "Deodorizer", "SIM-Deodorizer"):
            self.blocked(writer, "POST", "/api/deviceProfile", {"name": name})

    def test_protected_dashboards_cannot_be_written(self):
        writer = deploy.SimTB(allow_create=True, allow_update_ids={"anything"})
        for title in ("SIBA · Khử mùi", "MUGE · Tổng quan trại", "DB-30-VEN-DETAIL-V1-DEMO"):
            self.blocked(writer, "POST", "/api/dashboard", {"title": title, "id": {"id": "anything"}})

    def test_delete_is_limited_to_manifest_ids(self):
        writer = deploy.SimTB(allow_delete_ids={"keep-1"})
        writer._check("DELETE", "/api/device/keep-1", None)
        self.blocked(writer, "DELETE", "/api/device/other", None)
        self.blocked(writer, "DELETE", "/api/dashboard/other", None)
        self.blocked(writer, "DELETE", "/api/tenant/devices", None)


class LiveDashboardPayloadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dash = live.dashboard()
        live.validate(cls.dash)
        cls.widgets = {w["config"]["settings"]["component"]: w
                       for w in cls.dash["configuration"]["widgets"].values()}

    def test_demo_dashboard_title_is_not_reused(self):
        self.assertEqual(self.dash["title"], "DB-30-VEN-DETAIL-V1-SIM")
        self.assertNotEqual(self.dash["title"], "DB-30-VEN-DETAIL-V1-DEMO")

    def test_every_widget_reads_live_and_never_falls_back_to_fixture(self):
        for component, widget in self.widgets.items():
            settings = widget["config"]["settings"]
            self.assertEqual(settings["sourceMode"], "live", component)
            self.assertFalse(settings["demoUseSubscription"], component)

    def test_overview_uses_the_multi_entity_alias_and_details_use_state_entity(self):
        overview = self.widgets["overview"]["config"]["datasources"][0]
        self.assertEqual(overview["entityAliasId"], live.ALIAS_LIST)
        alias = self.dash["configuration"]["entityAliases"][live.ALIAS_LIST]["filter"]
        self.assertTrue(alias["resolveMultiple"])
        self.assertEqual(alias["deviceTypes"], [sim.SIM_PROFILE])
        for component in live.DETAIL_COMPONENTS + ("history",):
            source = self.widgets[component]["config"]["datasources"][0]
            self.assertEqual(source["entityAliasId"], live.ALIAS_SELECTED, component)
        selected = self.dash["configuration"]["entityAliases"][live.ALIAS_SELECTED]["filter"]
        self.assertEqual(selected["type"], "stateEntity")
        self.assertFalse(selected["resolveMultiple"])

    def test_alarm_widget_has_alarm_source_bound_to_the_selected_barn(self):
        alarms = self.widgets["alarms"]["config"]
        self.assertEqual(alarms["alarmSource"]["entityAliasId"], live.ALIAS_SELECTED)

    def test_controller_online_is_read_from_the_platform_attribute(self):
        for component in live.DETAIL_COMPONENTS + ("overview",):
            config = self.widgets[component]["config"]
            self.assertEqual(config["settings"]["keyMap"]["controllerOnline"], live.ONLINE_ATTRIBUTE)
            attribute_keys = [key for source in config["datasources"] for key in source["dataKeys"]
                              if key["type"] == "attribute"]
            self.assertEqual([key["name"] for key in attribute_keys], [live.ONLINE_ATTRIBUTE], component)

    def test_detail_widgets_declare_every_monitoring_key(self):
        monitoring = set(sim.variables("monitoring"))
        for component in live.DETAIL_COMPONENTS:
            declared = {key["name"] for source in self.widgets[component]["config"]["datasources"]
                        for key in source["dataKeys"]}
            self.assertTrue(monitoring <= declared, component)

    def test_settings_widget_declares_every_setting_key(self):
        declared = {key["name"] for source in self.widgets["settings"]["config"]["datasources"]
                    for key in source["dataKeys"]}
        self.assertTrue(set(sim.variables("setting")) <= declared)

    def test_freshness_is_configured_for_every_mapped_key(self):
        """Khóa không có ngưỡng tươi sẽ hiện UNKNOWN — không được để sót."""
        for component, widget in self.widgets.items():
            settings = widget["config"]["settings"]
            for semantic in settings["keyMap"]:
                self.assertGreater(settings["freshnessMs"].get(semantic, 0), 0, (component, semantic))

    def test_key_map_only_uses_contract_keys(self):
        allowed = set(sim.variables("monitoring")) | set(sim.variables("setting")) | {"controllerOnline"}
        for component, widget in self.widgets.items():
            self.assertLessEqual(set(widget["config"]["settings"]["keyMap"]), allowed, component)

    def test_build_output_matches_the_source(self):
        target = live.OUT / "dashboard.json"
        self.assertTrue(target.is_file(), "chạy build_vent_live.py")
        self.assertEqual(json.loads(target.read_text(encoding="utf-8")), self.dash)


if __name__ == "__main__":
    unittest.main()
