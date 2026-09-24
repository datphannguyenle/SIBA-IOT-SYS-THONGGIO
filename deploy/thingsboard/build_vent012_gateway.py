#!/usr/bin/env python3
"""Dựng dashboard VENT-012 Gateway SIM; không gọi ThingsBoard."""
import copy
import json
import sys

import vent011_sim as sim
from build_vent_live import (ALARM_FIELDS, ALARM_WINDOW_MS, ALIAS_LIST, ALIAS_SELECTED,
                             DETAIL_COMPONENTS, HISTORY_KEYS, ONLINE_ATTRIBUTE,
                             data_key, dashboard as live_dashboard)
from vent_demo_common import ROOT, write_json

OUT = ROOT / 'deploy/thingsboard/build/vent012'
DASHBOARD_TITLE = 'DB-30-VEN-DETAIL-V1-GATEWAY-SIM'
PROFILE = 'SIM-VEN-GatewayController-V012'
PREFIX = 'SIM-VEN-ND2-'
FRESHNESS_MS = 30_000


def alarm_source():
    return {'type': 'entity', 'name': 'Bộ điều khiển thông gió SIM',
            'entityAliasId': ALIAS_LIST,
            'dataKeys': [data_key(field, 'alarm') for field in ALARM_FIELDS]}


def dashboard():
    dash = copy.deepcopy(live_dashboard())
    dash['title'] = dash['name'] = DASHBOARD_TITLE
    aliases = dash['configuration']['entityAliases']
    aliases[ALIAS_LIST]['alias'] = 'Bốn nhà thông gió Gateway SIM'
    aliases[ALIAS_LIST]['filter'].update(deviceTypes=[PROFILE], deviceNameFilter=PREFIX)
    aliases[ALIAS_SELECTED]['alias'] = 'Bộ điều khiển Gateway SIM đang xem'
    for widget in dash['configuration']['widgets'].values():
        cfg, settings = widget['config'], widget['config']['settings']
        component = settings['component']
        settings.update({
            'simulation': True, 'invalidKeysTelemetryKey': 'simInvalidKeys',
            'provenance': {'kind': 'SIM', 'label': 'MÔ PHỎNG QUA GATEWAY',
                           'note': 'Không phải dữ liệu PLC thật'},
            'alarmScope': 'Bộ điều khiển mô phỏng VENT-012; alarm có nhãn [SIM]',
        })
        # Header không có datasource nhưng vẫn phải hiện provenance SIM.
        if component != 'header':
            keys = list(settings['keyMap'])
            settings['freshnessMs'] = {key: (7 * 24 * 60 * 60 * 1000
                                               if key in set(sim.variables('setting'))
                                               else FRESHNESS_MS) for key in keys}
        if component == 'overview':
            cfg['datasources'][0]['dataKeys'].append(data_key('simInvalidKeys'))
            settings['alarmTotalSource'] = alarm_source()
        elif cfg['datasources']:
            cfg['datasources'][0]['dataKeys'].append(data_key('simInvalidKeys'))
        if widget['type'] == 'alarm':
            cfg['alarmSource'] = {'type': 'entity', 'name': 'Nhà gió',
                                  'entityAliasId': ALIAS_SELECTED,
                                  'dataKeys': [data_key(field, 'alarm') for field in ALARM_FIELDS]}
            cfg['alarmFilterConfig']['searchPropagatedAlarms'] = False
            cfg['timewindow'] = {'realtime': {'timewindowMs': ALARM_WINDOW_MS}}
    return dash


def validate(dash):
    assert dash['title'] == DASHBOARD_TITLE
    widgets = dash['configuration']['widgets'].values()
    assert all(w['config']['settings']['simulation'] is True for w in widgets)
    overview = next(w for w in widgets if w['config']['settings']['component'] == 'overview')
    assert overview['config']['settings']['alarmTotalSource']['entityAliasId'] == ALIAS_LIST
    assert overview['config']['settings']['freshnessMs']['controllerOnline'] == FRESHNESS_MS
    assert all(w['config']['settings']['sourceMode'] == 'live' for w in widgets)


def build(check=False):
    payload = dashboard(); validate(payload)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    target = OUT / 'dashboard.json'
    if check:
        if not target.is_file() or target.read_text(encoding='utf-8') != text:
            raise SystemExit('build VENT-012 lệch nguồn')
    else:
        write_json(target, payload)
    return payload


if __name__ == '__main__':
    build('--check' in sys.argv)
    print('VENT-012 Gateway dashboard verified' if '--check' in sys.argv else 'VENT-012 Gateway dashboard written')
