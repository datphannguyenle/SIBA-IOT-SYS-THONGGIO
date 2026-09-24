"""Chặn mọi downlink trước đường Modbus, kể cả reserved get/set của Gateway 3.8."""
from thingsboard_gateway.connectors.modbus.modbus_connector import AsyncModbusConnector


class VentilationReadOnlyConnector(AsyncModbusConnector):
    def server_side_rpc_handler(self, content):
        # Không chuyển tiếp, không ghi log payload (có thể chứa thông tin nhạy cảm).
        return None

    def on_attributes_update(self, content):
        return None

    def get_device_shared_attributes_keys(self, device_name):
        return []
