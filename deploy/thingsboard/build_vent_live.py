#!/usr/bin/env python3
"""VENT-011 — dựng dashboard SIM gắn dữ liệu mô phỏng. Không gọi ThingsBoard.

Tái dùng nguyên layout và widget type của VENT-010; chỉ thêm phần GẮN DỮ LIỆU:
entity alias, datasource, keyMap, freshnessMs, sourceMode = live.

Dashboard demo fixture (DB-30-VEN-DETAIL-V1-DEMO) KHÔNG bị chạm tới; đây là dashboard riêng
để so sánh cạnh nhau.
"""
import copy
import json
import sys

import vent011_sim as sim
from build_vent_modular import FQNS, TB_TYPE, kind_for, dashboard as demo_dashboard
from vent_demo_common import ROOT, write_json

OUT = ROOT / 'deploy/thingsboard/build/live'
SIM_DASHBOARD_TITLE = 'DB-30-VEN-DETAIL-V1-SIM'
ALIAS_LIST = 'a1b2c3d0-0001-4000-8000-00000000ve01'   # nhiều nhà, cho màn Tổng quan
ALIAS_SELECTED = 'a1b2c3d0-0002-4000-8000-00000000ve02'  # nhà đang xem, cho widget chi tiết

# controllerOnline không phải khóa PLC: nó là attribute `active` do nền tảng tự quản.
ONLINE_ATTRIBUTE = 'active'
OVERVIEW_KEYS = ('fanStage', 'operatingMode', 'controllerOnline',
                 'equipmentFaultActive', 'externalHighTemperatureAlarm')
HISTORY_KEYS = ('indoorTemperatureAvg', 'outdoorTemperature', 'perceivedTemperature',
                'relativeHumidity', 'airSpeed', 'airFlow', 'waterConsumptionTotal')
DETAIL_COMPONENTS = ('kpis', 'synoptic', 'controller', 'metrics')
# Chu kỳ bơm 60s; 5 phút là STALE. Cài đặt ghi thưa nên nới ngưỡng, không để mặc định UNKNOWN.
FRESHNESS_MONITORING_MS = 300000
FRESHNESS_SETTING_MS = 7 * 24 * 60 * 60 * 1000


def alias_definitions():
    return {
        ALIAS_LIST: {'id': ALIAS_LIST, 'alias': 'Nhà gió mô phỏng', 'filter': {
            'type': 'deviceType', 'deviceTypes': [sim.SIM_PROFILE],
            'deviceNameFilter': sim.SIM_PREFIX, 'resolveMultiple': True}},
        ALIAS_SELECTED: {'id': ALIAS_SELECTED, 'alias': 'Nhà gió đang xem', 'filter': {
            'type': 'stateEntity', 'stateEntityParamName': None, 'resolveMultiple': False}},
    }


def data_key(name, key_type='timeseries'):
    return {'name': name, 'label': name, 'type': key_type, 'color': '#00d4e0', 'settings': {}}


def keys_for(component):
    """Khóa telemetry mỗi widget cần khai. Không khai thì widget đọc ra UNKNOWN, không phải 0."""
    if component == 'overview':
        return [key for key in OVERVIEW_KEYS if key != 'controllerOnline']
    if component == 'history':
        return list(HISTORY_KEYS)
    if component == 'settings':
        return sim.variables('setting')
    if component in DETAIL_COMPONENTS:
        return sim.variables('monitoring')
    return []


def datasource_for(component):
    keys = keys_for(component)
    if not keys:
        return []
    alias = ALIAS_LIST if component == 'overview' else ALIAS_SELECTED
    data_keys = [data_key(key) for key in keys]
    if component in DETAIL_COMPONENTS or component == 'overview':
        data_keys.append(data_key(ONLINE_ATTRIBUTE, 'attribute'))
    return [{'type': 'entity', 'name': 'Nhà gió', 'entityAliasId': alias, 'dataKeys': data_keys}]


def key_map_for(component):
    """Bộ điều khiển mô phỏng phát đúng tên khóa semantic, nên đây là ánh xạ một-một.
    PLC thật sẽ dùng tên khác: khi đó chỉ sửa keyMap ở cài đặt widget, không sửa code."""
    mapping = {key: key for key in keys_for(component)}
    if component in DETAIL_COMPONENTS or component == 'overview':
        mapping['controllerOnline'] = ONLINE_ATTRIBUTE
    return mapping


def freshness_for(component):
    settings_keys = set(sim.variables('setting'))
    values = {}
    for key in keys_for(component):
        values[key] = FRESHNESS_SETTING_MS if key in settings_keys else FRESHNESS_MONITORING_MS
    if component in DETAIL_COMPONENTS or component == 'overview':
        values['controllerOnline'] = FRESHNESS_MONITORING_MS
    return values


def dashboard():
    dash = copy.deepcopy(demo_dashboard())
    dash['title'] = dash['name'] = SIM_DASHBOARD_TITLE
    cfg = dash['configuration']
    cfg['entityAliases'] = alias_definitions()
    for widget in cfg['widgets'].values():
        component = widget['config']['settings']['component']
        widget['config']['datasources'] = datasource_for(component)
        widget['config']['settings'].update({
            'sourceMode': 'live',
            'demoUseSubscription': False,
            'keyMap': key_map_for(component),
            'freshnessMs': freshness_for(component),
            'alarmScope': 'Thiết bị mô phỏng %s (VENT-011), chưa xác minh trên PLC thật' % sim.SIM_PROFILE,
        })
        if widget['type'] == 'alarm':
            widget['config']['alarmSource'] = {'type': 'entity', 'name': 'Nhà gió',
                                               'entityAliasId': ALIAS_SELECTED, 'dataKeys': []}
    return dash


def validate(dash):
    cfg = dash['configuration']
    assert dash['title'] == SIM_DASHBOARD_TITLE
    assert set(cfg['entityAliases']) == {ALIAS_LIST, ALIAS_SELECTED}
    monitoring, settings_keys = set(sim.variables('monitoring')), set(sim.variables('setting'))
    seen = set()
    for widget in cfg['widgets'].values():
        config = widget['config']
        component = config['settings']['component']
        seen.add(component)
        assert config['settings']['sourceMode'] == 'live', component
        # Lặp lại vòng quét alias của TB: widget alarm đọc [alarmSource], còn lại đọc datasources.
        sources = [config.get('alarmSource')] if widget['type'] == 'alarm' else config['datasources']
        assert sources is not None and all(source is not None for source in sources), component
        for source in sources:
            assert source['entityAliasId'] in cfg['entityAliases'], component
        # Mọi khóa đã khai phải có keyMap và ngưỡng tươi, nếu không widget hiện UNKNOWN.
        declared = {key['name'] for source in config['datasources'] for key in source['dataKeys']}
        mapped = set(config['settings']['keyMap'].values())
        assert declared <= mapped | {ONLINE_ATTRIBUTE}, component
        for semantic, actual in config['settings']['keyMap'].items():
            assert semantic in monitoring | settings_keys | {'controllerOnline'}, (component, semantic)
            assert actual in declared, (component, semantic, actual)
            assert config['settings']['freshnessMs'].get(semantic), (component, semantic)
        if component == 'overview':
            assert len(config['datasources'][0]['dataKeys']) == len(OVERVIEW_KEYS)
        if component in DETAIL_COMPONENTS:
            assert monitoring <= declared, component
        if component == 'settings':
            assert settings_keys <= declared, component
        if component == 'header':
            assert config['datasources'] == [], 'header không cần datasource'
    assert seen == {'header', 'overview', 'kpis', 'synoptic', 'controller', 'metrics',
                    'history', 'alarms', 'settings'}, seen


def build(check=False):
    dash = dashboard()
    validate(dash)
    payload = json.dumps(dash, ensure_ascii=False, indent=2) + '\n'
    target = OUT / 'dashboard.json'
    if check:
        current = target.read_text(encoding='utf-8') if target.is_file() else ''
        if current != payload:
            raise SystemExit('build/live/dashboard.json lệch với nguồn; chạy lại build_vent_live.py')
        print('VENT-011 live build khớp nguồn')
        return dash
    write_json(target, dash)
    print('VENT-011 live build written ->', target)
    return dash


if __name__ == '__main__':
    build(check='--check' in sys.argv)
