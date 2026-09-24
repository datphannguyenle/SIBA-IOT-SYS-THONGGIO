"""Kiểm tra Modbus/TCP raw và codec thuần cho simulator VENT-012 cô lập."""
import pathlib
import socket
import struct
import sys
import tempfile
import threading
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gateway" / "ventilation"))
import codec  # noqa: E402
import simulator  # noqa: E402


class CodecTest(unittest.TestCase):
    def test_contract_roles_and_missing_is_not_zero(self):
        self.assertEqual(len(codec.MONITORING_KEYS), 41)
        self.assertEqual(len(codec.SETTING_KEYS), 224)
        blocks = codec.build_blocks({"fanStage": 0.0}, sequence=7, source_timestamp_ms=1234)
        item = codec.decode_blocks(blocks)
        self.assertEqual(item.values["fanStage"], 0.0)
        self.assertIsNone(item.values["indoorTemperature01"])
        self.assertFalse(item.flags["indoorTemperature01"] & codec.VALID)

    def test_torn_blocks_are_rejected(self):
        blocks = codec.build_blocks({}, sequence=7, source_timestamp_ms=1234)
        blocks[1][3] = 8
        with self.assertRaisesRegex(ValueError, "torn"):
            codec.decode_blocks(blocks)


class TcpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = simulator.ModbusServer(("127.0.0.1", 0), simulator.Simulator(cycle_seconds=9999))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close()

    def request(self, unit, pdu, partial=False):
        packet = struct.pack(">HHHB", 42, 0, len(pdu) + 1, unit) + pdu
        with socket.create_connection(self.server.server_address, timeout=2) as sock:
            if partial:
                for byte in packet:
                    sock.sendall(bytes((byte,)))
            else:
                sock.sendall(packet)
            header = self.read_exact(sock, 7)
            _, _, length, _ = struct.unpack(">HHHB", header)
            return self.read_exact(sock, length - 1)

    @staticmethod
    def read_exact(sock, length):
        result = bytearray()
        while len(result) < length:
            part = sock.recv(length - len(result))
            if not part: raise AssertionError("early EOF")
            result.extend(part)
        return bytes(result)

    def test_partial_framing_and_fc03(self):
        pdu = self.request(1, struct.pack(">BHH", 3, 0, 8), partial=True)
        self.assertEqual(pdu[:2], bytes((3, 16)))

    def test_fc03_limit_and_writes_rejected(self):
        self.assertEqual(self.request(1, struct.pack(">BHH", 3, 0, 126)), bytes((0x83, 3)))
        self.assertEqual(self.request(1, struct.pack(">BHH", 6, 0, 1)), bytes((0x86, 1)))

    def test_oversized_mbap_length_is_closed(self):
        with socket.create_connection(self.server.server_address, timeout=2) as sock:
            sock.sendall(struct.pack(">HHHB", 42, 0, 255, 1))
            self.assertEqual(sock.recv(1), b"")

    def test_offline_and_health_are_separate(self):
        original = self.server.simulator.controls
        try:
            self.server.simulator.controls = lambda: {unit: {"scenario": "OFFLINE", "allow_alarms": False}
                                                      for unit in range(1, 5)}
            self.server.simulator._last_cycle = -1
            self.assertEqual(self.request(1, struct.pack(">BHH", 3, 0, 1)), bytes((0x83, 0x0B)))
            self.assertEqual(self.request(0, struct.pack(">BHH", 3, 0, 1))[:2], bytes((3, 2)))
        finally:
            self.server.simulator.controls = original
            self.server.simulator._last_cycle = -1


class StateTest(unittest.TestCase):
    def test_default_fault_flags_are_suppressed_and_stale_keeps_source_time(self):
        clock = lambda: 2_000_000.0
        sim = simulator.Simulator(cycle_seconds=3, clock=clock)
        sim._refresh()
        fault = codec.decode_blocks(sim._blocks[4])
        self.assertEqual(fault.values["equipmentFaultActive"], 0.0)
        self.assertTrue(fault.flags["equipmentFaultActive"] & codec.ALARM_SUPPRESSED)
        self.assertEqual(fault.values["externalHighTemperatureAlarm"], 0.0)
        self.assertTrue(fault.flags["externalHighTemperatureAlarm"] & codec.ALARM_SUPPRESSED)
        sim.controls = lambda: {1: {"scenario": "STALE", "allow_alarms": False},
                                2: {"scenario": "UNKNOWN", "allow_alarms": False},
                                3: {"scenario": "INVALID_ENUM", "allow_alarms": False},
                                4: {"scenario": "NORMAL", "allow_alarms": False}}
        sim._last_cycle = -1; sim._refresh()
        stale = codec.decode_blocks(sim._blocks[1])
        self.assertLess(stale.source_timestamp_ms, int(clock() * 1000))
        self.assertTrue(stale.flags["indoorTemperature01"] & codec.STALE)
        unknown = codec.decode_blocks(sim._blocks[2])
        self.assertEqual({key for key, value in unknown.values.items() if value is not None},
                         {"indoorTemperature01", "indoorTemperature02", "indoorTemperatureAvg"})
        self.assertIsNone(unknown.values["fanStage"])
        invalid = codec.decode_blocks(sim._blocks[3])
        self.assertTrue(invalid.flags["operatingMode"] & codec.INVALID_ENUM)

    def test_alarm_authorization_requires_json_true(self):
        sim = simulator.Simulator(cycle_seconds=3, clock=lambda: 2_000_000.0)
        sim.controls = lambda: {1: {"scenario": "FAULT", "allow_alarms": "true"},
                                2: {"scenario": "NORMAL", "allow_alarms": False},
                                3: {"scenario": "NORMAL", "allow_alarms": False},
                                4: {"scenario": "NORMAL", "allow_alarms": False}}
        sim._refresh()
        fault = codec.decode_blocks(sim._blocks[1])
        self.assertEqual(fault.values["externalHighTemperatureAlarm"], 0.0)
        self.assertTrue(fault.flags["externalHighTemperatureAlarm"] & codec.ALARM_SUPPRESSED)

    def test_corrupt_persisted_water_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            state = pathlib.Path(directory) / "water.json"
            state.write_text("not-json", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "state thể tích"):
                simulator.Simulator(volume_file=state)


if __name__ == "__main__":
    unittest.main()
