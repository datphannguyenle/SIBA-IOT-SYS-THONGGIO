/* Local test harness only. Never included in ThingsBoard widget descriptors. */
(function () {
  'use strict';
  var fixture, dashboard, views = [];
  function navigate(state, params) {
    location.hash = state + (params && params.barnId ? '?barnId=' + encodeURIComponent(params.barnId) : '');
  }
  function draw() {
    if (!fixture || !dashboard) return;
    views.forEach(function (view) { VentilationModular.destroy(view); });
    views = [];
    var hash = location.hash.slice(1).split('?'), state = hash[0] || 'default';
    var params = {state: state, barnId: new URLSearchParams(hash[1] || '').get('barnId') || fixture.barns[0].id};
    var config = dashboard.configuration, layout = config.states[state];
    if (!layout) { navigate('default', {}); return; }
    var grid = document.getElementById('modular-grid'); grid.innerHTML = '';
    var mode = document.getElementById('test-source').value;
    Object.entries(layout.layouts.main.widgets).forEach(function (entry) {
      var id = entry[0], position = entry[1], instance = config.widgets[id], settings = Object.assign({}, instance.config.settings);
      var cell = document.createElement('section'); cell.className = 'preview-widget';
      cell.style.gridColumn = (position.col + 1) + ' / span ' + position.sizeX;
      cell.style.gridRow = (position.row + 1) + ' / span ' + position.sizeY;
      var node = document.createElement('div'); node.className = 'vent-modular-root';
      node.setAttribute('data-component', settings.component); cell.appendChild(node); grid.appendChild(cell); views.push(node);
      var ctx = {data: [], stateController: {getStateParams: function () { return {}; }}};
      if (mode !== 'demo') {
        settings.sourceMode = 'live'; settings.context = {farm: 'CTX TEST · không kết nối PLC', selectedBarn: 'Nhà kiểm thử'};
      }
      if (mode === 'subscription') {
        settings.keyMap = {indoorTemperatureAvg: 'rawTemperature', operatingMode: 'rawMode', fanStage: 'rawStage'};
        ctx.data = [{dataKey: {name: 'rawTemperature'}, data: [[Date.now(), 30.4]]},
          {dataKey: {name: 'rawMode'}, data: [[Date.now(), 0]]}, {dataKey: {name: 'rawStage'}, data: [[Date.now(), 0]]}];
      }
      var vm = VentilationSource.createViewModel(ctx, settings, fixture);
      VentilationModular.render(node, vm, settings.component, navigate, params);
    });
    window.__ventPreviewReady = state;
  }
  Promise.all([fetch('../fixtures/ventilation/demo.json').then(function (r) { return r.json(); }),
    fetch('../deploy/thingsboard/build/modular/dashboard.json').then(function (r) { return r.json(); })]).then(function (values) {
      fixture = values[0]; dashboard = values[1]; draw();
  }).catch(function () { document.getElementById('modular-grid').textContent = 'Không nạp được bản dựng kiểm thử.'; });
  window.addEventListener('hashchange', draw);
  window.addEventListener('resize', draw);
  document.getElementById('test-source').addEventListener('change', draw);
}());
