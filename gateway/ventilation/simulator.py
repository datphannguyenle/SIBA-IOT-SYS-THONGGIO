"""Bộ mô phỏng Modbus/TCP stdlib chỉ đọc cho VENT-012, chỉ dùng mạng nội bộ."""
from __future__ import annotations

import argparse
import json
import socketserver
import struct
import threading
import time
from pathlib import Path
from typing import Any

from codec import (ALARM_SUPPRESSED, BLOCK_COUNT, BLOCK_REGISTERS, CONTRACT_KEYS,
                   INVALID_ENUM, STALE, VALID, build_blocks)

SCENARIOS = ("NORMAL", "BOUNDARY", "MANUAL", "FAULT", "UNKNOWN", "STALE", "OFFLINE", "INVALID_ENUM")
DEFAULT_SCENARIOS = ("NORMAL", "BOUNDARY", "MANUAL", "FAULT")
HEALTH_REGISTERS = (0x5349, 0x4D31, 1)  # SIM1, sẵn sàng
# Đồng bộ với các khóa đầu tiên của RULES trong deploy/thingsboard/vent011_alarms.py.
# Đây là một danh sách tường minh để image SIM vẫn chỉ cần các module thuần VENT-011.
ALARM_KEYS = (
    "equipmentFaultActive", "externalHighTemperatureAlarm", "temperatureHighAlarmActive",
    "temperatureLowAlarmActive", "perceivedTemperatureHighAlarmActive",
    "perceivedTemperatureLowAlarmActive",
)


def _vent011():
    import sys
    here = Path(__file__).resolve()
    root = next((parent for parent in here.parents
                 if (parent / "deploy" / "thingsboard").exists()), Path("/app"))
    deploy = root / "deploy" / "thingsboard"
    if str(deploy) not in sys.path:
        sys.path.insert(0, str(deploy))
    import vent011_sim
    return vent011_sim


class Simulator:
    def __init__(self, control_file: str | Path | None = None, volume_file: str | Path | None = None,
                 cycle_seconds: float = 3.0, clock=time.time):
        self.control_file = Path(control_file) if control_file else None
        self.volume_file = Path(volume_file) if volume_file else None
        self.cycle_seconds, self.clock = cycle_seconds, clock
        self._lock = threading.Lock()
        self._sequence = 0
        self._last_cycle = -1
        self._started_ms = int(clock() * 1000)
        self._base_water = self._load_water()
        self._water_total = dict(self._base_water)
        self._water_flow = {unit: 0.0 for unit in range(1, 5)}
        self._water_sample_ms = self._started_ms
        self._blocks: dict[int, list[list[int]]] = {}

    def _load_water(self) -> dict[int, float]:
        if not self.volume_file or not self.volume_file.exists():
            return {unit: 18450.0 for unit in range(1, 5)}
        try:
            raw = json.loads(self.volume_file.read_text(encoding="utf-8"))
            return {unit: float(raw.get(str(unit), 18450.0)) for unit in range(1, 5)}
        except (ValueError, OSError, json.JSONDecodeError) as error:
            # Không reset bộ đếm khi state hỏng: dừng rõ ràng an toàn hơn là giảm tổng nước.
            raise RuntimeError("Không đọc được state thể tích SIM: %s" % error) from error

    def _persist_water(self) -> None:
        if self.volume_file:
            self.volume_file.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.volume_file.with_name(self.volume_file.name + ".tmp")
            temporary.write_text(json.dumps({str(k): v for k, v in self._water_total.items()}), encoding="utf-8")
            temporary.replace(self.volume_file)

    def controls(self) -> dict[int, dict[str, Any]]:
        result = {unit: {"scenario": DEFAULT_SCENARIOS[unit - 1], "allow_alarms": False} for unit in range(1, 5)}
        if not self.control_file or not self.control_file.exists():
            return result
        try:
            raw = json.loads(self.control_file.read_text(encoding="utf-8"))
        except (ValueError, OSError, json.JSONDecodeError):
            return result
        units = raw.get("units", raw) if isinstance(raw, dict) else {}
        for unit in range(1, 5):
            item = units.get(str(unit), units.get(unit, {})) if isinstance(units, dict) else {}
            if isinstance(item, str):
                item = {"scenario": item}
            scenario = item.get("scenario", result[unit]["scenario"]) if isinstance(item, dict) else result[unit]["scenario"]
            result[unit] = {"scenario": scenario if scenario in SCENARIOS else "UNKNOWN",
                            "allow_alarms": item.get("allow_alarms") is True if isinstance(item, dict) else False}
        return result

    def _refresh(self) -> None:
        now_ms = int(self.clock() * 1000)
        cycle = int(now_ms / (self.cycle_seconds * 1000))
        with self._lock:
            if cycle == self._last_cycle:
                return
            self._last_cycle, self._sequence = cycle, self._sequence + 1
            sim = _vent011()
            elapsed_minutes = max(0, (now_ms - self._started_ms) // 60000)
            elapsed_since_sample = max(0.0, (now_ms - self._water_sample_ms) / 60000.0)
            for unit in range(1, 5):
                self._water_total[unit] += self._water_flow[unit] * elapsed_since_sample
            self._water_sample_ms = now_ms
            for unit, control in self.controls().items():
                scenario = control["scenario"]
                if scenario == "OFFLINE":
                    self._blocks.pop(unit, None)
                    self._water_flow[unit] = 0.0
                    continue
                source_scenario = "UNKNOWN" if scenario == "INVALID_ENUM" else scenario
                values = dict(sim.settings_payload(source_scenario))
                values.update(sim.monitoring_payload(source_scenario, int(elapsed_minutes)))
                # Tick của generator chỉ là cadence hiển thị; tuổi/nước dùng thời gian thực.
                if source_scenario != "UNKNOWN":
                    values["pigAgeDay"] = (0 if scenario == "BOUNDARY" else 36 + elapsed_minutes // 1440)
                    flow = float(values.get("waterFlow", 0.0) or 0.0)
                    values["waterConsumptionTotal"] = self._water_total[unit]
                    self._water_flow[unit] = flow
                else:
                    self._water_flow[unit] = 0.0
                flags = {key: VALID for key in values}
                if scenario == "STALE":
                    flags = {key: value | STALE for key, value in flags.items()}
                if scenario == "INVALID_ENUM":
                    values["operatingMode"] = 99.0
                    flags["operatingMode"] = VALID | INVALID_ENUM
                if control["allow_alarms"] is not True:
                    for key in ALARM_KEYS:
                        if key in values:
                            values[key] = 0.0
                            flags[key] = VALID | ALARM_SUPPRESSED
                source_ts = now_ms - sim.STALE_AGE_MS if scenario == "STALE" else now_ms
                self._blocks[unit] = build_blocks(values, sequence=self._sequence,
                                                   source_timestamp_ms=source_ts, flags=flags)
            self._persist_water()

    def read(self, unit: int, address: int, quantity: int) -> list[int] | None:
        if quantity < 1 or quantity > 125:
            raise ValueError("quantity")
        if unit == 0:
            if address + quantity > len(HEALTH_REGISTERS):
                raise IndexError("address")
            return list(HEALTH_REGISTERS[address:address + quantity])
        if unit not in range(1, 5):
            raise LookupError("unit")
        self._refresh()
        with self._lock:
            if unit not in self._blocks:
                return None  # OFFLINE: đích Modbus không phản hồi.
            flat = [reg for block in self._blocks[unit] for reg in block]
            if address < 0 or address + quantity > len(flat):
                raise IndexError("address")
            return flat[address:address + quantity]


class ModbusHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        self.request.settimeout(5.0)
        while True:
            header = self._read_exact(7)
            if header is None:
                return
            txid, protocol, length, unit = struct.unpack(">HHHB", header)
            if protocol != 0 or length < 2 or length > 254:
                return
            pdu = self._read_exact(length - 1)
            if pdu is None:
                return
            response = self._pdu(unit, pdu)
            self.request.sendall(struct.pack(">HHHB", txid, 0, len(response) + 1, unit) + response)

    def _read_exact(self, length: int) -> bytes | None:
        chunks = bytearray()
        while len(chunks) < length:
            try:
                part = self.request.recv(length - len(chunks))
            except OSError:
                return None
            if not part:
                return None
            chunks.extend(part)
        return bytes(chunks)

    def _pdu(self, unit: int, pdu: bytes) -> bytes:
        function = pdu[0] if pdu else 0
        if function != 3:
            return bytes((function | 0x80, 0x01))
        if len(pdu) != 5:
            return bytes((0x83, 0x03))
        address, quantity = struct.unpack(">HH", pdu[1:])
        try:
            registers = self.server.simulator.read(unit, address, quantity)  # type: ignore[attr-defined]
            if registers is None:
                return bytes((0x83, 0x0B))
        except ValueError:
            return bytes((0x83, 0x03))
        except (IndexError, LookupError):
            return bytes((0x83, 0x02))
        return bytes((3, len(registers) * 2)) + struct.pack(">" + "H" * len(registers), *registers)


class ModbusServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    def __init__(self, address: tuple[str, int], simulator: Simulator):
        self.simulator = simulator
        super().__init__(address, ModbusHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description="VENT-012 SIM-ONLY read-only Modbus TCP")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=1502)
    parser.add_argument("--control-file")
    parser.add_argument("--volume-file")
    args = parser.parse_args()
    with ModbusServer((args.host, args.port), Simulator(args.control_file, args.volume_file)) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
