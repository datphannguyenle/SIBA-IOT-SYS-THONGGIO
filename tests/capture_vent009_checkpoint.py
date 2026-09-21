"""Bằng chứng local cho bước 1; không gọi API ThingsBoard hoặc ghi dữ liệu thiết bị."""
import base64
import json
import pathlib
import tempfile

from webdriver_support import ROOT, Browser, StaticServer

ELEMENT_KEY = 'element-6066-11e4-a52e-4f735466cecf'
OUT = ROOT / 'docs/ventilation/dashboard/evidence'


def main():
    results = []
    with StaticServer() as server, tempfile.TemporaryDirectory(dir=pathlib.Path.home()) as tmp:
        browser = Browser()
        try:
            for state, width, height in [(s,w,h) for w,h in ((1672,941),(1366,768),(820,1180),(390,844)) for s in ('default','vent_detail','vent_history','vent_alarms','vent_settings')]:
                url = server.base_url + '/dashboard/design-preview.html#' + state
                frame = None
                if width == 390:
                    browser.resize(1280, 1000)
                    browser._session('POST', '/url', {'url': server.base_url + '/deploy/thingsboard/mobile_frame.html'})
                    frame = browser._session('POST', '/element', {'using': 'css selector', 'value': '#device'})[ELEMENT_KEY]
                    browser._session('POST', '/frame', {'id': {ELEMENT_KEY: frame}})
                    browser.run('location.href=arguments[0]', url)
                else:
                    browser.resize(width, height)
                    browser.resize(width, height + height - browser.run('return innerHeight'))
                    browser.open(url)
                browser.wait_for("return !!document.querySelector('.state-tabs a.active[href=\"#%s\"]')" % state)
                if state == 'default':
                    browser.wait_for("var i=document.querySelector('.barn-illustration img');return i&&i.complete&&i.naturalWidth>0")
                result = browser.run("""return {
                  width:innerWidth,height:innerHeight,
                  overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
                  fans:document.querySelectorAll('.synoptic .fan').length,
                  settings:document.querySelectorAll('[data-setting-key]').length,
                  bodyHeight:document.documentElement.scrollHeight,
                  writableInputs:document.querySelectorAll('input:not([type=search]),textarea,select').length
                }""")
                assert (result['width'], result['height'], result['overflow']) == (width, height, 0), result
                assert result['writableInputs'] == 0, result
                if state == 'vent_detail':
                    assert result['fans'] == 6, result
                if state == 'vent_settings':
                    assert result['settings'] == 224, result
                name = 'vent009-step2-%s-%s.png' % (state,width)
                target = pathlib.Path(tmp) / name
                if frame:
                    browser._session('POST', '/frame/parent', {})
                    target.write_bytes(base64.b64decode(browser._session('GET', '/element/%s/screenshot' % frame)))
                else:
                    browser.screenshot_full(target)
                (OUT / name).write_bytes(target.read_bytes())
                results.append(dict(result, state=state, screenshot=name, scope='local-only'))
                print(json.dumps(results[-1], ensure_ascii=False))
        finally:
            browser.close()
    (OUT / 'vent009-step2-checkpoint.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
