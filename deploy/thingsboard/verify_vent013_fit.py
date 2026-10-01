#!/usr/bin/env python3
"""VENT-013: xác minh CHỈ ĐỌC dashboard thông gió vừa khung (full màn hình) trên Firefox thật.

  python3 deploy/thingsboard/verify_vent013_fit.py [GATEWAY]

Đo những thứ mà bộ kiểm cũ bỏ sót vì chỉ nhìn cuộn BÊN TRONG widget:
  1. Cuộn ở cấp DASHBOARD ThingsBoard (tổ tiên của widget) - "con lăn của dashboard".
  2. Vị trí tiêu đề/nút quay lại giữa các tab: không được nhảy.
  3. Panel lấp đầy khung (không để trống) và không bị CẮT nội dung (vùng dài phải tự cuộn bên trong).
  4. Desktop 1366x768, 1536x734, 1920x1080; màn hẹp 900px; di động 390px thật (iframe).
  5. Chiều cao di động đúng SỐ HÀNG khai báo (mobileHeight là hàng, không phải px).
Không ghi gì lên ThingsBoard. Mật khẩu đọc từ TB_PASSWORD hoặc ~/.config/siba-tb-pass (không in ra).
"""
import base64
import functools
import http.server
import json
import os
import pathlib
import socket
import sys
import threading
import time

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tests'))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from webdriver_support import Browser  # noqa: E402
from vent013_fit_deploy import DASHBOARDS, NAMES  # noqa: E402
from build_vent_modular import MOBILE_HEIGHT_PX, mobile_rows, LAYOUT_ROWS  # noqa: E402

TB = os.environ.get('TB_URL', 'http://100.86.144.207:8080').rstrip('/')
TB_USER = os.environ.get('TB_USER', 'tenant@siba.com.vn')
ELEMENT_KEY = 'element-6066-11e4-a52e-4f735466cecf'
EVIDENCE = REPO / 'docs/ventilation/deployment/evidence'
DETAIL = ['vent_detail', 'vent_history', 'vent_alarms', 'vent_settings']

PROBE = """
 var roots=[].slice.call(document.querySelectorAll('.vent-modular-root'));
 var dash=[], seen={};
 roots.forEach(function(r){var e=r.parentElement;
   while(e&&e!==document.documentElement){var o=getComputedStyle(e).overflowY;
     if((o==='auto'||o==='scroll')&&e.scrollHeight>e.clientHeight+1){var k=e.tagName+'.'+String(e.className).slice(0,50);
       if(!seen[k]){seen[k]=1;dash.push(k+':'+(e.scrollHeight-e.clientHeight));}}
     e=e.parentElement;}});
 var grid=document.querySelector('gridster'), gb=grid?grid.getBoundingClientRect():null;
 var widgets=roots.map(function(r){
   var rb=r.getBoundingClientRect(), comp=r.getAttribute('data-vent-component'), first=r.firstElementChild, fb=first?first.getBoundingClientRect():null;
   var scrollers=[].slice.call(r.querySelectorAll('*')).filter(function(e){var o=getComputedStyle(e).overflowY;
     return (o==='auto'||o==='scroll')&&e.scrollHeight>e.clientHeight+1;}).map(function(e){return String(e.className).split(' ')[0]+':'+(e.scrollHeight-e.clientHeight);});
   var clipped=[].slice.call(r.querySelectorAll('.vm-card,.vm-panel,.vm-barn,.vm-metrics>div,.vm-kpis,.vm-history,.vm-alarms,.vm-overview')).filter(function(c){
     var o=getComputedStyle(c).overflowY; return o!=='auto'&&o!=='scroll'&&c.scrollHeight>c.clientHeight+1;}).map(function(c){return String(c.className).split(' ')[0]+':'+(c.scrollHeight-c.clientHeight);});
   var tiny=[].slice.call(r.querySelectorAll('*')).filter(function(x){return x.offsetParent&&x.children.length===0&&x.textContent.trim()&&parseFloat(getComputedStyle(x).fontSize)<9.5;}).length;
   return {comp:comp,top:Math.round(rb.top),bottom:Math.round(rb.bottom),h:Math.round(rb.height),w:Math.round(rb.width),
     rootScroll:r.scrollHeight-r.clientHeight, fillGap:fb?Math.round(rb.bottom-fb.bottom):null,
     scrollers:scrollers.slice(0,4), clipped:clipped.slice(0,4), tiny:tiny, notice:!!r.querySelector('.vm-notice')};});
 var title=document.querySelector('.vent-modular-root .vm-shell__brand h1'), tb=title?title.getBoundingClientRect():null;
 var back=document.querySelector('.vent-modular-root .vm-back'), bb=back?back.getBoundingClientRect():null;
 var lowest=widgets.length?Math.max.apply(null,widgets.map(function(w){return w.bottom;})):0;
 return {dashScroll:dash, pageX:document.documentElement.scrollWidth-document.documentElement.clientWidth,
   gridBottom:gb?Math.round(gb.bottom):null, lowest:lowest, titleTop:tb?Math.round(tb.top):null, backTop:bb?Math.round(bb.top):null,
   errors:document.querySelectorAll('.tb-widget-error').length, text:roots.map(function(x){return x.innerText}).join(' ').slice(0,3000), widgets:widgets};
"""


def password():
    if os.environ.get('TB_PASSWORD'):
        return os.environ['TB_PASSWORD']
    return pathlib.Path(os.path.expanduser('~/.config/siba-tb-pass')).read_text().strip()


class LocalServer:
    """Phục vụ khung iframe 390px từ chính repo này."""

    def __init__(self, root):
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
        handler.log_message = lambda *a, **k: None
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]
        self.httpd = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    @property
    def base_url(self):
        return 'http://127.0.0.1:%d' % self.httpd.server_address[1]

    def __enter__(self):
        self.thread.start(); return self

    def __exit__(self, *exc):
        self.httpd.shutdown(); self.httpd.server_close()


def find(b, css):
    return b._session('POST', '/element', {'using': 'css selector', 'value': css})[ELEMENT_KEY]


def goto(b, url, in_frame):
    if in_frame:
        b.run('location.href=arguments[0]', url)
    else:
        b._session('POST', '/url', {'url': url})


def login(b, in_frame=False):
    goto(b, TB + '/login', in_frame)
    b.wait_for("return !!document.querySelector('input[type=password]')", timeout=90)
    b._session('POST', '/element/%s/value' % find(b, 'input[formcontrolname=username], input[type=email], input[name=username]'), {'text': TB_USER})
    b._session('POST', '/element/%s/value' % find(b, 'input[type=password]'), {'text': password()})
    b._session('POST', '/element/%s/click' % find(b, 'button[type=submit]'), {})
    b.wait_for("return location.pathname.indexOf('/login') < 0", timeout=90)


def size(b, w, h):
    b.resize(w, h); b.resize(w, h + h - b.run('return innerHeight'))


def open_dashboard(b, did, in_frame=False):
    goto(b, '%s/dashboards/%s' % (TB, did), in_frame)
    b.wait_for("return document.querySelectorAll('.vent-modular-root .vm-barn').length>0", timeout=120)
    time.sleep(3)


BARN = {}   # mặc định ND2-2; nhà không có dữ liệu chi tiết chỉ hiện thông báo nên phải chọn nhà có dữ liệu
CURRENT = {'barn': 'ND2-2'}


def click_barn(b):
    b.run("var l=[].slice.call(document.querySelectorAll('.vm-barn')); var p=l.filter(function(x){return x.innerText.indexOf(arguments[0])>=0;})[0]||l[0]; p.click();", CURRENT['barn'])
    b.wait_for("return !!document.querySelector('.vm-tabs')", timeout=60); time.sleep(3)


def collect(b, did, in_frame=False):
    out = {}
    open_dashboard(b, did, in_frame)
    out['default'] = b.run(PROBE)
    click_barn(b)
    for state in DETAIL:
        if state != 'vent_detail':
            b.run("document.querySelector('[data-nav=\"'+arguments[0]+'\"]').click()", state)
            time.sleep(3)
        out[state] = b.run(PROBE)
    return out


def judge_desktop(label, data, problems):
    bad = problems.append
    tops = {st: d['titleTop'] for st, d in data.items() if st in DETAIL}
    if max(tops.values()) - min(tops.values()) > 1:
        bad('%s: tiêu đề nhảy vị trí giữa các tab: %s' % (label, tops))
    backs = {st: d['backTop'] for st, d in data.items() if st in DETAIL}
    if max(backs.values()) - min(backs.values()) > 1:
        bad('%s: nút ← Tổng quan nhảy vị trí giữa các tab: %s' % (label, backs))
    for st, d in data.items():
        if d['errors']:
            bad('%s/%s: %d widget lỗi' % (label, st, d['errors']))
        if d['dashScroll']:
            bad('%s/%s: dashboard ThingsBoard tự cuộn: %s' % (label, st, d['dashScroll']))
        if d['pageX']:
            bad('%s/%s: tràn ngang %dpx' % (label, st, d['pageX']))
        if d['gridBottom'] and d['lowest'] < d['gridBottom'] - 14:
            bad('%s/%s: nội dung dừng cách đáy %dpx' % (label, st, d['gridBottom'] - d['lowest']))
        for w in d['widgets']:
            tag = '%s/%s %s' % (label, st, w['comp'])
            if w['clipped']:
                bad('%s: nội dung bị cắt %s' % (tag, w['clipped']))
            if w['fillGap'] is not None and w['comp'] not in ('header',) and w['fillGap'] > 14:
                bad('%s: panel để trống %dpx dưới đáy' % (tag, w['fillGap']))
            if w['comp'] != 'header' and w['rootScroll'] > 2:
                bad('%s: cuộn cả widget %dpx (chỉ vùng dữ liệu bên trong được cuộn)' % (tag, w['rootScroll']))
            if w['comp'] == 'header' and w['rootScroll'] > 2:
                bad('%s: header bị cắt/cuộn %dpx' % (tag, w['rootScroll']))
            # Lịch sử có thể rỗng thật (thiết bị mô phỏng chưa có mẫu trong cửa sổ thời gian): chỉ ghi chú, không phải lỗi bố cục.
            if w['notice'] and st in DETAIL and w['comp'] in ('kpis', 'synoptic', 'controller', 'metrics'):
                bad('%s: chỉ hiện thông báo, không có nội dung thật (đang kiểm sai nhà?)' % tag)
            if w['tiny']:
                bad('%s: %d phần tử chữ < 9,5px' % (tag, w['tiny']))


def judge_narrow(label, data, problems, mobile=False):
    bad = problems.append
    allowed = sorted({mobile_rows(px) * 30 - 6 for px in MOBILE_HEIGHT_PX.values()})
    for st, d in data.items():
        if d['errors']:
            bad('%s/%s: %d widget lỗi' % (label, st, d['errors']))
        if d['pageX']:
            bad('%s/%s: tràn ngang %dpx' % (label, st, d['pageX']))
        for w in d['widgets']:
            tag = '%s/%s %s' % (label, st, w['comp'])
            if mobile and not any(abs(w['h'] - a) <= 14 for a in allowed):
                bad('%s: cao %dpx, không khớp mobileHeight (hàng) %s' % (tag, w['h'], allowed))
            if w['clipped']:
                bad('%s: nội dung bị cắt %s' % (tag, w['clipped']))
            if w['comp'] == 'header' and w['rootScroll'] > 2:
                bad('%s: header bị cắt %dpx' % (tag, w['rootScroll']))


def shots(b, did, key, w, states=('default', 'vent_detail', 'vent_history', 'vent_alarms', 'vent_settings')):
    open_dashboard(b, did)
    for st in states:
        if st == 'vent_detail':
            click_barn(b)
        elif st != 'default':
            b.run("document.querySelector('[data-nav=\"'+arguments[0]+'\"]').click()", st); time.sleep(3)
        png = b._session('GET', '/screenshot')
        (EVIDENCE / ('vent013-%s-%s-%d.png' % (key.lower(), st.replace('_', '-'), w))).write_bytes(base64.b64decode(png))


def main():
    keys = [k.upper() for k in sys.argv[1:]] or ['GATEWAY']
    report = {'task': 'VENT-013', 'checked_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'problems': {}, 'views': {}}
    b = Browser()
    first = True
    try:
        for key in keys:
            did = DASHBOARDS[key]; problems = report['problems'].setdefault(key, [])
            CURRENT['barn'] = BARN.get(key, 'ND2-2')
            for w, h in ((1366, 768), (1536, 734), (1920, 1080)):
                size(b, w, h)
                if first:
                    login(b); first = False
                label = '%s %dx%d' % (key, w, h)
                data = collect(b, did); report['views'][label] = data
                judge_desktop(label, data, problems)
                if w in (1366, 1920):
                    shots(b, did, key, w)
            size(b, 900, 800)
            data = collect(b, did); report['views']['%s 900x800' % key] = data
            judge_narrow('%s 900x800' % key, data, problems)
            with LocalServer(REPO) as server:
                b.resize(1280, 1000)
                b._session('POST', '/url', {'url': server.base_url + '/deploy/thingsboard/mobile_frame.html'})
                frame = find(b, '#device')
                b._session('POST', '/frame', {'id': {ELEMENT_KEY: frame}})
                login(b, in_frame=True)
                data = collect(b, did, in_frame=True); report['views']['%s mobile390' % key] = data
                judge_narrow('%s mobile390' % key, data, problems, mobile=True)
                b._session('POST', '/frame/parent', {})
    except Exception as error:  # noqa: BLE001
        report['problems'].setdefault('_runner', []).append('%s: %s' % (type(error).__name__, error))
    finally:
        try:
            b.close()
        except Exception:  # noqa: BLE001
            pass
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    out = EVIDENCE / 'vent013_fit_runtime.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    total = 0
    for key, items in report['problems'].items():
        print('%s: %d vấn đề' % (key, len(items)))
        for item in items[:40]:
            print('  -', item)
        total += len(items)
    print('bằng chứng:', out.name)
    return 1 if total else 0


if __name__ == '__main__':
    raise SystemExit(main())
