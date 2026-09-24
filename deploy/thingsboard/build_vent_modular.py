#!/usr/bin/env python3
"""Build isolated VENT-010 widgets; never access ThingsBoard or provision devices."""
import json
import sys
import uuid

from build_vent_demo import read, scope_iife, strip_css_comments
from vent_demo_common import ROOT, DASHBOARD_TITLE, STATES, write_json

OUT = ROOT / 'deploy/thingsboard/build/modular'
NS = uuid.UUID('bb572bc0-a117-4595-a6e2-553de66ca010')
KINDS = ('static', 'latest', 'timeseries', 'alarm', 'overview')
# Danh sách nhà cần nhiều entity; mọi widget khác giữ ràng buộc một entity.
MULTI_ENTITY_KINDS = ('overview',)
TB_TYPE = {'overview': 'latest'}
FQNS = {kind: 'siba_vent_demo.modular_' + kind for kind in KINDS}
# Position is native ThingsBoard grid; widget data/settings are independently editable.
# 24px rows + 8px gaps, bounded scrolling instead of viewport scaling.
LAYOUTS = {
    'default': [('header', 0, 0, 24, 3), ('overview', 0, 3, 24, 15)],
    'vent_detail': [('header', 0, 0, 24, 4), ('kpis', 0, 4, 24, 4),
                    ('synoptic', 0, 8, 16, 14), ('controller', 16, 8, 8, 14),
                    ('metrics', 0, 22, 24, 7)],
    'vent_history': [('header', 0, 0, 24, 4), ('history', 0, 4, 24, 22)],
    'vent_alarms': [('header', 0, 0, 24, 4), ('alarms', 0, 4, 24, 18)],
    'vent_settings': [('header', 0, 0, 24, 4), ('settings', 0, 4, 24, 20)],
}


def kind_for(component):
    return {'header': 'static', 'history': 'timeseries', 'alarms': 'alarm', 'overview': 'overview'}.get(component, 'latest')


def controller(multi_entity=False):
    # Keep the pure decoder, omit legacy standalone fixture-loading/network classes.
    adapter = read('widgets/ventilation-adapter.js').split('  function FixtureSource(')[0]
    adapter += '''  root.VentilationAdapter = {createViewModel:createViewModel, stageDisplay:stageDisplay,
      mapHistory:mapHistory, RUN_KEYS:RUN_KEYS, FLAG_KEYS:FLAG_KEYS, HISTORY_KEYS:HISTORY_KEYS};
}(window));'''
    modules = '\n'.join((scope_iife(read('widgets/ventilation-contract-v03.js'), 'contract'),
                         scope_iife(adapter, 'pure-adapter'),
                         scope_iife(read('widgets/ventilation-source.js'), 'source'),
                         scope_iife(read('dashboard/alarm-total-subscription.js'), 'alarm-total'),
                         scope_iife(read('dashboard/modular.js'), 'modular')))
    fixture = json.dumps(json.loads(read('fixtures/ventilation/demo.json')), ensure_ascii=False)
    return '''// GENERATED. Repo source only; no device API or write operations.
var __vent = {};
var WIDGET_MULTI_ENTITY = ''' + ('true' if multi_entity else 'false') + ''';
''' + modules + '\nvar fixture = ' + fixture + ''';
self.onInit = function () {
  var ctx = self.ctx, node = ctx.$container[0].querySelector('.vent-modular-root');
  self._ventNode = node;
  self._ventDraw = function () {
    if (!self._ventNode) return;
    var settings = ctx.settings || {}, savedTab = node.querySelector('[data-settings-tab].is-active');
    var params = Object.assign({}, ctx.stateController && ctx.stateController.getStateParams ? ctx.stateController.getStateParams() : {});
    params.state = settings.viewState || (ctx.stateController && ctx.stateController.getStateId ? ctx.stateController.getStateId() : 'default');
    if (savedTab) params.settingsGroup = Number(savedTab.getAttribute('data-settings-tab'));
    var vm = __vent.VentilationSource.createViewModel(ctx, settings, settings.sourceMode === 'demo' ? fixture : undefined);
    if (self._ventAlarmTotal && vm.summary) {
      vm.summary.activeAlarms = self._ventAlarmTotal.state.loaded ? self._ventAlarmTotal.state.total : null;
    }
    if (!params.barnId && vm.demo) params.barnId = (vm.barns[0] || {}).id;
    var scroll = node.scrollTop;
    __vent.VentilationModular.render(node, vm, settings.component || 'kpis', function (next, values) {
      if (!ctx.stateController) return;
      var merged = Object.assign({}, params, values); delete merged.state;
      // Alias stateEntity của TB đọc params.entityId dạng {entityType, id}; chỉ truyền id chuỗi
      // là widget chi tiết không bind được thiết bị nào.
      if (values && values.barnId && values.barnEntityType) {
        merged.entityId = {entityType: values.barnEntityType, id: values.barnId};
        if (values.barnLabel) { merged.entityName = values.barnLabel; merged.entityLabel = values.barnLabel; }
      }
      var change = next === 'default' || params.state === 'default' ? 'openState' : 'updateState';
      if (typeof ctx.stateController[change] !== 'function') change = 'openState';
      ctx.stateController[change](next, merged, false);
    }, params);
    node.scrollTop = scroll;
    // Chẩn đoán bật bằng tay (settings.diagnostics = true): chỉ ghi HÌNH DẠNG của subscription,
    // không ghi giá trị, không gọi mạng. Dùng khi một widget "đã nạp" mà vẫn trống.
    if (settings.diagnostics === true) {
      var probe = {component: settings.component || null, mapping: (vm.mapping || {}).status || null,
        scope: (vm.mapping || {}).scope || null, rows: (ctx.data || []).length,
        latestRows: (ctx.latestData || []).length,
        datasources: (ctx.datasources || []).length,
        alarmsStatus: (vm.alarmsSource || {}).status || null, alarms: (vm.alarms || []).length};
      var sub = ctx.defaultSubscription;
      probe.subscriptionKeys = sub ? Object.keys(sub).filter(function (key) {
        return key.toLowerCase().indexOf('alarm') >= 0; }) : null;
      var block = sub && sub.alarms;
      probe.alarmBlock = block ? Object.keys(block) : null;
      probe.alarmDataCount = block && Array.isArray(block.data) ? block.data.length : null;
      probe.alarmTotal = block ? block.totalElements : null;
      // Alias stateEntity chỉ resolve khi state param mang entityId; đây là chỗ hay mất nhất.
      var source = sub && sub.alarmSource;
      probe.alarmSourceEntity = source ? {type: source.type || null,
        alias: source.entityAliasId || null,
        entityId: source.entityId ? (source.entityId.id || String(source.entityId)) : null,
        entityName: source.entityName || null,
        keys: (source.dataKeys || []).map(function (key) { return key.name; })} : null;
      probe.canSubscribe = !!(sub && typeof sub.subscribeForAlarms === 'function');
      probe.stateParams = Object.keys(params || {});
      probe.hasEntityIdParam = !!(params && params.entityId && params.entityId.id);
      node.setAttribute('data-vent-diagnostic', JSON.stringify(probe));
    }
    if (ctx.detectChanges) ctx.detectChanges();
  };
  self._ventDraw();
  if ((ctx.settings || {}).sourceMode === 'live' && (ctx.settings || {}).component === 'overview' &&
      (ctx.settings || {}).alarmTotalSource) {
    self._ventAlarmTotal = __vent.VentilationAlarmTotal.attach(ctx,
      {alarmSource: ctx.settings.alarmTotalSource}, function () { if (self._ventDraw) self._ventDraw(); });
  }
  // Đánh giá freshness cả lúc nguồn ngừng phát, không cần REST poller.
  self._ventClock = setInterval(function () { if (self._ventDraw) self._ventDraw(); }, 5000);
  self._ventObserver = typeof ResizeObserver === 'function' ? new ResizeObserver(function () {
    var width = Math.round(node.clientWidth);
    if (width !== self._ventWidth) { self._ventWidth = width; self._ventDraw(); }
  }) : null;
  if (self._ventObserver) self._ventObserver.observe(node);
  // Alarm subscription is platform-owned, read-only. Never create a custom REST poller.
  if ((ctx.settings || {}).sourceMode === 'live' && (ctx.settings || {}).component === 'alarms') {
    var subscription = ctx.defaultSubscription;
    if (subscription && subscription.subscribeForAlarms) {
      // sortOrder.key PHẢI là EntityKey {type, key}. Truyền chuỗi thì máy chủ không dựng được
      // đối tượng và BỎ QUA lệnh trong im lặng: không dữ liệu, không lỗi, bảng trống mãi mãi.
      subscription.subscribeForAlarms({pageSize: 100, page: 0,
        sortOrder: {key: {type: 'ALARM_FIELD', key: 'createdTime'}, direction: 'DESC'},
        statusList: [], severityList: [], typeList: [], searchPropagatedAlarms: false}, null);
    }
  }
};
self.onDataUpdated = function () { if (self._ventDraw) self._ventDraw(); };
self.onLatestDataUpdated = self.onDataUpdated;
self.onResize = function () { if (self._ventDraw) self._ventDraw(); };
self.onDestroy = function () {
  if (self._ventClock) clearInterval(self._ventClock);
  if (self._ventAlarmTotal) self._ventAlarmTotal.destroy();
  if (self._ventObserver) self._ventObserver.disconnect();
  if (self._ventNode) __vent.VentilationModular.destroy(self._ventNode);
  self._ventNode = null; self._ventDraw = null; self._ventObserver = null;
};
self.typeParameters = function () {
  if (WIDGET_MULTI_ENTITY) return {maxDatasources: -1, singleEntity: false, hasAdditionalLatestDataKeys: true};
  return {maxDatasources: 1, singleEntity: true, hasAdditionalLatestDataKeys: true};
};
'''


def widget_types():
    css = strip_css_comments(read('dashboard/modular.css')) + '''
.vent-modular-root{height:100%;overflow:auto;overscroll-behavior:contain;min-width:0}
.vent-modular-root h1,.vent-modular-root h2,.vent-modular-root h3{font-weight:700;line-height:1.25}
.vent-modular-root p{line-height:1.42}
.vent-modular-root :where(b,strong){font-weight:700}
.vent-modular-root :where(table,th,td){font-family:inherit;font-size:inherit}
.vent-modular-root [hidden]{display:none!important}
'''
    return {kind: {'fqn': FQNS[kind], 'name': 'SIBA ventilation · modular ' + kind,
                  'description': 'VENT-010 functional widget. Explicit demo or mapped read-only subscription. No PLC commands.',
                  'deprecated': False, 'scada': False,
                  'descriptor': {'type': TB_TYPE.get(kind, kind), 'sizeX': 12, 'sizeY': 8, 'resources': [],
                                 'templateHtml': '<div class="vent-modular-root"></div>', 'templateCss': css,
                                 'controllerScript': controller(kind in MULTI_ENTITY_KINDS),
                                 'settingsSchema': '', 'dataKeySettingsSchema': '',
                                 'defaultConfig': json.dumps(dict(alarm_source(TB_TYPE.get(kind, kind)),
                                     showTitle=False, datasources=[],
                                     settings={'component': 'kpis', 'sourceMode': 'live', 'keyMap': {}, 'freshnessMs': {}}))}}
            for kind in KINDS}



# TB duyệt widget kiểu alarm bằng [config.alarmSource] thay cho datasources; thiếu khóa này
# thì toàn bộ dashboard vỡ ngay khi mở (đọc entityAliasId của undefined).
def alarm_source(tb_type):
    if tb_type != 'alarm':
        return {}
    return {'alarmSource': {'type': 'entity', 'name': 'alarms', 'dataKeys': []}}


def dashboard():
    widgets, states = {}, {}
    for state, entries in LAYOUTS.items():
        layout = {}
        for component, col, row, width, height in entries:
            wid = str(uuid.uuid5(NS, state + ':' + component))
            position = {'col': col, 'row': row, 'sizeX': width, 'sizeY': height}
            config = {'title': component, 'showTitle': False, 'showTitleIcon': False, 'padding': '0px',
                      'backgroundColor': '#001827', 'color': '#f0f5ff', 'dropShadow': False,
                      'enableFullscreen': False, 'enableDataExport': False, 'actions': {}, 'datasources': [],
                      **alarm_source(TB_TYPE.get(kind_for(component), kind_for(component))),
                      'settings': {'component': component, 'viewState': state, 'sourceMode': 'demo',
                                   'demoUseSubscription': False, 'keyMap': {}, 'freshnessMs': {}},
                      'mobileHeight': {'header': 110, 'overview': 660, 'kpis': 220,
                                       'synoptic': 540, 'controller': 550, 'metrics': 440,
                                       'history': 750, 'alarms': 650, 'settings': 650}.get(component, 300)}
            widgets[wid] = {'id': wid, 'typeFullFqn': 'tenant.' + FQNS[kind_for(component)],
                            'type': TB_TYPE.get(kind_for(component), kind_for(component)), **position, 'config': config}
            layout[wid] = position
        states[state] = {'name': {'default': 'Tổng quan', 'vent_detail': 'Giám sát', 'vent_history': 'Lịch sử',
                                   'vent_alarms': 'Cảnh báo', 'vent_settings': 'Cài đặt · chỉ đọc'}[state],
                         'root': state == 'default', 'layouts': {'main': {'widgets': layout, 'gridSettings': {
                             'layoutType': 'default', 'columns': 24, 'margin': 6, 'outerMargin': True,
                             'autoFillHeight': False, 'mobileAutoFillHeight': False, 'mobileRowHeight': 24,
                             'rowHeight': 24, 'backgroundColor': '#001827'}}}}
    return {'title': DASHBOARD_TITLE, 'name': DASHBOARD_TITLE, 'configuration': {
        'widgets': widgets, 'states': states, 'entityAliases': {}, 'filters': {},
        'timewindow': {'displayValue': '', 'selectedTab': 0, 'realtime': {'timewindowMs': 21600000},
                       'aggregation': {'type': 'NONE', 'limit': 500}},
        'settings': {'stateControllerId': 'default', 'showTitle': False, 'showDashboardsSelect': False,
                     'showEntitiesSelect': False, 'showDashboardTimewindow': False,
                     'showDashboardExport': False, 'toolbarAlwaysOpen': False, 'hideToolbar': False,
                     'showFilters': False, 'dashboardCss': '.tb-widget-container>.tb-widget{border:0!important;box-shadow:none!important;background:#001827!important}'}}}


def validate(types, dash):
    assert list(dash['configuration']['states']) == STATES
    for kind, widget in types.items():
        descriptor = widget['descriptor']
        assert descriptor['type'] == TB_TYPE.get(kind, kind)
        multi = kind in MULTI_ENTITY_KINDS
        assert ('singleEntity: false' in descriptor['controllerScript']) is True
        assert ("WIDGET_MULTI_ENTITY = %s" % ('true' if multi else 'false')) in descriptor['controllerScript']
        assert len(json.dumps(descriptor, ensure_ascii=False)) < 900000
        for forbidden in ('sendOneWayRpc', 'sendTwoWayRpc', 'controlApi', 'ackAlarm', 'clearAlarm',
                          'saveEntityAttributes', 'fetch(', 'XMLHttpRequest(', 'WebSocket(', '/api/'):
            assert forbidden not in descriptor['controllerScript'], forbidden
    assert all(w['config']['settings']['sourceMode'] == 'demo' and not w['config']['datasources']
               for w in dash['configuration']['widgets'].values())
    for widget in dash['configuration']['widgets'].values():
        has_source = 'alarmSource' in widget['config']
        assert has_source == (widget['type'] == 'alarm'), widget['typeFullFqn']
        if has_source:
            assert not widget['config']['alarmSource'].get('entityAliasId')
    for kind, widget in types.items():
        default = json.loads(widget['descriptor']['defaultConfig'])
        assert ('alarmSource' in default) == (TB_TYPE.get(kind, kind) == 'alarm'), kind


def build(check=False):
    types, dash = widget_types(), dashboard()
    validate(types, dash)
    outputs = {**{'widget_' + k + '.json': v for k, v in types.items()}, 'dashboard.json': dash}
    for filename, payload in outputs.items():
        path = OUT / filename
        if check:
            assert path.is_file() and json.loads(path.read_text()) == payload, str(path)
        else:
            write_json(path, payload)
    return outputs


if __name__ == '__main__':
    build('--check' in sys.argv)
    print('VENT-010 modular build verified' if '--check' in sys.argv else 'VENT-010 modular build written')
