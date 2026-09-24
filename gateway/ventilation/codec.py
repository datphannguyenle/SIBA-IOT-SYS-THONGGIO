"""Codec thanh ghi Modbus VENT-012 chỉ dành cho SIM.

Đây là hợp đồng truyền cho simulator cục bộ, không phải mapping PLC được xác nhận.
Mỗi block lặp timestamp nguồn và sequence để converter loại lần đọc lẫn chu kỳ.
Mỗi giá trị contract chiếm float32 big-endian và một cờ validity.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Iterable, Mapping

BLOCK_REGISTERS = 125
HEADER_REGISTERS = 8
ENTRY_REGISTERS = 3
ENTRIES_PER_BLOCK = (BLOCK_REGISTERS - HEADER_REGISTERS) // ENTRY_REGISTERS  # 39 mục
MAGIC = 0x5349  # "SI"
VERSION = 1
VALID = 0x0001
STALE = 0x0002
ALARM_SUPPRESSED = 0x0004
INVALID_ENUM = 0x0008


def _contract_keys() -> tuple[str, ...]:
    # Chỉ import generator VENT-011 thuần có sẵn, không phụ thuộc gateway/runtime.
    import pathlib
    import sys
    here = pathlib.Path(__file__).resolve()
    root = next((parent for parent in here.parents
                 if (parent / "deploy" / "thingsboard").exists()), pathlib.Path("/app"))
    deploy = root / "deploy" / "thingsboard"
    if str(deploy) not in sys.path:
        sys.path.insert(0, str(deploy))
    import vent011_sim
    monitoring = vent011_sim.variables("monitoring")
    settings = vent011_sim.variables("setting")
    if len(monitoring) != 41 or len(settings) != 224:
        raise RuntimeError("VENT-011 contract must contain exactly 41 monitoring + 224 setting keys")
    return tuple(monitoring + settings)


CONTRACT_KEYS = _contract_keys()
MONITORING_KEYS = CONTRACT_KEYS[:41]
SETTING_KEYS = CONTRACT_KEYS[41:]
BLOCK_COUNT = (len(CONTRACT_KEYS) + ENTRIES_PER_BLOCK - 1) // ENTRIES_PER_BLOCK


@dataclass(frozen=True)
class DecodedSnapshot:
    sequence: int
    source_timestamp_ms: int
    values: dict[str, float | None]
    flags: dict[str, int]


def encode_float(value: float) -> tuple[int, int]:
    return struct.unpack(">HH", struct.pack(">f", float(value)))


def decode_float(high: int, low: int) -> float:
    return struct.unpack(">f", struct.pack(">HH", high, low))[0]


def build_blocks(values: Mapping[str, float], *, sequence: int, source_timestamp_ms: int,
                 flags: Mapping[str, int] | None = None) -> list[list[int]]:
    """Tạo các block cố định 125 thanh ghi, mỗi block tự kiểm tính nhất quán."""
    if sequence < 0 or source_timestamp_ms < 0:
        raise ValueError("sequence and source timestamp must be unsigned")
    flags = flags or {}
    header = [MAGIC, VERSION, (sequence >> 16) & 0xffff, sequence & 0xffff,
              (source_timestamp_ms >> 48) & 0xffff, (source_timestamp_ms >> 32) & 0xffff,
              (source_timestamp_ms >> 16) & 0xffff, source_timestamp_ms & 0xffff]
    blocks: list[list[int]] = []
    for block_index in range(BLOCK_COUNT):
        registers = list(header)
        keys = CONTRACT_KEYS[block_index * ENTRIES_PER_BLOCK:(block_index + 1) * ENTRIES_PER_BLOCK]
        for key in keys:
            if key in values and values[key] is not None:
                registers.extend((*encode_float(values[key]), int(flags.get(key, VALID)) | VALID))
            else:
                # Cố ý khác IEEE zero: validity vắng mặt.
                registers.extend((0, 0, int(flags.get(key, 0)) & ~VALID))
        registers.extend([0] * (BLOCK_REGISTERS - len(registers)))
        blocks.append(registers)
    return blocks


def decode_blocks(blocks: Iterable[Iterable[int]]) -> DecodedSnapshot:
    """Chỉ giải mã snapshot đủ block/cùng sequence; từ chối dữ liệu xé hoặc sai dạng."""
    materialized = [list(block) for block in blocks]
    if len(materialized) != BLOCK_COUNT or any(len(block) != BLOCK_REGISTERS for block in materialized):
        raise ValueError("all fixed simulator blocks are required")
    headers = []
    for block in materialized:
        if block[0:2] != [MAGIC, VERSION]:
            raise ValueError("not a VENT-012 simulator block")
        sequence = (block[2] << 16) | block[3]
        timestamp = (block[4] << 48) | (block[5] << 32) | (block[6] << 16) | block[7]
        headers.append((sequence, timestamp))
    if len(set(headers)) != 1:
        raise ValueError("torn snapshot: block headers differ")
    values: dict[str, float | None] = {}
    result_flags: dict[str, int] = {}
    for index, key in enumerate(CONTRACT_KEYS):
        block = materialized[index // ENTRIES_PER_BLOCK]
        offset = HEADER_REGISTERS + (index % ENTRIES_PER_BLOCK) * ENTRY_REGISTERS
        flag = block[offset + 2]
        result_flags[key] = flag
        values[key] = decode_float(block[offset], block[offset + 1]) if flag & VALID else None
    sequence, timestamp = headers[0]
    return DecodedSnapshot(sequence, timestamp, values, result_flags)


def register_block(index: int) -> int:
    if not 0 <= index < BLOCK_COUNT:
        raise ValueError("invalid block index")
    return index * BLOCK_REGISTERS
