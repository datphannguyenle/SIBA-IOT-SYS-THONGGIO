#!/usr/bin/env python3
"""Provision VENT-012 SIM objects/dashboard with exact allowlists; no deletion."""
import argparse
import copy
import json
import os
import pathlib
import stat
import sys
import urllib.parse

from build_vent012_gateway import DASHBOARD_TITLE, PROFILE, dashboard as dashboard_payload
from vent011_alarms import alarm_rules
from vent011_deploy import SimTB, now_iso, protected_snapshot
from vent_demo_common import ROOT, write_json

MANIFEST = ROOT / 'deploy/thingsboard/vent012_manifest.json'
EVIDENCE = ROOT / 'docs/ventilation/deployment/evidence'
TOKEN_FILE = pathlib.Path(os.path.expanduser('~/.config/siba-vent012-gateway-token'))
CUSTOMER = '4199dcf0-a2bc-11f1-812e-f9c2621c1a59'
GATEWAY = 'SIM-VEN-GATEWAY-012'
ASSET_PROFILE = 'SIM-AP-VEN-SYSTEM-V012'
REL_BARN_SYSTEM = 'BarnToVentilationSystem'
REL_SYSTEM_CONTROLLER = 'VentilationSystemToController'
BARNS = {
    'ND2-1': 'e8a84a30-9c3c-11f1-a0fc-e93bd628a87f',
    'ND2-2': 'efa5b020-9c3c-11f1-a0fc-e93bd628a87f',
    'ND2-3': 'f69867b0-9c3c-11f1-a0fc-e93bd628a87f',
    'ND2-4': 'fdbeb260-9c3c-11f1-a0fc-e93bd628a87f',
}
CONTROLLERS = {'ND2-%d' % i: 'SIM-VEN-ND2-%d' % i for i in range(1, 5)}
SYSTEMS = {'ND2-%d' % i: 'SIM-VEN-SYS-ND2-%d' % i for i in range(1, 5)}


def manifest():
    if MANIFEST.is_file():
        return json.loads(MANIFEST.read_text(encoding='utf-8'))
    return {'task': 'VENT-012', 'created': {}, 'profiles': {}, 'systems': {},
            'controllers': {}, 'gateway': None, 'dashboard': None, 'mutations': []}


class TB(SimTB):
    def __init__(self, allowed=False):
        super().__init__()
        self.allowed = allowed

    def _check(self, method, path, body):
        if method == 'GET' or (method == 'POST' and path == '/api/auth/login'):
            return
        if not self.allowed:
            raise RuntimeError('mutation chưa được mở')
        if method == 'POST' and path == '/api/deviceProfile' and body.get('name') == PROFILE:
            return
        if method == 'POST' and path == '/api/assetProfile' and body.get('name') == ASSET_PROFILE:
            return
        if method == 'POST' and path.startswith('/api/device') and path.split('?')[0] == '/api/device':
            if body.get('name') in set(CONTROLLERS.values()) | {GATEWAY}: return
        if method == 'POST' and path == '/api/asset' and body.get('name') in set(SYSTEMS.values()):
            return
        if method == 'POST' and path == '/api/relation':
            if body.get('type') in (REL_BARN_SYSTEM, REL_SYSTEM_CONTROLLER): return
        if method == 'POST' and path == '/api/dashboard' and body.get('title') == DASHBOARD_TITLE:
            return
        prefixes = ('/api/customer/%s/device/' % CUSTOMER, '/api/customer/%s/asset/' % CUSTOMER)
        if method == 'POST' and path.startswith(prefixes): return
        raise RuntimeError('VENT-012 chặn %s %s' % (method, path))


def page(tb, path):
    return tb.pages(path)


def exact(tb, kind, name):
    endpoint = {'device': '/api/tenant/devices', 'asset': '/api/tenant/assets',
                'dashboard': '/api/tenant/dashboards'}[kind]
    found = [x for x in page(tb, endpoint) if x.get('name', x.get('title')) == name]
    if len(found) > 1: raise SystemExit('DỪNG: trùng tên %s' % name)
    return found[0] if found else None


def named_profile(tb, endpoint, name):
    rows = page(tb, endpoint)
    found = [x for x in rows if x['name'] == name]
    if len(found) > 1: raise SystemExit('DỪNG: trùng profile %s' % name)
    return found[0] if found else None


def plan(tb):
    collisions = {name: bool(exact(tb, 'device', name))
                  for name in [GATEWAY] + list(CONTROLLERS.values())}
    collisions.update({name: bool(exact(tb, 'asset', name)) for name in SYSTEMS.values()})
    report = {'task': 'VENT-012', 'at': now_iso(), 'barns': BARNS, 'customer': CUSTOMER,
              'collisions': collisions,
              'profiles': {PROFILE: bool(named_profile(tb, '/api/deviceProfiles', PROFILE)),
                           ASSET_PROFILE: bool(named_profile(tb, '/api/assetProfiles', ASSET_PROFILE))},
              'dashboard': bool(exact(tb, 'dashboard', DASHBOARD_TITLE)),
              'protected': protected_snapshot(tb), 'mutationsSent': []}
    write_json(EVIDENCE / 'vent012_plan.json', report)
    return report


def post(tb, path, body):
    status, result = tb.request(path, 'POST', body)
    if status != 200:
        raise SystemExit('DỪNG: POST %s -> %s %s' % (path, status, str(result)[:250]))
    return result


def device_profile(tb):
    current = named_profile(tb, '/api/deviceProfiles', PROFILE)
    if current: return tb.get_ok('/api/deviceProfile/' + current['id']['id']), False
    source = named_profile(tb, '/api/deviceProfiles', 'SIM-VentController')
    body = copy.deepcopy(tb.get_ok('/api/deviceProfile/' + source['id']['id']))
    for key in ('id', 'createdTime', 'version', 'defaultQueueName'):
        body.pop(key, None)
    body['name'] = PROFILE; body['description'] = 'SIM ONLY VENT-012; không dùng cho PLC thật.'
    rules = alarm_rules()
    for rule in rules:
        rule['alarmType'] = rule['id'] = '[SIM] ' + rule['alarmType']
        rule['propagate'] = True
        rule['propagateRelationTypes'] = [REL_SYSTEM_CONTROLLER, REL_BARN_SYSTEM,
                                          'AreaToBarn', 'FarmToArea']
        for create in rule['createRules'].values():
            create['alarmDetails'] = '[SIM VENT-012] ' + (create.get('alarmDetails') or '')
    body.setdefault('profileData', {})['alarms'] = rules
    return post(tb, '/api/deviceProfile', body), True


def asset_profile(tb):
    current = named_profile(tb, '/api/assetProfiles', ASSET_PROFILE)
    if current: return tb.get_ok('/api/assetProfile/' + current['id']['id']), False
    source = named_profile(tb, '/api/assetProfiles', 'default')
    body = copy.deepcopy(tb.get_ok('/api/assetProfile/' + source['id']['id']))
    for key in ('id', 'createdTime', 'version', 'defaultQueueName'):
        body.pop(key, None)
    body['name'] = ASSET_PROFILE; body['description'] = 'SIM ONLY VENT-012.'
    body['default'] = False
    return post(tb, '/api/assetProfile', body), True


def assign(tb, kind, entity_id):
    post(tb, '/api/customer/%s/%s/%s' % (CUSTOMER, kind, entity_id), {})


def relation(tb, from_type, from_id, rel_type, to_type, to_id):
    body = {'from': {'entityType': from_type, 'id': from_id}, 'to': {'entityType': to_type, 'id': to_id},
            'type': rel_type, 'typeGroup': 'COMMON', 'additionalInfo': {'simulation': True, 'task': 'VENT-012'}}
    return post(tb, '/api/relation', body)


def provision():
    reader = TB(); before = protected_snapshot(reader); report = plan(reader)
    state = manifest()
    expected_existing = set(state.get('created', {}))
    for name in [GATEWAY] + list(CONTROLLERS.values()):
        row = exact(reader, 'device', name)
        if row and row['id']['id'] not in expected_existing:
            raise SystemExit('DỪNG: collision không thuộc manifest: ' + name)
    for name in SYSTEMS.values():
        row = exact(reader, 'asset', name)
        if row and row['id']['id'] not in expected_existing:
            raise SystemExit('DỪNG: collision không thuộc manifest: ' + name)
    tb = TB(True); tb._token = reader.token
    def checkpoint():
        state['mutations'] = tb.mutations
        write_json(MANIFEST, state)
    dp, created = device_profile(tb); state['profiles']['device'] = dp['id']['id']; state['created'].setdefault(dp['id']['id'], created)
    checkpoint()
    ap, created = asset_profile(tb); state['profiles']['asset'] = ap['id']['id']; state['created'].setdefault(ap['id']['id'], created)
    checkpoint()
    gateway = exact(reader, 'device', GATEWAY)
    if not gateway:
        gateway = post(tb, '/api/device', {'name': GATEWAY, 'label': 'Gateway mô phỏng thông gió VENT-012',
            'type': 'Gateway', 'deviceProfileId': {'entityType': 'DEVICE_PROFILE', 'id': '0ac35540-9528-11f1-af48-7566a705eb32'},
            'additionalInfo': {'gateway': True, 'simulation': True, 'task': 'VENT-012'}})
        state['created'][gateway['id']['id']] = True
    gid = gateway['id']['id']; assign(tb, 'device', gid); state['gateway'] = gid; checkpoint()
    if not TOKEN_FILE.is_file():
        credentials = reader.get_ok('/api/device/%s/credentials' % gid)
        token = credentials.get('credentialsId')
        if not token: raise SystemExit('DỪNG: Gateway không có access token')
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as handle: handle.write(token + '\n')
    for barn, name in CONTROLLERS.items():
        system = exact(reader, 'asset', SYSTEMS[barn])
        if not system:
            system = post(tb, '/api/asset', {'name': SYSTEMS[barn], 'label': '[SIM] Hệ thống thông gió ' + barn,
                'assetProfileId': {'entityType': 'ASSET_PROFILE', 'id': ap['id']['id']},
                'additionalInfo': {'simulation': True, 'task': 'VENT-012', 'barn': barn}})
            state['created'][system['id']['id']] = True
        sid = system['id']['id']; assign(tb, 'asset', sid); state['systems'][barn] = sid; checkpoint()
        controller = exact(reader, 'device', name)
        if not controller:
            controller = post(tb, '/api/device', {'name': name, 'label': '[SIM] Bộ điều khiển thông gió ' + barn,
                'type': PROFILE, 'deviceProfileId': {'entityType': 'DEVICE_PROFILE', 'id': dp['id']['id']},
                'additionalInfo': {'simulation': True, 'task': 'VENT-012', 'barn': barn}})
            state['created'][controller['id']['id']] = True
        did = controller['id']['id']; assign(tb, 'device', did); state['controllers'][barn] = did; checkpoint()
        relation(tb, 'ASSET', BARNS[barn], REL_BARN_SYSTEM, 'ASSET', sid)
        relation(tb, 'ASSET', sid, REL_SYSTEM_CONTROLLER, 'DEVICE', did)
        checkpoint()
    if protected_snapshot(reader)['dashboards'] != before['dashboards']:
        raise SystemExit('DỪNG: protected dashboard thay đổi')
    print('Provision VENT-012 hoàn tất; token nằm ngoài repo, quyền 600.')


def deploy_dashboard():
    state = manifest(); reader = TB(); before = protected_snapshot(reader)
    current = exact(reader, 'dashboard', DASHBOARD_TITLE)
    body = dashboard_payload()
    if current:
        full = reader.get_ok('/api/dashboard/' + current['id']['id'])
        body.update(id=full['id'], createdTime=full.get('createdTime'), version=full.get('version'))
    tb = TB(True); tb._token = reader.token
    saved = post(tb, '/api/dashboard', body)
    state['dashboard'] = saved['id']['id']; state['created'][saved['id']['id']] = not bool(current)
    state['mutations'] += tb.mutations; write_json(MANIFEST, state)
    if protected_snapshot(reader)['dashboards'] != before['dashboards']:
        raise SystemExit('DỪNG: protected dashboard thay đổi')
    print('Dashboard VENT-012 version', saved.get('version'))


def verify():
    tb = TB(); state = manifest(); issues = []
    for barn, name in CONTROLLERS.items():
        row = exact(tb, 'device', name)
        if not row or row['id']['id'] != state.get('controllers', {}).get(barn): issues.append(name)
    report = {'task': 'VENT-012', 'at': now_iso(), 'manifest': state, 'issues': issues,
              'tokenFileMode600': TOKEN_FILE.is_file() and stat.S_IMODE(TOKEN_FILE.stat().st_mode) == 0o600,
              'protected': protected_snapshot(tb), 'mutationsSent': []}
    write_json(EVIDENCE / 'vent012_verify.json', report)
    if issues: raise SystemExit('DỪNG verify: ' + ', '.join(issues))
    print('VERIFY PASS: 4 controller, token ngoài repo.')


def main():
    p = argparse.ArgumentParser(); p.add_argument('action', choices=('plan', 'provision', 'dashboard', 'verify'))
    p.add_argument('--confirm-create', action='store_true'); p.add_argument('--confirm-dashboard', action='store_true')
    a = p.parse_args()
    if a.action == 'plan': print(json.dumps(plan(TB()), ensure_ascii=False, indent=2))
    elif a.action == 'provision':
        if not a.confirm_create: p.error('cần --confirm-create')
        provision()
    elif a.action == 'dashboard':
        if not a.confirm_dashboard: p.error('cần --confirm-dashboard')
        deploy_dashboard()
    else: verify()


if __name__ == '__main__': main()
