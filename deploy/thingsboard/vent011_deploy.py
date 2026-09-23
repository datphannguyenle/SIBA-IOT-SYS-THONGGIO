#!/usr/bin/env python3
"""VENT-011 — cấp thiết bị mô phỏng cho hệ thông gió và bơm telemetry.

  python3 vent011_deploy.py plan                        # chỉ đọc
  python3 vent011_deploy.py provision --confirm-create   # tạo profile + 7 thiết bị SIM
  python3 vent011_deploy.py seed --confirm-write         # nạp 3 giờ lịch sử + cài đặt
  python3 vent011_deploy.py feed --minutes 30            # bơm liên tục mỗi phút
  python3 vent011_deploy.py bind --confirm-create        # tạo dashboard DB-30-VEN-DETAIL-V1-SIM
  python3 vent011_deploy.py verify                       # chỉ đọc
  python3 vent011_deploy.py teardown --confirm-delete     # xoá đúng những gì đã tạo

RÀO CHẮN:
  - Telemetry đi qua ĐÚNG access token của thiết bị (/api/v1/{token}/telemetry) để bản tin chạy
    qua rule engine. Tuyệt đối không dùng /api/plugins/telemetry của phiên người dùng.
  - Chỉ tạo/xoá đúng profile SIM-VentController, thiết bị tiền tố SIM-VEN- và dashboard SIM.
  - Không RPC, không ghi attribute thiết bị, không sửa rule chain, không chạm dashboard khác.
  - Access token KHÔNG bao giờ được ghi vào repo; chỉ nằm ở ~/.config/siba-vent011-tokens.json.
"""
import argparse
import datetime
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

import vent011_sim as sim
from build_vent_live import SIM_DASHBOARD_TITLE, build as build_live
from vent_demo_common import (EVIDENCE_DIR, PROTECTED_BUNDLE, PROTECTED_DASHBOARDS, ROOT,
                              TB_URL, TB_USER, Blocked, config_sha, read_password, write_json)

MANIFEST = ROOT / 'deploy/thingsboard/vent011_manifest.json'
TOKEN_STORE = pathlib.Path(os.path.expanduser('~/.config/siba-vent011-tokens.json'))
HISTORY_POINTS = 180          # 3 giờ, mỗi phút một điểm
FEED_PERIOD_S = 60
SETTINGS_EVERY_TICKS = 60     # cài đặt là hằng số cấu hình; ghi lại mỗi giờ là đủ để giữ CURRENT


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec='seconds')


class SimTB:
    """Client chỉ cho phép đúng các lệnh của VENT-011."""

    def __init__(self, allow_create=False, allow_delete_ids=(), allow_update_ids=(),
                 allow_profile_update_ids=()):
        self.allow_create = allow_create
        self.allow_delete_ids = set(allow_delete_ids)
        self.allow_update_ids = set(allow_update_ids)
        self.allow_profile_update_ids = set(allow_profile_update_ids)
        self.mutations = []
        self._token = None

    def _check(self, method, path, body):
        if method == 'GET':
            return
        if method == 'POST' and path == '/api/auth/login':
            return
        if method == 'POST' and path == '/api/deviceProfile':
            if body.get('name') != sim.SIM_PROFILE:
                raise Blocked('deviceProfile không được phép: %s' % body.get('name'))
            # Sửa profile phải mở riêng, không đi kèm quyền tạo: alarm rule ảnh hưởng mọi
            # thiết bị thuộc profile nên không để lọt vào cùng một lượt cho phép.
            if 'id' in body:
                if (body['id'] or {}).get('id') not in self.allow_profile_update_ids:
                    raise Blocked('chưa mở cập nhật cho profile này')
            elif not self.allow_create:
                raise Blocked('chưa mở quyền tạo profile')
            return
        if method == 'POST' and path == '/api/device':
            name = body.get('name') or ''
            if not name.startswith(sim.SIM_PREFIX):
                raise Blocked('tên thiết bị phải bắt đầu bằng %s: %s' % (sim.SIM_PREFIX, name))
            if 'id' in body or not self.allow_create:
                raise Blocked('chỉ cho phép TẠO thiết bị mới: %s' % name)
            return
        if method == 'POST' and path == '/api/dashboard':
            if body.get('title') != SIM_DASHBOARD_TITLE or body.get('assignedCustomers'):
                raise Blocked('dashboard không được phép: %s' % body.get('title'))
            if 'id' in body and (body['id'] or {}).get('id') not in self.allow_update_ids:
                raise Blocked('chưa mở cập nhật cho dashboard này')
            if 'id' not in body and not self.allow_create:
                raise Blocked('chưa mở quyền tạo dashboard')
            return
        if method == 'DELETE':
            for prefix in ('/api/device/', '/api/deviceProfile/', '/api/dashboard/'):
                if path.startswith(prefix) and path[len(prefix):] in self.allow_delete_ids:
                    return
        raise Blocked('%s %s' % (method, path))

    def request(self, path, method='GET', body=None):
        self._check(method, path, body)
        req = urllib.request.Request(TB_URL + path, method=method,
                                     headers={'Content-Type': 'application/json'})
        if path != '/api/auth/login':
            req.add_header('X-Authorization', 'Bearer ' + self.token)
        data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
        if method != 'GET' and path != '/api/auth/login':
            self.mutations.append({'method': method, 'path': path})
        try:
            with urllib.request.urlopen(req, data, timeout=120) as resp:
                raw = resp.read().decode()
                return resp.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as err:
            return err.code, err.read().decode()[:500]

    @property
    def token(self):
        if self._token is None:
            status, body = self.request('/api/auth/login', 'POST',
                                        {'username': TB_USER, 'password': read_password()})
            if status != 200:
                raise SystemExit('Đăng nhập thất bại (%s)' % status)
            self._token = body['token']
        return self._token

    def get_ok(self, path):
        status, body = self.request(path)
        if status != 200:
            raise RuntimeError('GET %s -> %s' % (path, status))
        return body

    def pages(self, path):
        items, page = [], 0
        while True:
            sep = '&' if '?' in path else '?'
            body = self.get_ok('%s%spageSize=500&page=%d' % (path, sep, page))
            items += body['data']
            if not body.get('hasNext'):
                return items
            page += 1


def device_telemetry(access_token, batch):
    """Đường THIẾT BỊ, không phải đường phiên người dùng: bản tin đi qua rule engine."""
    if not batch:
        return 0
    req = urllib.request.Request(TB_URL + '/api/v1/' + access_token + '/telemetry', method='POST',
                                 headers={'Content-Type': 'application/json'})
    data = json.dumps(batch, ensure_ascii=False).encode()
    with urllib.request.urlopen(req, data, timeout=120) as resp:
        if resp.status != 200:
            raise RuntimeError('telemetry -> %s' % resp.status)
    return len(batch) if isinstance(batch, list) else 1


def protected_snapshot(tb):
    dashboards = {}
    for dashboard_id, expected in PROTECTED_DASHBOARDS.items():
        body = tb.get_ok('/api/dashboard/' + dashboard_id)
        dashboards[dashboard_id] = {'title': body['title'], 'version': body.get('version'),
                                    'sha16': config_sha(body['configuration'])[:16]}
        if dashboards[dashboard_id]['sha16'] != expected['sha16']:
            raise SystemExit('DỪNG: dashboard được bảo vệ đã đổi: %s' % body['title'])
    return {'dashboards': dashboards,
            'devices': len(tb.pages('/api/tenant/devices')),
            'profiles': sorted(p['name'] for p in tb.pages('/api/deviceProfiles'))}


def read_manifest():
    if MANIFEST.is_file():
        return json.loads(MANIFEST.read_text(encoding='utf-8'))
    return {'task': 'VENT-011', 'profile': None, 'devices': {}, 'dashboard': None, 'mutations': []}


def read_tokens():
    if not TOKEN_STORE.is_file():
        raise SystemExit('Chưa có access token: chạy `provision` trước (%s)' % TOKEN_STORE)
    return json.loads(TOKEN_STORE.read_text(encoding='utf-8'))


def write_tokens(tokens):
    TOKEN_STORE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_STORE.write_text(json.dumps(tokens, indent=2) + '\n', encoding='utf-8')
    TOKEN_STORE.chmod(0o600)


def device_name(scenario):
    return sim.SIM_PREFIX + scenario


# --- Hành động -----------------------------------------------------------------------------

def plan():
    tb = SimTB()
    devices = {d['name']: d for d in tb.pages('/api/tenant/devices') if d['name'].startswith(sim.SIM_PREFIX)}
    profiles = {p['name']: p['id']['id'] for p in tb.pages('/api/deviceProfiles')}
    dashboards = {d['title']: d['id']['id'] for d in tb.pages('/api/tenant/dashboards')}
    report = {
        'task': 'VENT-011', 'checked_at': now_iso(), 'tb_url': TB_URL,
        'profile': {'name': sim.SIM_PROFILE, 'exists': sim.SIM_PROFILE in profiles},
        'devices_to_create': [device_name(s) for s in sim.SCENARIOS if device_name(s) not in devices],
        'devices_existing': sorted(devices),
        'dashboard': {'title': SIM_DASHBOARD_TITLE, 'exists': SIM_DASHBOARD_TITLE in dashboards},
        'demo_dashboard_untouched': 'DB-30-VEN-DETAIL-V1-DEMO' in dashboards,
        'monitoring_keys': len(sim.variables('monitoring')),
        'setting_keys': len(sim.variables('setting')),
        'protected': protected_snapshot(tb),
    }
    write_json(EVIDENCE_DIR / 'vent011_plan.json', report)
    print(json.dumps({k: v for k, v in report.items() if k != 'protected'}, ensure_ascii=False, indent=2))
    print('Chỉ đọc, chưa ghi gì. Bằng chứng: vent011_plan.json')
    return report


def provision():
    reader = SimTB()
    before = protected_snapshot(reader)
    manifest = read_manifest()
    profiles = {p['name']: p['id']['id'] for p in reader.pages('/api/deviceProfiles')}
    writer = SimTB(allow_create=True)
    writer._token = reader.token

    profile_id = profiles.get(sim.SIM_PROFILE)
    if profile_id:
        print('Profile đã có:', sim.SIM_PROFILE, profile_id)
    else:
        status, body = writer.request('/api/deviceProfile', 'POST', {
            'name': sim.SIM_PROFILE, 'type': 'DEFAULT', 'transportType': 'DEFAULT',
            'provisionType': 'DISABLED',
            'description': 'VENT-011 · bộ điều khiển thông gió MÔ PHỎNG. Số liệu mô phỏng, không phải số NCC.',
            'profileData': {'configuration': {'type': 'DEFAULT'},
                            'transportConfiguration': {'type': 'DEFAULT'},
                            'provisionConfiguration': {'type': 'DISABLED',
                                                       'provisionDeviceSecret': None},
                            'alarms': None}})
        if status != 200:
            raise SystemExit('Tạo profile thất bại (%s): %s' % (status, body))
        profile_id = body['id']['id']
        print('Đã tạo profile:', sim.SIM_PROFILE, profile_id)
    manifest['profile'] = {'name': sim.SIM_PROFILE, 'id': profile_id,
                           'created_by_us': not bool(profiles.get(sim.SIM_PROFILE))}

    existing = {d['name']: d['id']['id'] for d in reader.pages('/api/tenant/devices')
                if d['name'].startswith(sim.SIM_PREFIX)}
    tokens = {}
    for scenario in sim.SCENARIOS:
        name = device_name(scenario)
        device_id = existing.get(name)
        if device_id:
            print('Thiết bị đã có:', name)
        else:
            status, body = writer.request('/api/device', 'POST', {
                'name': name, 'label': sim.SCENARIO_LABEL[scenario], 'type': sim.SIM_PROFILE,
                'deviceProfileId': {'entityType': 'DEVICE_PROFILE', 'id': profile_id},
                'additionalInfo': {'description': 'VENT-011 kịch bản %s — dữ liệu mô phỏng' % scenario}})
            if status != 200:
                raise SystemExit('Tạo thiết bị %s thất bại (%s): %s' % (name, status, body))
            device_id = body['id']['id']
            print('Đã tạo thiết bị:', name, device_id)
        credentials = reader.get_ok('/api/device/%s/credentials' % device_id)
        tokens[name] = credentials['credentialsId']
        manifest['devices'][name] = {'id': device_id, 'scenario': scenario,
                                     'created_by_us': name not in existing}

    write_tokens(tokens)
    print('Access token lưu riêng ở %s (quyền 600), KHÔNG vào repo.' % TOKEN_STORE)
    after = protected_snapshot(reader)
    if after['dashboards'] != before['dashboards']:
        raise SystemExit('DỪNG: dashboard được bảo vệ đã đổi')
    manifest['mutations'] += writer.mutations
    manifest['provisioned_at'] = now_iso()
    write_json(MANIFEST, manifest)
    write_json(EVIDENCE_DIR / 'vent011_provision.json',
               {'task': 'VENT-011', 'at': now_iso(),
                'devices': {k: v['id'] for k, v in manifest['devices'].items()},
                'profile': manifest['profile'], 'protected_before': before, 'protected_after': after})
    print('Xong provision. Thiết bị:', len(manifest['devices']))


def seed():
    manifest, tokens = read_manifest(), read_tokens()
    if not manifest['devices']:
        raise SystemExit('Chưa provision.')
    now_ms = int(time.time() * 1000)
    written = {}
    for name, info in sorted(manifest['devices'].items()):
        scenario = info['scenario']
        batch = sim.history(scenario, now_ms, points=HISTORY_POINTS, period_ms=60000)
        settings = sim.settings_payload(scenario)
        if settings:
            batch.append({'ts': now_ms, 'values': settings})
        written[name] = device_telemetry(tokens[name], batch)
        print('%-20s %d bản tin' % (name, written[name]))
    record = {'task': 'VENT-011', 'at': now_iso(), 'history_points': HISTORY_POINTS,
              'messages_per_device': written,
              'note': 'Telemetry đi qua access token thiết bị nên chạy qua rule engine.'}
    write_json(EVIDENCE_DIR / 'vent011_seed.json', record)
    print('Đã nạp lịch sử. Thiết bị OFFLINE cố tình không nhận gì.')


def feed(minutes):
    manifest, tokens = read_manifest(), read_tokens()
    if not manifest['devices']:
        raise SystemExit('Chưa provision.')
    ticks = max(1, int(minutes))
    for tick in range(ticks):
        now_ms = int(time.time() * 1000)
        for name, info in sorted(manifest['devices'].items()):
            scenario = info['scenario']
            item = sim.sample(scenario, now_ms, tick=0, period_ms=60000,
                              include_settings=(tick % SETTINGS_EVERY_TICKS == 0))
            if item is None:
                continue
            # Kịch bản STALE giữ nguyên mốc thời gian cũ: đó là điều đang cần kiểm.
            device_telemetry(tokens[name], [item])
        print('[%s] lượt %d/%d đã bơm' % (now_iso(), tick + 1, ticks))
        if tick + 1 < ticks:
            time.sleep(FEED_PERIOD_S)


def bind():
    reader = SimTB()
    before = protected_snapshot(reader)
    manifest = read_manifest()
    payload = build_live()
    dashboards = {d['title']: d['id']['id'] for d in reader.pages('/api/tenant/dashboards')}
    existing_id = dashboards.get(SIM_DASHBOARD_TITLE)
    writer = SimTB(allow_create=existing_id is None,
                   allow_update_ids={existing_id} if existing_id else ())
    writer._token = reader.token

    body = dict(payload)
    if existing_id:
        live = reader.get_ok('/api/dashboard/' + existing_id)
        body = dict(live)
        body['configuration'] = payload['configuration']
        body['title'] = body['name'] = SIM_DASHBOARD_TITLE
    status, result = writer.request('/api/dashboard', 'POST', body)
    if status != 200:
        raise SystemExit('Ghi dashboard thất bại (%s): %s' % (status, result))
    manifest['dashboard'] = {'id': result['id']['id'], 'title': result['title'],
                             'version': result.get('version'),
                             'created_by_us': existing_id is None}
    manifest['mutations'] += writer.mutations
    manifest['bound_at'] = now_iso()
    write_json(MANIFEST, manifest)
    after = protected_snapshot(reader)
    if after['dashboards'] != before['dashboards']:
        raise SystemExit('DỪNG: dashboard được bảo vệ đã đổi')
    print('Dashboard SIM:', result['id']['id'], 'version', result.get('version'))
    print('%s/dashboards/%s' % (TB_URL, result['id']['id']))
    verify()


def verify():
    tb = SimTB()
    manifest = read_manifest()
    report = {'task': 'VENT-011', 'at': now_iso(), 'devices': {}}
    for name, info in sorted(manifest.get('devices', {}).items()):
        device_id = info['id']
        keys = tb.get_ok('/api/plugins/telemetry/DEVICE/%s/keys/timeseries' % device_id)
        attributes = tb.get_ok('/api/plugins/telemetry/DEVICE/%s/values/attributes/SERVER_SCOPE' % device_id)
        active = {a['key']: a['value'] for a in attributes}.get('active')
        latest = {}
        if keys:
            sample_keys = ','.join(k for k in ('fanStage', 'indoorTemperatureAvg', 'operatingMode',
                                               'equipmentFaultActive') if k in keys)
            if sample_keys:
                latest = tb.get_ok('/api/plugins/telemetry/DEVICE/%s/values/timeseries?keys=%s'
                                   % (device_id, sample_keys))
        report['devices'][name] = {'scenario': info['scenario'], 'telemetry_keys': len(keys),
                                   'active': active,
                                   'sample': {k: v[0]['value'] for k, v in latest.items()}}
        print('%-20s keys=%-4d active=%-5s %s' % (name, len(keys), active,
                                                 report['devices'][name]['sample']))
    dashboard = manifest.get('dashboard')
    if dashboard:
        live = tb.get_ok('/api/dashboard/' + dashboard['id'])
        cfg = live['configuration']
        widgets = cfg['widgets']
        bad = [w['config']['settings']['component'] for w in widgets.values()
               if (([w['config'].get('alarmSource')] if w['type'] == 'alarm'
                    else w['config']['datasources']) or [None]) and
               any(s is None for s in ([w['config'].get('alarmSource')] if w['type'] == 'alarm'
                                       else w['config']['datasources']))]
        live_mode = sorted({w['config']['settings']['sourceMode'] for w in widgets.values()})
        report['dashboard'] = {'id': dashboard['id'], 'version': live.get('version'),
                              'widgets': len(widgets), 'aliases': len(cfg['entityAliases']),
                              'source_modes': live_mode, 'widgets_that_would_crash': bad}
        print('Dashboard version', live.get('version'), '| widget', len(widgets),
              '| alias', len(cfg['entityAliases']), '| sourceMode', live_mode)
        if bad:
            raise SystemExit('DỪNG: widget thiếu nguồn dữ liệu: %s' % bad)
    report['protected'] = protected_snapshot(tb)
    report['protected_bundle_expected'] = PROTECTED_BUNDLE['alias']
    write_json(EVIDENCE_DIR / 'vent011_verify.json', report)
    print('Xác minh xong (chỉ đọc). Bằng chứng: vent011_verify.json')


def teardown():
    manifest = read_manifest()
    ids = {info['id'] for info in manifest.get('devices', {}).values() if info.get('created_by_us')}
    if manifest.get('dashboard', {}) and manifest['dashboard'].get('created_by_us'):
        ids.add(manifest['dashboard']['id'])
    profile = manifest.get('profile') or {}
    reader = SimTB()
    writer = SimTB(allow_delete_ids=ids | ({profile['id']} if profile.get('created_by_us') else set()))
    writer._token = reader.token
    for name, info in sorted(manifest.get('devices', {}).items()):
        if not info.get('created_by_us'):
            continue
        status, _ = writer.request('/api/device/' + info['id'], 'DELETE')
        print('xoá thiết bị', name, status)
    if manifest.get('dashboard', {}).get('created_by_us'):
        status, _ = writer.request('/api/dashboard/' + manifest['dashboard']['id'], 'DELETE')
        print('xoá dashboard SIM', status)
    if profile.get('created_by_us'):
        status, _ = writer.request('/api/deviceProfile/' + profile['id'], 'DELETE')
        print('xoá profile', status)
    if TOKEN_STORE.is_file():
        TOKEN_STORE.unlink()
        print('đã xoá kho access token cục bộ')
    write_json(MANIFEST, dict(manifest, torn_down_at=now_iso()))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', choices=('plan', 'provision', 'seed', 'feed', 'bind',
                                           'verify', 'teardown'))
    parser.add_argument('--confirm-create', action='store_true')
    parser.add_argument('--confirm-write', action='store_true')
    parser.add_argument('--confirm-delete', action='store_true')
    parser.add_argument('--minutes', type=int, default=30)
    args = parser.parse_args()

    if args.action == 'plan':
        plan()
    elif args.action == 'provision':
        if not args.confirm_create:
            parser.error('cần --confirm-create')
        provision()
    elif args.action == 'seed':
        if not args.confirm_write:
            parser.error('cần --confirm-write')
        seed()
    elif args.action == 'feed':
        feed(args.minutes)
    elif args.action == 'bind':
        if not args.confirm_create:
            parser.error('cần --confirm-create')
        bind()
    elif args.action == 'verify':
        verify()
    else:
        if not args.confirm_delete:
            parser.error('cần --confirm-delete')
        teardown()


if __name__ == '__main__':
    main()
