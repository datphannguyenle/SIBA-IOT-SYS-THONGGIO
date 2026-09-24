"""Giải mã SIM ONLY; không dùng bảng thanh ghi này để commissioning PLC thật."""
import json
import math
import time
from pathlib import Path

from codec import BLOCK_COUNT, decode_blocks
from thingsboard_gateway.gateway.entities.converted_data import ConvertedData


class VentilationSimUplinkConverter:
    def __init__(self, config, logger):
        self.config, self.log = config, logger

    def convert(self, _, data):
        result = ConvertedData(self.config.device_name, self.config.device_type)
        for sample in data:
            try:
                blocks = []
                for index in range(BLOCK_COUNT):
                    responses = sample.get('telemetry', {}).get('sim_block_%d' % index, [])
                    if len(responses) != 1 or responses[0] is None or responses[0].isError():
                        raise ValueError('thiếu block')
                    blocks.append(responses[0].registers)
                decoded = decode_blocks(blocks)
                values = {k: round(v, 4) for k, v in decoded.values.items()
                          if v is not None and math.isfinite(v)}
                invalid = [k for k in decoded.values if k not in values]
                values.update(simulation=True, simSource='VENT-012-MODBUS',
                              simSequence=decoded.sequence,
                              simInvalidKeys=json.dumps(invalid),
                              simSourceTimestamp=decoded.source_timestamp_ms)
                result.add_to_telemetry({'ts': decoded.source_timestamp_ms, 'values': values})
                # Chỉ chứng minh converter có mẫu hợp lệ, không thay bằng chứng MQTT/API.
                Path('/thingsboard_gateway/logs/vent012-converter-heartbeat').touch()
            except (KeyError, ValueError, AttributeError, TypeError):
                self.log.warning('VENT-012 bỏ snapshot thiếu hoặc khác sequence; không điền giá trị giả')
        return result
