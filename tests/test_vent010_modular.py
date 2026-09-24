"""VENT-010 generated modular widget validation; local Firefox only, never ThingsBoard."""
import json
import re
import subprocess
import sys
import unittest

try:
    from webdriver_support import ROOT, Browser, StaticServer, geckodriver_path
except ModuleNotFoundError:
    from tests.webdriver_support import ROOT, Browser, StaticServer, geckodriver_path


BUILD = ROOT / "deploy/thingsboard/build/modular"
NAMESPACE = "tb-vent010-ns"


def namespace_css(css):
    """Same deliberately small ThingsBoard CSS namespace simulation as the payload harness."""
    animation = r'@keyframes[^{}]+\{(?:[^{}]*\{[^{}]*\})+\s*\}'
    keyframes = re.findall(animation, css)
    css = re.sub(animation, '', css)
    def scope(block):
        return ''.join('.%s %s{%s}' % (NAMESPACE, selector.strip(), body)
                       for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', block)
                       for selector in selector.split(','))
    return '\n'.join(scope(block) for block in re.findall(r'([^@{}]+\{[^{}]*\})', css) + keyframes)


class ModularBuildStaticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.types = {kind: json.loads((BUILD / ('widget_%s.json' % kind)).read_text())
                     for kind in ('static', 'latest', 'timeseries', 'alarm', 'overview')}
        cls.dashboard = json.loads((BUILD / 'dashboard.json').read_text())

    def test_dashboard_survives_thingsboard_alias_validation(self):
        """Lặp lại đúng vòng quét alias của TB: widget alarm đọc [config.alarmSource],
        các widget khác đọc config.datasources. Thiếu alarmSource là vỡ cả dashboard."""
        for wid, widget in self.dashboard['configuration']['widgets'].items():
            config = widget['config']
            sources = [config.get('alarmSource')] if widget['type'] == 'alarm' else config.get('datasources')
            self.assertIsNotNone(sources, wid)
            for source in sources:
                self.assertIsNotNone(source, '%s: TB sẽ đọc entityAliasId của undefined' % wid)
                self.assertFalse(source.get('entityAliasId'), wid)

    def test_alarm_widget_type_default_config_carries_alarm_source(self):
        for kind, widget in self.types.items():
            default = json.loads(widget['descriptor']['defaultConfig'])
            self.assertEqual('alarmSource' in default, widget['descriptor']['type'] == 'alarm', kind)

    def test_overview_widget_is_the_only_multi_entity_type(self):
        for kind, widget in self.types.items():
            multi = kind == 'overview'
            self.assertIn('WIDGET_MULTI_ENTITY = %s' % ('true' if multi else 'false'),
                          widget['descriptor']['controllerScript'], kind)
        self.assertEqual(self.types['overview']['descriptor']['type'], 'latest')
        self.assertEqual(self.types['overview']['fqn'], 'siba_vent_demo.modular_overview')
        widgets = self.dashboard['configuration']['widgets']
        home = self.dashboard['configuration']['states']['default']['layouts']['main']['widgets']
        components = {widgets[wid]['config']['settings']['component']: widgets[wid] for wid in home}
        self.assertIn('overview', components)
        self.assertEqual(components['overview']['typeFullFqn'], 'tenant.siba_vent_demo.modular_overview')
        self.assertEqual(components['overview']['config']['datasources'], [])

    def test_deterministic_build_and_native_widget_distribution(self):
        subprocess.run([sys.executable, 'build_vent_modular.py', '--check'],
                       cwd=ROOT / 'deploy/thingsboard', check=True, capture_output=True)
        states = self.dashboard['configuration']['states']
        self.assertEqual(list(states), ['default', 'vent_detail', 'vent_history', 'vent_alarms', 'vent_settings'])
        widgets = self.dashboard['configuration']['widgets']
        for state, definition in states.items():
            layout = definition['layouts']['main']
            native = layout['widgets']
            self.assertGreater(len(native), 1, state)
            self.assertEqual(layout['gridSettings']['autoFillHeight'], state != 'vent_detail', state)
            self.assertFalse(layout['gridSettings']['mobileAutoFillHeight'], state)
            if state == 'vent_detail':
                # LAYOUTS là nguồn chuẩn: 5 widget chức năng độc lập cho màn giám sát.
                self.assertEqual({widgets[wid]['config']['settings']['component'] for wid in native},
                                 {'header', 'kpis', 'synoptic', 'controller', 'metrics'})
                positions = {widgets[wid]['config']['settings']['component']: native[wid]
                             for wid in native}
                self.assertEqual((positions['header']['row'], positions['header']['sizeY']), (0, 2))
                self.assertEqual((positions['kpis']['row'], positions['kpis']['sizeY']), (2, 2))
            if state == 'default':
                self.assertEqual({widgets[wid]['config']['settings']['component'] for wid in native},
                                 {'header', 'overview'})
            self.assertTrue(all(wid in widgets for wid in native))
        self.assertEqual({w['type'] for w in widgets.values()}, {'static', 'latest', 'timeseries', 'alarm'})

    def test_generated_descriptors_are_read_only_and_default_live(self):
        forbidden = ('sendOneWayRpc', 'sendTwoWayRpc', 'controlApi', 'ackAlarm', 'clearAlarm',
                     'saveEntityAttributes', 'attributeService.save', 'fetch(', 'XMLHttpRequest(', '/api/')
        for kind, payload in self.types.items():
            descriptor = payload['descriptor']
            # 'overview' là widget riêng của dự án nhưng chạy trên widget type 'latest' của ThingsBoard.
            self.assertEqual(descriptor['type'], 'latest' if kind == 'overview' else kind)
            self.assertIn('VentilationSource.createViewModel', descriptor['controllerScript'])
            self.assertEqual(json.loads(descriptor['defaultConfig'])['settings']['sourceMode'], 'live')
            self.assertFalse(any(word in descriptor['controllerScript'] for word in forbidden), kind)


HARNESS = r'''
var payload=arguments[0], css=arguments[1], opts=arguments[2]||{};
var style=document.getElementById('vent010-style') || document.head.appendChild(Object.assign(document.createElement('style'),{id:'vent010-style'}));
style.textContent=css;
var host=document.getElementById('tb-widget'); host.className='%s'; host.innerHTML=payload.descriptor.templateHtml;
window.__calls=[];
var params=opts.params||{}, ctx=opts.ctx||{};
ctx.$container=[host]; ctx.settings=Object.assign({component:opts.component,viewState:opts.state,sourceMode:'live',keyMap:{},freshnessMs:{}},opts.settings||{});
ctx.detectChanges=function(){}; ctx.stateController={getStateId:function(){return opts.state;},getStateParams:function(){return params;},
 openState:function(id,p,r){window.__calls.push(['openState',id,p,r]);},updateState:function(id,p,r){window.__calls.push(['updateState',id,p,r]);}};
var self={ctx:ctx}; new Function('self',payload.descriptor.controllerScript)(self); self.onInit(); window.__widgetSelf=self; return true;
''' % NAMESPACE


@unittest.skipUnless(geckodriver_path(), 'geckodriver chưa có')
class ModularRuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = StaticServer().__enter__()
        cls.browser = Browser()
        cls.payloads = {kind: json.loads((BUILD / ('widget_%s.json' % kind)).read_text())
                        for kind in ('static', 'latest', 'timeseries', 'alarm', 'overview')}
        cls.css = {kind: namespace_css(payload['descriptor']['templateCss']) for kind, payload in cls.payloads.items()}

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.__exit__(None, None, None)

    def mount(self, kind='latest', component='kpis', state='vent_detail', settings=None, ctx=None, params=None):
        self.browser._session('POST', '/url', {'url': self.server.base_url + '/tests/tb_widget_harness.html'})
        self.browser.run(HARNESS, self.payloads[kind], self.css[kind], {'component': component, 'state': state,
                         'settings': settings or {}, 'ctx': ctx or {}, 'params': params or {}})

    def test_all_native_descriptor_kinds_execute_in_namespace_harness(self):
        for kind, component, state in (('static', 'header', 'vent_detail'), ('latest', 'kpis', 'vent_detail'),
                                       ('timeseries', 'history', 'vent_history'), ('alarm', 'alarms', 'vent_alarms')):
            self.mount(kind, component, state)
            self.assertEqual(self.browser.run("return document.querySelectorAll('.vent-modular-root').length"), 1, kind)

    def test_alarm_subscription_sorts_by_an_entity_key_not_a_plain_string(self):
        """sortOrder.key dạng chuỗi làm máy chủ bỏ qua lệnh trong im lặng: bảng cảnh báo trống
        vĩnh viễn mà không có lỗi nào. Đã đo trực tiếp trên websocket của TB 4.3.1.2."""
        script = self.payloads['alarm']['descriptor']['controllerScript']
        self.assertIn("sortOrder: {key: {type: 'ALARM_FIELD', key: 'createdTime'}", script)
        self.assertNotIn("sortOrder: {key: 'createdTime'", script)

    def test_detail_header_names_the_barn_chosen_from_the_overview(self):
        """Ở chế độ live, widget chi tiết không có danh sách nhà; tên nhà phải lấy từ state param,
        nếu không màn Giám sát luôn hiện "Nhà chưa chọn" dù đã chọn nhà."""
        self.mount('static', 'header', 'vent_detail',
                   settings={'keyMap': {'fanStage': 'vent_stage'}},
                   ctx={'data': [{'datasource': {'entityId': {'entityType': 'DEVICE', 'id': 'dev-7'},
                                                 'entityName': 'ND6-1'},
                                  'dataKey': {'name': 'vent_stage'}, 'data': [[1, 3]]}]},
                   params={'barnId': 'dev-7', 'barnLabel': 'Nhà mô phỏng · chạy tự động'})
        heading = self.browser.run("return document.querySelector('.vent-modular-root h1').innerText")
        self.assertEqual(heading, 'Nhà mô phỏng · chạy tự động')

    def test_detail_header_admits_when_no_barn_was_chosen(self):
        self.mount('static', 'header', 'vent_detail')
        heading = self.browser.run("return document.querySelector('.vent-modular-root h1').innerText")
        self.assertEqual(heading, 'Nhà chưa chọn')

    def test_live_empty_default_never_uses_demo_fixture_or_fake_barn(self):
        self.mount('latest', 'kpis', settings={'context': {'farm': 'Trại test'}})
        text = self.browser.run("return document.querySelector('.vent-modular-root').innerText")
        self.assertIn('--', text)
        self.assertNotIn('27.8', text)
        self.assertNotIn('ND2-1', text)
        # Widget KPI không tự dựng header; provenance nằm ở header/overview/history/alarm.
        self.assertEqual(self.browser.run("return document.querySelectorAll('.vm-badge').length"), 0)

    def test_live_data_update_keeps_zero_and_turns_null_to_missing(self):
        settings = {'keyMap': {'indoorTemperatureAvg': 'temp'}, 'freshnessMs': {'indoorTemperatureAvg': 999999999999}}
        ctx = {'data': [{'dataKey': {'name': 'temp'}, 'data': [[1, 0]]}]}
        self.mount('latest', 'kpis', settings=settings, ctx=ctx)
        self.assertEqual(self.browser.run("return document.querySelector('[data-metric-key=indoorTemperatureAvg]').innerText"), '0 °C')
        self.browser.run("window.__widgetSelf.ctx.data[0].data=[[2,null]]; window.__widgetSelf.onDataUpdated();")
        self.assertEqual(self.browser.run("return document.querySelector('[data-metric-key=indoorTemperatureAvg]').innerText"), '--')

    def test_navigation_preserves_barn_params_and_uses_open_or_update(self):
        self.mount('static', 'header', state='vent_detail', settings={'sourceMode': 'demo'}, params={'barnId': 'barn-nd2-1'})
        self.browser.run("document.querySelector('[data-nav=vent_history]').click()")
        call = self.browser.run('return window.__calls[0]')
        self.assertEqual(call[0], 'updateState')
        self.assertEqual(call[1], 'vent_history')
        self.assertEqual(call[2]['barnId'], 'barn-nd2-1')
        self.browser.run("document.querySelector('[data-nav=default]').click()")
        self.assertEqual(self.browser.run('return window.__calls[1][0]'), 'openState')

    def test_destroy_disconnects_resize_observer_and_two_instances_are_independent(self):
        self.mount('latest', 'kpis', settings={'keyMap': {'indoorTemperatureAvg': 'a'}},
                   ctx={'data': [{'dataKey': {'name': 'a'}, 'data': [[1, 11]]}]})
        destroyed = self.browser.run("window.__widgetSelf.onDestroy(); return [window.__widgetSelf._ventNode,window.__widgetSelf._ventObserver,window.__widgetSelf._ventDraw]")
        self.assertEqual(destroyed, [None, None, None])
        result = self.browser.run(r'''
          var payload=arguments[0], a=document.createElement('div'),b=document.createElement('div'); document.body.append(a,b);
          function mount(host,key,value) {
            host.innerHTML=payload.descriptor.templateHtml;
            var self={ctx:{$container:[host],settings:{component:'kpis',viewState:'vent_detail',sourceMode:'live',keyMap:{indoorTemperatureAvg:key}},
              data:[{dataKey:{name:key},data:[[1,value]]}],detectChanges:function(){},stateController:{getStateId:function(){return 'vent_detail';},getStateParams:function(){return {};}}}};
            new Function('self',payload.descriptor.controllerScript)(self); self.onInit(); return host.querySelector('[data-metric-key=indoorTemperatureAvg]').innerText;
          }
          return [mount(a,'a',1),mount(b,'b',0)];''', self.payloads['latest'])
        self.assertNotEqual(result[0], result[1])

    def test_settings_exposes_224_readonly_values_and_tabs_switch(self):
        self.mount('latest', 'settings', state='vent_settings', settings={'sourceMode': 'demo'})
        self.assertIn('224 thông số', self.browser.run("return document.querySelector('.vent-modular-root').innerText"))
        count = self.browser.run("return document.querySelectorAll('[data-settings-tab]').length")
        self.assertGreater(count, 1)
        self.browser.run("document.querySelectorAll('[data-settings-tab]')[1].click()")
        visible = self.browser.run("return [...document.querySelectorAll('[data-settings-group]')].filter(x=>!x.hidden).map(x=>x.getAttribute('data-settings-group'))")
        self.assertEqual(visible, ['1'])
        self.assertEqual(self.browser.run("return document.querySelectorAll('input:not([type=search]),textarea,select').length"), 0)



if __name__ == '__main__':
    unittest.main()
