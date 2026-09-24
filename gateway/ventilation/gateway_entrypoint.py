"""Sinh config runtime từ secret mount, không ghi credential vào repo/image/log."""
import json
import os
import shutil
from pathlib import Path
from codec import BLOCK_COUNT, BLOCK_REGISTERS, register_block


def connector_config():
    slaves = []
    for unit in range(1, 5):
        slaves.append({
            'host': 'ventilation-plc-sim', 'port': 1502, 'type': 'tcp', 'method': 'socket',
            'unitId': unit, 'deviceName': 'SIM-VEN-ND2-%d' % unit,
            'deviceType': 'SIM-VEN-GatewayController-V012', 'pollPeriod': 3000,
            'byteOrder': 'BIG', 'wordOrder': 'BIG',
            'uplink_converter': 'VentilationSimUplinkConverter',
            'timeseries': [{'tag': 'sim_block_%d' % i, 'type': 'bytes', 'functionCode': 3,
                            'objectsCount': BLOCK_REGISTERS, 'address': register_block(i)}
                           for i in range(BLOCK_COUNT)],
            'attributes': [], 'attributeUpdates': [], 'rpc': [],
            'reportStrategy': {'type': 'ON_RECEIVED'},
        })
    return {'name': 'VENT-012 chỉ đọc', 'logLevel': 'INFO',
            'enableRemoteLogging': False, 'master': {'slaves': slaves}}


def main():
    os.umask(0o077)
    config = Path('/thingsboard_gateway/config')
    config.mkdir(parents=True, exist_ok=True)
    for item in Path('/default-config/config').glob('*'):
        if item.is_file() and not (config / item.name).exists():
            shutil.copyfile(item, config / item.name)
    token = Path('/run/secrets/gateway_token').read_text().strip()
    if not token:
        raise SystemExit('Thiếu gateway credential')
    gateway = {
        'thingsboard': {'host': os.environ.get('VENT_TB_MQTT_HOST', '100.86.144.207'), 'port': 1883,
                       'security': {'accessToken': token}, 'remoteShell': False,
                       'remoteConfiguration': False, 'qos': 1,
                       'reportStrategy': {'type': 'ON_RECEIVED'},
                       'statistics': {'enable': False},
                       'checkingDeviceActivity': {'checkDeviceInactivity': True,
                           'inactivityTimeoutSeconds': 45, 'inactivityCheckPeriodSeconds': 5}},
        'storage': {'type': 'file', 'data_folder_path': '/thingsboard_gateway/data/',
                    'max_file_count': 10, 'max_read_records_count': 100, 'max_records_per_file': 1000},
        'grpc': {'enabled': False},
        'connectors': [{'type': 'vent_modbus', 'class': 'VentilationReadOnlyConnector',
                        'name': 'VENT-012 chỉ đọc', 'configuration': 'ventilation.json'}]}
    (config / 'tb_gateway.json').write_text(json.dumps(gateway))
    (config / 'ventilation.json').write_text(json.dumps(connector_config()))
    # Console only; rotation thuộc Docker, không để log file tăng không giới hạn.
    logcfg = {'version': 1, 'disable_existing_loggers': False,
              'handlers': {'console': {'class': 'logging.StreamHandler', 'level': 'INFO'}},
              'root': {'level': 'INFO', 'handlers': ['console']}}
    (config / 'logs.json').write_text(json.dumps(logcfg))
    os.chdir('/thingsboard_gateway')
    os.execvp('python', ['python', '/thingsboard_gateway/tb_gateway.py'])


if __name__ == '__main__':
    main()
