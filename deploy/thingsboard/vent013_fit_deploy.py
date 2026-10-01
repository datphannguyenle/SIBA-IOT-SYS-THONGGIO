#!/usr/bin/env python3
"""VENT-013: đưa giao diện thông gió full màn hình lên 3 dashboard đang chạy.

Chỉ làm hai việc, đều có sao lưu trước và đọc lại sau:
  1. cập nhật descriptor của đúng 5 widget type `siba_vent_demo.modular_*` (CSS/JS vừa khung);
  2. thay phần BỐ CỤC (vị trí, kích thước, mobileHeight theo hàng, autoFillHeight) của đúng 3 dashboard
     DEMO / SIM / GATEWAY-SIM. Nguồn dữ liệu, alias, key map, cảnh báo, cài đặt giữ nguyên.
Không tạo/xóa thực thể, không ghi telemetry/thuộc tính, không RPC. Đọc TB_URL/TB_USER/TB_PASSWORD từ môi trường.

  --widgets      cập nhật 5 widget type
  --dashboards   DEMO,SIM,GATEWAY (mặc định cả ba)
  --dry-run      chỉ so sánh, không ghi
"""
import argparse
import copy
import json
import os
import pathlib
import sys
import time

sys.path.insert(0, os.path.expanduser('~/thingsboard-kit/lib'))
from tbclient import TB  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILD = ROOT / 'deploy/thingsboard/build/modular'
BACKUP = pathlib.Path(os.path.expanduser('~/siba-data/vent013-backup'))
KINDS = ('static', 'latest', 'timeseries', 'alarm', 'overview')
DASHBOARDS = {
    'DEMO': 'b9ff4d70-b26a-11f1-83ad-9912edc644d2',
    'SIM': '32b1ecb0-b71a-11f1-a719-7da6129c6745',
    'GATEWAY': '0e30c5f0-b7bf-11f1-a719-7da6129c6745',
}
NAMES = {'DEMO': 'DB-30-VEN-DETAIL-V1-DEMO', 'SIM': 'DB-30-VEN-DETAIL-V1-SIM',
         'GATEWAY': 'DB-30-VEN-DETAIL-V1-GATEWAY-SIM'}


def target_layout():
    """Bố cục chuẩn lấy từ bản dựng của repo (nguồn chân lý: build_vent_modular.LAYOUTS)."""
    dash = json.loads((BUILD / 'dashboard.json').read_text(encoding='utf-8'))
    cfg = dash['configuration']
    by_state = {}
    for state, st in cfg['states'].items():
        layout = st['layouts']['main']
        entries = {}
        for wid, pos in layout['widgets'].items():
            component = cfg['widgets'][wid]['config']['settings']['component']
            entries[component] = dict(pos)
        by_state[state] = {'grid': dict(layout['gridSettings']), 'entries': entries}
    return by_state


def apply_layout(live, target):
    """Nhận `configuration` của dashboard live; trả về bản sao có bố cục mới, mọi thứ khác giữ nguyên."""
    new = copy.deepcopy(live)
    cfg = new
    widgets = cfg['widgets']
    for state, spec in target.items():
        layout = cfg['states'][state]['layouts']['main']
        grid = layout['gridSettings']
        for key in ('autoFillHeight', 'mobileAutoFillHeight', 'mobileRowHeight', 'rowHeight', 'columns', 'margin'):
            grid[key] = spec['grid'][key]
        for wid in list(layout['widgets']):
            component = widgets[wid]['config']['settings']['component']
            pos = spec['entries'].get(component)
            if pos is None:
                raise SystemExit('DỪNG: %s/%s không có trong bố cục chuẩn' % (state, component))
            layout['widgets'][wid] = dict(pos)
            for key in ('col', 'row', 'sizeX', 'sizeY'):
                widgets[wid][key] = pos[key]
            widgets[wid]['config'].pop('mobileHeight', None)
        missing = set(spec['entries']) - {widgets[w]['config']['settings']['component'] for w in layout['widgets']}
        if missing:
            raise SystemExit('DỪNG: %s thiếu widget %s' % (state, sorted(missing)))
    return new


def strip_layout(config):
    """Bản sao đã bỏ phần bố cục, để chứng minh không đổi gì khác."""
    c = copy.deepcopy(config)
    for st in c['states'].values():
        layout = st['layouts']['main']
        layout['widgets'] = sorted(layout['widgets'])
        for key in ('autoFillHeight', 'mobileAutoFillHeight', 'mobileRowHeight', 'rowHeight', 'columns', 'margin'):
            layout['gridSettings'].pop(key, None)
    for w in c['widgets'].values():
        for key in ('col', 'row', 'sizeX', 'sizeY'):
            w.pop(key, None)
        w['config'].pop('mobileHeight', None)
    return c


def save_backup(name, payload):
    BACKUP.mkdir(parents=True, exist_ok=True)
    path = BACKUP / ('%s-%s.json' % (name, time.strftime('%Y%m%dT%H%M%S')))
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    path.chmod(0o600)
    return path


def norm(descriptor):
    """ThingsBoard ghi lại defaultConfig với khoảng trắng JSON khác; so sánh theo giá trị, không theo chuỗi."""
    d = copy.deepcopy(descriptor)
    if isinstance(d.get('defaultConfig'), str):
        d['defaultConfig'] = json.loads(d['defaultConfig'])
    return d


def update_widgets(tb, dry):
    for kind in KINDS:
        fqn = 'tenant.siba_vent_demo.modular_' + kind
        existing = tb.call('/api/widgetType?fqn=' + fqn)
        source = json.loads((BUILD / ('widget_%s.json' % kind)).read_text(encoding='utf-8'))
        same = norm(existing['descriptor']) == norm(source['descriptor'])
        print('widget %-10s %s' % (kind, 'đã khớp' if same else 'sẽ cập nhật'))
        if same or dry:
            continue
        save_backup('widget-' + kind, existing)
        body = copy.deepcopy(existing)
        for key in ('descriptor', 'name', 'description', 'deprecated', 'scada'):
            body[key] = copy.deepcopy(source[key])
        saved = tb.call('/api/widgetType', 'POST', body)
        back = tb.call('/api/widgetType?fqn=' + fqn)
        if norm(back['descriptor']) != norm(source['descriptor']):
            raise SystemExit('DỪNG: đọc lại widget %s không khớp' % kind)
        print('  -> version', saved.get('version'))


def update_dashboards(tb, which, dry):
    target = target_layout()
    for key in which:
        did = DASHBOARDS[key]
        live = tb.call('/api/dashboard/' + did)
        if live['title'] != NAMES[key]:
            raise SystemExit('DỪNG: id %s không phải %s (%s)' % (did, NAMES[key], live['title']))
        new_cfg = apply_layout(live['configuration'], target)
        if strip_layout(new_cfg) != strip_layout(live['configuration']):
            raise SystemExit('DỪNG: %s thay đổi ngoài phần bố cục' % key)
        changed = new_cfg != live['configuration']
        print('dashboard %-8s %s (version %s)' % (key, 'sẽ cập nhật' if changed else 'đã khớp', live.get('version')))
        if not changed or dry:
            continue
        save_backup('dashboard-' + key, live)
        body = copy.deepcopy(live)
        body['configuration'] = new_cfg
        saved = tb.call('/api/dashboard', 'POST', body)
        back = tb.call('/api/dashboard/' + did)
        if back['configuration'] != new_cfg:
            raise SystemExit('DỪNG: đọc lại dashboard %s không khớp' % key)
        print('  -> version', saved.get('version'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--widgets', action='store_true')
    ap.add_argument('--dashboards', default='')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    which = [k for k in args.dashboards.split(',') if k]
    for k in which:
        if k not in DASHBOARDS:
            ap.error('dashboard không hợp lệ: ' + k)
    tb = TB()
    if args.widgets:
        update_widgets(tb, args.dry_run)
    if which:
        update_dashboards(tb, which, args.dry_run)


if __name__ == '__main__':
    main()
