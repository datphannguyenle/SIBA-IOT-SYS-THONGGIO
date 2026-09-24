#!/usr/bin/env python3
"""Firefox read-only verification for the VENT-012 Gateway SIM dashboard."""
import base64
import json
import pathlib
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'tests'))
from webdriver_support import Browser
from verify_vent_demo_ui import login
from vent_demo_common import EVIDENCE_DIR, TB_URL, write_json

ROOT = '.vent-modular-root'
SIZES = ((1366, 768), (1536, 734), (390, 844))


def open_dashboard(browser, dashboard_id):
    browser._session('POST', '/url', {'url': '%s/dashboards/%s' % (TB_URL, dashboard_id)})
    browser.wait_for("return document.querySelectorAll('%s .vm-barn').length===4" % ROOT, timeout=120)
    time.sleep(2)


def snapshot(browser, label):
    png = browser._session('GET', '/screenshot')
    path = EVIDENCE_DIR / ('vent012-%s.png' % label)
    path.write_bytes(base64.b64decode(png))
    return str(path.relative_to(EVIDENCE_DIR.parents[2]))


def inspect(browser):
    return browser.run("""
      var roots=[].slice.call(document.querySelectorAll('.vent-modular-root'));
      var text=roots.map(function(x){return x.innerText;}).join(' ');
      var tiny=[].slice.call(document.querySelectorAll('.vent-modular-root *')).filter(function(x){
        return x.offsetParent && parseFloat(getComputedStyle(x).fontSize)<12;}).length;
      return {barns:document.querySelectorAll('.vm-barn').length,
        overflowX:document.documentElement.scrollWidth-document.documentElement.clientWidth,
        clipped:roots.filter(function(x){return x.scrollWidth>x.clientWidth+2;}).length,
        tiny:tiny,text:text.slice(0,10000),badge:text.indexOf('MÔ PHỎNG QUA GATEWAY')>=0,
        kpis:[].map.call(document.querySelectorAll('.vm-kpis .vm-card b'),function(x){return x.innerText;}),
        writable:document.querySelectorAll('.vent-modular-root input:not([type=search]),.vent-modular-root textarea,.vent-modular-root select').length};
    """)


def main():
    manifest = json.loads((pathlib.Path(__file__).resolve().parents[2] /
                           'deploy/thingsboard/vent012_manifest.json').read_text())
    dashboard_id = manifest['dashboard']
    report = {'task': 'VENT-012', 'dashboard': dashboard_id, 'problems': [], 'viewports': {}}
    with tempfile.TemporaryDirectory(dir=pathlib.Path.home()):
        browser = Browser()
        try:
            login(browser)
            for width, height in SIZES:
                browser.resize(width, height); open_dashboard(browser, dashboard_id)
                info = inspect(browser); key = '%dx%d' % (width, height)
                report['viewports'][key] = info; snapshot(browser, 'overview-' + key)
                if info['barns'] != 4 or info['overflowX'] > 2 or info['clipped']:
                    report['problems'].append('%s overview layout %s' % (key, info))
                if not info['badge'] or info['writable'] or info['tiny']:
                    report['problems'].append('%s provenance/read-only/font' % key)
                if len(info['kpis']) != 4 or not info['kpis'][3].isdigit():
                    report['problems'].append('%s active alarm total chưa nạp: %s' %
                                              (key, info['kpis']))
            browser.resize(1536, 734); open_dashboard(browser, dashboard_id)
            # ND2-2 carries valid zero values.
            browser.run("[].find.call(document.querySelectorAll('.vm-barn'),function(x){return x.innerText.indexOf('ND2-2')>=0;}).click()")
            browser.wait_for("return !!document.querySelector('.vm-tabs')", timeout=60); time.sleep(2)
            detail = inspect(browser); report['detail'] = detail; snapshot(browser, 'detail-1536x734')
            compact = ' '.join(detail['text'].split())
            if 'Cấp hiện tại 0' not in compact:
                report['problems'].append('ND2-2 không hiện cấp 0')
            for state in ('vent_history', 'vent_alarms', 'vent_settings'):
                ok = browser.run("var x=document.querySelector('[data-nav=\"'+arguments[0]+'\"]');if(x){x.click();return true}return false", state)
                if not ok: report['problems'].append('thiếu tab '+state); continue
                time.sleep(3); data=inspect(browser); report[state]=data; snapshot(browser, state+'-1536x734')
                if data['writable'] or data['overflowX'] > 2: report['problems'].append(state+' không read-only/overflow')
                if state == 'vent_alarms' and ('Cảnh báo' not in data['text'] or
                                               '[object Object]' in data['text']):
                    report['problems'].append('alarm chưa render đúng hoặc còn object thô')
            if report.get('vent_settings', {}).get('text', '').count('--') > 20:
                report['problems'].append('cài đặt thiếu nhiều giá trị')
        finally:
            browser.close()
    write_json(EVIDENCE_DIR / 'vent012_ui_verify.json', report)
    if report['problems']:
        raise SystemExit('VENT-012 UI FAIL: ' + '; '.join(report['problems']))
    print('VENT-012 UI PASS:', ', '.join(report['viewports']))


if __name__ == '__main__': main()
