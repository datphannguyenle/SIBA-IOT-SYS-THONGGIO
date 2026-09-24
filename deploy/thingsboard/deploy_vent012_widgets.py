#!/usr/bin/env python3
"""Cập nhật đúng 5 modular widget type; không đổi dashboard DEMO hoặc bundle."""
import argparse
import copy
import json

from build_vent_modular import KINDS, OUT
from deploy_vent_demo import snapshot
from vent_demo_common import GuardedTB, EVIDENCE_DIR, write_json
from vent011_deploy import now_iso

BACKUP = EVIDENCE_DIR / 'vent012_widget_backup.json'
REPORT = EVIDENCE_DIR / 'vent012_widget_deploy.json'


def execute():
    reader = GuardedTB(); before = snapshot(reader); existing = {}
    for kind in KINDS:
        fqn = 'tenant.siba_vent_demo.modular_' + kind
        status, body = reader.get('/api/widgetType?fqn=' + fqn)
        if status != 200: raise SystemExit('DỪNG: thiếu widget ' + fqn)
        existing[kind] = body
    write_json(BACKUP, {'task': 'VENT-012', 'savedAt': now_iso(), 'widgets': existing})
    writer = GuardedTB(allow_update_ids={row['id']['id'] for row in existing.values()})
    writer._token = reader.token; saved = {}
    for kind in KINDS:
        source = json.loads((OUT / ('widget_%s.json' % kind)).read_text(encoding='utf-8'))
        body = copy.deepcopy(existing[kind])
        for key in ('descriptor', 'name', 'description', 'deprecated', 'scada'):
            body[key] = copy.deepcopy(source[key])
        status, result = writer.request('/api/widgetType', 'POST', body)
        if status != 200: raise SystemExit('DỪNG update widget %s (%s)' % (kind, status))
        saved[kind] = {'id': result['id']['id'], 'version': result.get('version')}
    after = snapshot(reader)
    if after['dashboards'] != before['dashboards'] or after['bundle'] != before['bundle']:
        raise SystemExit('DỪNG: protected dashboard/bundle thay đổi')
    write_json(REPORT, {'task': 'VENT-012', 'at': now_iso(), 'widgets': saved,
                        'mutations': writer.mutations, 'protectedUnchanged': True})
    print('Đã cập nhật 5 widget type; dashboard DEMO và bundle không đổi.')


def main():
    p=argparse.ArgumentParser(); p.add_argument('action', choices=('execute',)); p.add_argument('--confirm-deploy', action='store_true')
    a=p.parse_args()
    if not a.confirm_deploy: p.error('cần --confirm-deploy')
    execute()


if __name__ == '__main__': main()
