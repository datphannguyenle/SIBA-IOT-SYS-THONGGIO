#!/usr/bin/env python3
"""VENT-011b — alarm rule cho profile MÔ PHỎNG SIM-VentController.

  python3 vent011_alarms.py plan                     # chỉ đọc, in diff
  python3 vent011_alarms.py apply --confirm-profile   # ghi alarm rule vào profile SIM
  python3 vent011_alarms.py verify                    # chỉ đọc, đếm alarm đang mở

KHÔNG sửa Root Rule Chain (nó xử lý message của MỌI thiết bị trong tenant). Alarm rule gắn vào
device profile, chỉ tác động tới thiết bị thuộc profile SIM-VentController.

CẢNH BÁO VỀ SỐ LIỆU: bảng mức độ nghiêm trọng dưới đây là **ĐỀ XUẤT của dự án**, contract v0.3
không quy định mức nào cho cờ nào. Phải được NCC/khách xác nhận trước khi dùng cho thiết bị thật.
"""
import argparse
import copy
import json

import vent011_sim as sim
from vent011_deploy import SimTB, now_iso, protected_snapshot, read_manifest
from vent_demo_common import EVIDENCE_DIR, write_json

# (khóa cờ trong contract, tên alarm, mức độ ĐỀ XUẤT, diễn giải)
RULES = [
    ('equipmentFaultActive', 'Lỗi thiết bị thông gió', 'CRITICAL',
     'Tín hiệu lỗi thiết bị tổng từ DI của bộ điều khiển'),
    ('externalHighTemperatureAlarm', 'Nhiệt độ cao (thermostat ngoài)', 'MAJOR',
     'Thermostat độc lập bên ngoài báo nhiệt độ cao'),
    ('temperatureHighAlarmActive', 'Nhiệt độ trong chuồng cao', 'MAJOR',
     'Nhiệt độ trung bình vượt ngưỡng cao của profile theo ngày tuổi'),
    ('temperatureLowAlarmActive', 'Nhiệt độ trong chuồng thấp', 'MINOR',
     'Nhiệt độ trung bình dưới ngưỡng thấp của profile theo ngày tuổi'),
    ('perceivedTemperatureHighAlarmActive', 'Nhiệt độ cảm nhận cao', 'MINOR',
     'Nhiệt độ cảm nhận vượt ngưỡng cao'),
    ('perceivedTemperatureLowAlarmActive', 'Nhiệt độ cảm nhận thấp', 'MINOR',
     'Nhiệt độ cảm nhận dưới ngưỡng thấp'),
]
SEVERITY_NOTE = ('Mức độ là ĐỀ XUẤT của dự án, contract v0.3 không quy định. '
                 'Cần NCC/khách xác nhận trước khi áp cho thiết bị thật.')


def flag_condition(key, expected):
    """Cờ trong contract là uint16 0/1, nên so sánh NUMERIC chứ không phải BOOLEAN."""
    return {'condition': [{'key': {'type': 'TIME_SERIES', 'key': key},
                           'valueType': 'NUMERIC', 'value': None,
                           'predicate': {'type': 'NUMERIC', 'operation': 'EQUAL',
                                         'value': {'defaultValue': expected, 'userValue': None,
                                                   'dynamicValue': None}}}],
            'spec': {'type': 'SIMPLE'}}


def alarm_rules():
    rules = []
    for key, name, severity, detail in RULES:
        rules.append({
            'id': name, 'alarmType': name,
            'createRules': {severity: {'condition': flag_condition(key, 1), 'schedule': None,
                                       'alarmDetails': '%s · khóa %s · %s' % (detail, key, SEVERITY_NOTE),
                                       'dashboardId': None}},
            'clearRule': {'condition': flag_condition(key, 0), 'schedule': None,
                          'alarmDetails': None, 'dashboardId': None},
            # Thiết bị mô phỏng chưa có quan hệ nhà/khu/trại nên không lan truyền.
            'propagate': False, 'propagateToOwner': False, 'propagateToTenant': False,
            'propagateRelationTypes': None,
        })
    return rules


def sim_profile(tb):
    manifest = read_manifest()
    profile = manifest.get('profile') or {}
    if not profile.get('id'):
        raise SystemExit('Chưa provision profile SIM.')
    body = tb.get_ok('/api/deviceProfile/' + profile['id'])
    if body['name'] != sim.SIM_PROFILE:
        raise SystemExit('Profile sai tên: %s' % body['name'])
    return body


def plan():
    tb = SimTB()
    profile = sim_profile(tb)
    current = profile.get('profileData', {}).get('alarms') or []
    wanted = alarm_rules()
    report = {'task': 'VENT-011b', 'at': now_iso(), 'profile': profile['name'],
              'severity_note': SEVERITY_NOTE,
              'current_alarm_types': [a['alarmType'] for a in current],
              'wanted': [{'alarmType': r['alarmType'], 'severity': list(r['createRules'])[0],
                          'key': RULES[i][0]} for i, r in enumerate(wanted)],
              'devices_affected': sorted(read_manifest().get('devices', {})),
              'protected': protected_snapshot(tb)}
    write_json(EVIDENCE_DIR / 'vent011_alarms_plan.json', report)
    print(json.dumps({k: v for k, v in report.items() if k != 'protected'},
                     ensure_ascii=False, indent=2))
    print('Chỉ đọc. %s' % SEVERITY_NOTE)
    return report


def apply_rules():
    reader = SimTB()
    before = protected_snapshot(reader)
    profile = sim_profile(reader)
    profile_id = profile['id']['id']
    writer = SimTB(allow_profile_update_ids={profile_id})
    writer._token = reader.token

    body = copy.deepcopy(profile)
    body.setdefault('profileData', {})['alarms'] = alarm_rules()
    status, result = writer.request('/api/deviceProfile', 'POST', body)
    if status != 200:
        raise SystemExit('Ghi alarm rule thất bại (%s): %s' % (status, result))

    # Đọc lại để chắc TB giữ đúng schema; TB nuốt field lạ mà không báo lỗi.
    saved = reader.get_ok('/api/deviceProfile/' + profile_id)
    stored = saved.get('profileData', {}).get('alarms') or []
    if [a['alarmType'] for a in stored] != [r['alarmType'] for r in alarm_rules()]:
        raise SystemExit('DỪNG: TB không giữ đúng danh sách alarm rule')
    for rule in stored:
        severity = list(rule['createRules'])[0]
        condition = rule['createRules'][severity]['condition']['condition'][0]
        if condition['predicate']['value']['defaultValue'] != 1:
            raise SystemExit('DỪNG: điều kiện tạo alarm không đúng: %s' % rule['alarmType'])
    after = protected_snapshot(reader)
    if after['dashboards'] != before['dashboards']:
        raise SystemExit('DỪNG: dashboard được bảo vệ đã đổi')
    print('Đã ghi %d alarm rule vào profile %s (version %s)'
          % (len(stored), saved['name'], saved.get('version')))
    write_json(EVIDENCE_DIR / 'vent011_alarms_apply.json',
               {'task': 'VENT-011b', 'at': now_iso(), 'profile_id': profile_id,
                'profile_version': saved.get('version'), 'severity_note': SEVERITY_NOTE,
                'stored': [{'alarmType': a['alarmType'], 'severity': list(a['createRules'])[0],
                            'propagate': a['propagate']} for a in stored],
                'mutations': writer.mutations})
    print('Alarm chỉ sinh khi có bản tin MỚI đi qua rule engine — giữ `feed` chạy.')


def verify():
    tb = SimTB()
    manifest = read_manifest()
    report = {'task': 'VENT-011b', 'at': now_iso(), 'devices': {}}
    total = 0
    for name, info in sorted(manifest.get('devices', {}).items()):
        body = tb.get_ok('/api/alarm/DEVICE/%s?pageSize=100&page=0&searchStatus=ANY'
                         % info['id'])
        alarms = [{'type': a['type'], 'severity': a['severity'], 'status': a['status']}
                  for a in body['data']]
        report['devices'][name] = alarms
        total += len(alarms)
        print('%-20s %d alarm %s' % (name, len(alarms),
                                     sorted({a['type'] for a in alarms}) or ''))
    report['total'] = total
    write_json(EVIDENCE_DIR / 'vent011_alarms_verify.json', report)
    print('Tổng alarm:', total)
    if not total:
        print('Chưa có alarm nào: alarm rule chỉ chạy khi có bản tin mới sau khi ghi rule.')


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', choices=('plan', 'apply', 'verify'))
    parser.add_argument('--confirm-profile', action='store_true')
    args = parser.parse_args()
    if args.action == 'plan':
        plan()
    elif args.action == 'apply':
        if not args.confirm_profile:
            parser.error('cần --confirm-profile')
        apply_rules()
    else:
        verify()


if __name__ == '__main__':
    main()
