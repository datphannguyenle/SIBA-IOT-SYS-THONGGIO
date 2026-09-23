"""VENT-011 — bộ sinh dữ liệu mô phỏng. Logic thuần, không gọi ThingsBoard."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "deploy/thingsboard"))
import vent011_sim as sim  # noqa: E402

NOW = 1_800_000_000_000


class ContractCoverageTest(unittest.TestCase):
    def test_payload_covers_contract_keys_exactly(self):
        """Không thiếu khóa nào và cũng không bịa khóa ngoài contract."""
        self.assertEqual(set(sim.monitoring_payload("NORMAL", 0)), set(sim.variables("monitoring")))
        self.assertEqual(set(sim.settings_payload("NORMAL")), set(sim.variables("setting")))

    def test_every_scenario_only_uses_contract_keys(self):
        allowed = set(sim.variables("monitoring")) | set(sim.variables("setting"))
        for scenario in sim.SCENARIOS:
            item = sim.sample(scenario, NOW, include_settings=True)
            if item is None:
                continue
            self.assertLessEqual(set(item["values"]), allowed, scenario)


class ScenarioContractTest(unittest.TestCase):
    def test_offline_sends_nothing_at_all(self):
        self.assertIsNone(sim.sample("OFFLINE", NOW))
        self.assertEqual(sim.settings_payload("OFFLINE"), {})
        self.assertEqual(sim.history("OFFLINE", NOW), [])

    def test_unknown_omits_keys_instead_of_sending_zero(self):
        """Điểm cốt tử: khóa chưa có phải VẮNG MẶT, không được gửi 0."""
        values = sim.monitoring_payload("UNKNOWN", 0)
        self.assertEqual(set(values), set(sim.UNKNOWN_KEYS))
        for key in ("fanStage", "operatingMode", "fan01Run", "equipmentFaultActive"):
            self.assertNotIn(key, values)
        self.assertEqual(sim.settings_payload("UNKNOWN"), {})

    def test_boundary_sends_real_zeros(self):
        """Số 0 thật phải được GỬI, để phân biệt với khóa chưa có."""
        values = sim.monitoring_payload("BOUNDARY", 0)
        for key in ("fanStage", "airSpeed", "waterFlow", "pigCount", "pigDeathCount", "pigAgeDay"):
            self.assertIn(key, values, key)
            self.assertEqual(values[key], 0, key)
        self.assertGreater(values["waterConsumptionTotal"], 0)

    def test_stale_timestamp_falls_outside_freshness_window(self):
        fresh = sim.sample("NORMAL", NOW)["ts"]
        stale = sim.sample("STALE", NOW)["ts"]
        self.assertEqual(fresh, NOW)
        self.assertEqual(NOW - stale, sim.STALE_AGE_MS)

    def test_fault_raises_flags_and_normal_keeps_them_clear(self):
        fault = sim.monitoring_payload("FAULT", 0)
        normal = sim.monitoring_payload("NORMAL", 0)
        self.assertEqual(fault["equipmentFaultActive"], 1)
        self.assertEqual(fault["externalHighTemperatureAlarm"], 1)
        self.assertEqual(fault["temperatureHighAlarmActive"], 1)
        self.assertEqual(normal["equipmentFaultActive"], 0)
        self.assertEqual(normal["temperatureHighAlarmActive"], 0)
        self.assertEqual(normal["temperatureLowAlarmActive"], 0)

    def test_manual_scenario_reports_manual_mode_and_vfd(self):
        values = sim.monitoring_payload("MANUAL", 0)
        self.assertEqual(values["operatingMode"], 0)
        self.assertEqual(values["fanControlMode"], 1)
        self.assertGreater(values["fan01SpeedFeedback"], 0)

    def test_every_scenario_label_is_declared(self):
        self.assertEqual(set(sim.SCENARIO_LABEL), set(sim.SCENARIOS))


class PhysicalCoherenceTest(unittest.TestCase):
    def test_average_matches_the_two_sensors(self):
        for scenario in ("NORMAL", "BOUNDARY", "FAULT", "MANUAL"):
            for tick in range(6):
                v = sim.monitoring_payload(scenario, tick)
                self.assertAlmostEqual(v["indoorTemperatureAvg"],
                                       round((v["indoorTemperature01"] + v["indoorTemperature02"]) / 2.0, 1),
                                       places=6, msg=scenario)

    def test_running_fans_follow_the_stage_and_never_go_backwards(self):
        counts = [sim.fans_for_stage(stage) for stage in range(0, sim.STAGE_COUNT + 1)]
        self.assertEqual(counts[0], 0)
        self.assertEqual(counts[-1], sim.FAN_COUNT)
        self.assertEqual(counts, sorted(counts))
        for tick in range(6):
            v = sim.monitoring_payload("NORMAL", tick)
            expected = sim.fans_for_stage(v["fanStage"])
            actual = sum(v["fan%02dRun" % fan] for fan in range(1, sim.FAN_COUNT + 1))
            self.assertEqual(actual, expected, v["fanStage"])
            for fan in range(1, sim.FAN_COUNT + 1):
                self.assertEqual(v["fan%02dRun" % fan], 1 if fan <= expected else 0)

    def test_stage_zero_stops_the_air(self):
        v = sim.monitoring_payload("BOUNDARY", 0)
        self.assertEqual(v["airSpeed"], 0.0)
        self.assertEqual(v["airFlow"], 0.0)
        self.assertEqual(sum(v["fan%02dRun" % fan] for fan in range(1, sim.FAN_COUNT + 1)), 0)

    def test_airflow_matches_rated_airflow_times_running_fans(self):
        rated = sim.settings_payload("NORMAL")["fanRatedAirflow"]
        for tick in range(6):
            v = sim.monitoring_payload("NORMAL", tick)
            running = sum(v["fan%02dRun" % fan] for fan in range(1, sim.FAN_COUNT + 1))
            self.assertAlmostEqual(v["airFlow"], rated * running, places=6)

    def test_water_total_only_increases(self):
        totals = [sim.monitoring_payload("NORMAL", tick)["waterConsumptionTotal"] for tick in range(10)]
        self.assertEqual(totals, sorted(totals))
        self.assertGreater(totals[-1], totals[0])

    def test_perceived_temperature_never_exceeds_indoor_average(self):
        for scenario in ("NORMAL", "BOUNDARY", "FAULT", "MANUAL"):
            for tick in range(6):
                v = sim.monitoring_payload(scenario, tick)
                self.assertLessEqual(v["perceivedTemperature"], v["indoorTemperatureAvg"], scenario)


class SettingsCoherenceTest(unittest.TestCase):
    def setUp(self):
        self.cfg = sim.settings_payload("NORMAL")

    def test_temperature_profile_ladder_is_ordered(self):
        for prefix in ("temperatureProfile", "perceivedProfile"):
            ages, setpoints = [], []
            for slot in range(1, sim.SLOT_COUNT + 1):
                tag = "%s%02d" % (prefix, slot)
                ages.append(self.cfg[tag + "AgeDay"])
                setpoints.append(self.cfg[tag + "Setpoint"])
                self.assertLess(self.cfg[tag + "LowAlarm"], self.cfg[tag + "Setpoint"], tag)
                self.assertGreater(self.cfg[tag + "HighAlarm"], self.cfg[tag + "Setpoint"], tag)
            self.assertEqual(ages, sorted(set(ages)), prefix)
            self.assertEqual(setpoints, sorted(setpoints, reverse=True), prefix)

    def test_stage_offsets_and_fan_selection_grow_with_stage(self):
        offsets, enabled = [], []
        for stage in range(1, sim.STAGE_COUNT + 1):
            tag = "%02d" % stage
            offsets.append(self.cfg["stage%sTemperatureOffset" % tag])
            enabled.append(sum(self.cfg["stage%sFan%02dEnabled" % (tag, fan)]
                               for fan in range(1, sim.FAN_COUNT + 1)))
        self.assertEqual(offsets, sorted(offsets))
        self.assertEqual(enabled, sorted(enabled))

    def test_inlet_setpoints_stay_within_percent_range(self):
        for stage in range(1, sim.STAGE_COUNT + 1):
            for key in ("stage%02dRoofInletPositionSetpoint", "stage%02dSideInletPositionSetpoint"):
                value = self.cfg[key % stage]
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 100.0)

    def test_setpoint_follows_the_age_day_slot(self):
        early = sim.setpoints_for_age(self.cfg, 0)
        late = sim.setpoints_for_age(self.cfg, 63)
        self.assertGreater(early[0], late[0])
        # Dưới slot đầu tiên vẫn dùng slot 01 thay vì trả về None.
        self.assertEqual(sim.setpoints_for_age(self.cfg, -5)[0], self.cfg["temperatureProfile01Setpoint"])


class HistoryTest(unittest.TestCase):
    def test_history_is_ordered_oldest_first_and_covers_the_window(self):
        batch = sim.history("NORMAL", NOW, points=20, period_ms=60000)
        self.assertEqual(len(batch), 20)
        stamps = [item["ts"] for item in batch]
        self.assertEqual(stamps, sorted(stamps))
        self.assertEqual(stamps[-1], NOW)
        self.assertEqual(NOW - stamps[0], 19 * 60000)

    def test_history_of_unknown_scenario_stays_sparse(self):
        batch = sim.history("UNKNOWN", NOW, points=5)
        self.assertEqual(len(batch), 5)
        for item in batch:
            self.assertEqual(set(item["values"]), set(sim.UNKNOWN_KEYS))


if __name__ == "__main__":
    unittest.main()
