(function (root) {
  "use strict";
  var STATES = ["default", "vent_detail", "vent_history", "vent_alarms", "vent_settings"];
  var labels = {default: "Tổng quan", vent_detail: "Giám sát", vent_history: "Lịch sử", vent_alarms: "Cảnh báo", vent_settings: "Cài đặt"};
  var ENUM_LABELS = {MANUAL: "MANUAL", AUTO: "AUTO", ACTUAL_TEMPERATURE: "Nhiệt độ thực", PERCEIVED_TEMPERATURE: "Nhiệt độ cảm nhận",
    STEP: "STEP", VFD: "VFD", DISABLED: "Tắt", ENABLED: "Bật"};
  var vm;
  function esc(value) { return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) { return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c]; }); }
  function isMissing(value) { return value === null || value === undefined; }
  function normalizeState(id) { return STATES.indexOf(id) >= 0 ? id : "default"; }
  function metric(key) { return vm.metrics[key] || {value: null, unit: "", quality: "UNKNOWN", configured: true}; }
  function stateLabel(state) { return state === "NOT_CONFIGURED" ? "NOT CONFIGURED" : state; }
  function displayText(item) {
    if (item.configured === false) return "NOT CONFIGURED";
    if (isMissing(item.value)) return "--";
    return ENUM_LABELS[item.value] || String(item.value);
  }
  function value(item) {
    var text = displayText(item);
    if (text === "--" || text === "NOT CONFIGURED" || !item.unit || typeof item.value !== "number") return '<span class="' + (text === "NOT CONFIGURED" ? "status-NOT_CONFIGURED" : "") + '">' + esc(text) + '</span>';
    return esc(text) + " <small>" + esc(item.unit) + "</small>";
  }
  function plainValue(item) {
    var text = displayText(item);
    return typeof item.value === "number" && item.unit ? text + " " + item.unit : text;
  }
  function header(state) {
    return '<header class="vent-header"><div class="vent-header__top"><strong class="vent-header__title">SIBA · Thông gió</strong>' +
      '<span class="vent-header__scope">' + esc(vm.scope.farm) + ' · ' + esc(vm.scope.area) + '</span>' +
      '<b class="demo-badge">' + esc(vm.badgeLabel) + '</b></div><nav class="state-tabs" aria-label="Trạng thái dashboard">' +
      STATES.map(function (item) { return '<a href="#' + item + '" data-nav="' + item + '" class="' + (item === state ? 'active' : '') + '">' + labels[item] + '</a>'; }).join("") + '</nav></header>';
  }
  function kpi(label, key, icon) {
    var item = metric(key);
    return '<article class="kpi"><div class="kpi__head"><span class="kpi__icon">' + icon + '</span>' + label + '</div>' +
      '<b class="kpi__value">' + value(item) + '</b><span class="kpi__quality quality-' + item.quality + '">' + item.quality +
      (item.ts ? ' · ' + new Date(item.ts).toLocaleTimeString('vi-VN', {hour:'2-digit', minute:'2-digit'}) : '') + '</span></article>';
  }
  function summaryValue(key) { var item = vm.summary[key]; return isMissing(item) ? "--" : item; }
  function summaryKpi(label, key, icon) {
    return '<article class="kpi"><div class="kpi__head"><span class="kpi__icon">' + icon + '</span>' + label + '</div>' +
      '<b class="kpi__value">' + esc(summaryValue(key)) + '</b><span class="kpi__quality">DEMO SUMMARY</span></article>';
  }
  var IDENTITY_TAGS = {PILOT: ['PILOT · DEMO', 'Nhà pilot có thật; trạng thái thông gió là dữ liệu demo'],
    LIVE_BARN_SIMULATED_STATE: ['DEMO', 'Nhà có thật; hệ thông gió chưa xác minh, trạng thái mô phỏng'],
    SYNTHETIC: ['SYNTHETIC', 'Nhà tổng hợp chỉ để minh họa bố cục; không tồn tại']};
  function identityTag(barn) {
    var tag = IDENTITY_TAGS[barn.identity] || IDENTITY_TAGS.SYNTHETIC;
    return ' <em class="identity-' + esc(barn.identity) + '" title="' + esc(tag[1]) + '">' + esc(tag[0]) + '</em>';
  }
  function sourceTag(alarm) { return '<i class="source-tag source-' + esc(alarm.source) + '">' + esc(isMissing(alarm.source) ? 'UNKNOWN' : alarm.source) + '</i>'; }
  function overview() {
    return '<section class="view"><div class="kpi-grid">' + summaryKpi('Tổng số nhà', 'barns', '⌂') +
      summaryKpi('Đang trực tuyến', 'online', '●') + summaryKpi('Cần chú ý', 'attention', '!') +
      summaryKpi('Cảnh báo đang mở', 'activeAlarms', '△') + '</div><div class="overview-grid"><section class="panel">' +
      '<div class="panel__head"><div><h2>Toàn trại</h2><p>Chọn một nhà để xem giám sát thông gió.</p></div><span class="muted">Trạng thái mọi nhà là mô phỏng</span></div>' +
      '<div class="barn-grid">' + vm.barns.map(function (barn) {
        return '<button class="barn-card" data-nav="vent_detail"><b>' + esc(barn.label) + identityTag(barn) + '</b>' +
          '<span class="status-' + barn.connectivity + '">' + barn.connectivity + '</span><span class="quality-' + barn.freshness + '">Dữ liệu: ' + barn.freshness + '</span>' +
          '<span>Chế độ: ' + esc(barn.mode) + ' · Cấp: ' + (isMissing(barn.stage) ? '--' : esc(barn.stage)) + '</span><span class="status-' + barn.alarm + '">Cảnh báo: ' + barn.alarm + '</span></button>';
      }).join('') + '</div></section><section class="panel"><div class="panel__head"><div><h2>Cảnh báo ưu tiên</h2>' +
      '<p>Chỉ xem; không có thao tác vòng đời.</p></div><a href="#vent_alarms" data-nav="vent_alarms" class="muted">Xem tất cả →</a></div><div class="alarm-list">' +
      vm.alarms.map(function (alarm) { return '<article class="alarm-mini ' + alarm.severity + '"><b>' + esc(alarm.type) + sourceTag(alarm) + '</b><span>' +
        esc(alarm.message) + '</span><small>' + esc(alarm.originator) + '</small></article>'; }).join('') + '</div></section></div>' + footer() + '</section>';
  }
  function equipmentCards() {
    return vm.equipment.map(function (item) { return '<article class="equipment-card state-card-' + esc(item.state) + '"><small>' + esc(item.label) + '</small>' +
      '<b class="status-' + esc(item.state) + '">' + esc(stateLabel(item.state)) + '</b><span class="muted">' +
      (item.configured ? 'Dữ liệu: ' + esc(item.quality) : 'Mapping PLC: N/A') + '</span></article>'; }).join('');
  }
  function louverShape(item, y) {
    return '<g class="louver quality-' + esc(item.quality) + '"><rect x="300" y="' + y + '" width="300" height="24" rx="4"/><text class="svg-sub" x="450" y="' + (y + 16) + '">' +
      esc(item.label) + ' · ' + esc(plainValue(item)) + ' · ' + esc(item.quality) + '</text></g>';
  }
  function synoptic() {
    var fans = vm.equipment.slice(0, 6);
    return '<div class="synoptic" role="region" aria-label="Sơ đồ thông gió có thể cuộn ngang"><svg viewBox="0 0 900 244" role="img" aria-label="Sơ đồ thông gió chỉ đọc nhà ' + esc(vm.scope.selectedBarn) + '">' +
      '<rect class="zone" x="45" y="14" width="810" height="220" rx="6"/><path class="pipe" d="M90 116H810"/>' + fans.map(function (fan, index) {
        var x = 130 + index * 128;
        return '<g class="fan ' + esc(fan.state) + '"><circle cx="' + x + '" cy="116" r="29"/><path class="pipe" d="M' + (x-13) + ' 103L' + (x+13) +
          ' 129M' + (x+13) + ' 103L' + (x-13) + ' 129"/><text class="svg-label" x="' + x + '" y="166">' + esc(fan.label) +
          '</text><text class="svg-sub state-' + esc(fan.state) + '" x="' + x + '" y="183">' + esc(stateLabel(fan.state)) + '</text></g>';
      }).join('') + louverShape(vm.louvers[0], 26) + louverShape(vm.louvers[1], 198) + '</svg></div>';
  }
  // Cờ cấp hệ thống: không suy ra quạt/bơm nào lỗi.
  function systemFlags() {
    var names = {equipmentFaultActive: 'Lỗi thiết bị tổng', externalHighTemperatureAlarm: 'Thermostat nhiệt độ cao'};
    return '<div class="system-flags" aria-label="Cờ trạng thái cấp hệ thống">' + vm.systemFlags.map(function (flag) {
      return '<span class="system-flag flag-' + esc(flag.value) + '"><small>' + esc(names[flag.key]) + '</small><b>' + esc(stateLabel(flag.value)) + '</b></span>';
    }).join('') + '<span class="system-flag-note">Cấp hệ thống · PLC không chỉ rõ thiết bị lỗi</span></div>';
  }
  function summaryRow(label, content, className, tag) {
    return '<div class="summary-row"><span>' + label + (tag ? ' <i class="derived-tag">' + tag + '</i>' : '') + '</span><b' + (className ? ' class="' + className + '"' : '') + '>' + content + '</b></div>';
  }
  function secondaryRow(label, key) {
    var item = metric(key);
    return '<div class="secondary-row"><span>' + label + '<small class="quality-' + item.quality + '">' + (item.configured === false ? 'N/A' : item.quality) + '</small></span><b>' + value(item) + '</b></div>';
  }
  function operationCell(label, key) {
    var item = metric(key);
    return '<div class="operation-cell"><small>' + label + '</small><b>' + value(item) + '</b></div>';
  }
  function vfdSection() {
    if (metric('fanControlMode').value !== 'VFD') return '';
    return '<h3 class="subsection-title">VFD (OPTIONAL)</h3><div class="secondary-metrics">' + secondaryRow('Tốc độ đặt kênh 1', 'fan01SpeedSetpoint') +
      secondaryRow('Tốc độ đặt kênh 2', 'fan02SpeedSetpoint') + secondaryRow('Phản hồi kênh 1', 'fan01SpeedFeedback') + secondaryRow('Phản hồi kênh 2', 'fan02SpeedFeedback') + '</div>';
  }
  function detail() {
    var quality = metric('dataQuality');
    return '<section class="view"><div class="kpi-grid">' + kpi('Nhiệt độ trung bình', 'indoorTemperatureAvg', '°') +
      kpi('Nhiệt độ ngoài trời', 'outdoorTemperature', '°') + kpi('Nhiệt độ cảm nhận', 'perceivedTemperature', '≈') +
      kpi('Độ ẩm trong nhà', 'relativeHumidity', '%') + '</div><div class="detail-layout"><section class="panel detail-main">' +
      '<div class="panel__head"><div><h2>Giám sát nhà ' + esc(vm.scope.selectedBarn) + '</h2><p>Sơ đồ read-only · trạng thái fixture có chủ đích</p></div>' +
      '<span class="quality-' + esc(isMissing(quality.value) ? quality.quality : quality.value) + '">' + esc(isMissing(quality.value) ? quality.quality : quality.value) + '</span></div>' +
      systemFlags() + synoptic() + '<div class="equipment-grid">' + equipmentCards() + '</div>' +
      '<h3 class="subsection-title">Thông số vận hành</h3><div class="operation-grid">' +
      operationCell('Nhiệt độ đặt hiện tại', 'temperatureSetpointCurrent') + operationCell('Nhiệt độ cảm nhận đặt', 'perceivedTemperatureSetpointCurrent') +
      operationCell('Độ ẩm đặt hiện tại', 'humiditySetpointCurrent') + operationCell('Nhiệt độ cảm biến 1', 'indoorTemperature01') +
      operationCell('Nhiệt độ cảm biến 2', 'indoorTemperature02') + operationCell('Tổng đàn', 'pigCount') +
      operationCell('Heo chết tích lũy', 'pigDeathCount') + operationCell('Ngày tuổi', 'pigAgeDay') + '</div></section>' +
      '<aside class="panel controller-panel"><div class="panel__head"><div><h2>Bộ điều khiển</h2><p>Thông tin chỉ đọc</p></div></div><div class="controller-summary">' +
      summaryRow('Kết nối', esc(vm.controller.online), 'status-' + vm.controller.online, 'PLATFORM') +
      summaryRow('Chế độ', value(metric('operatingMode'))) + summaryRow('Cơ sở điều khiển', value(metric('controlBasis'))) +
      summaryRow('Điều khiển quạt', value(metric('fanControlMode'))) + summaryRow('Cấp hiện tại', esc(vm.controller.stageDisplay)) +
      summaryRow('Khử ẩm', value(metric('dehumidificationEnabled'))) +
      summaryRow('Chất lượng dữ liệu', value(quality), 'quality-' + (isMissing(quality.value) ? 'UNKNOWN' : esc(quality.value)), 'PLATFORM') + '</div>' +
      '<h3 class="subsection-title">Dữ liệu bổ sung</h3><div class="secondary-metrics">' + secondaryRow('Tốc độ gió', 'airSpeed') + secondaryRow('Lưu lượng gió', 'airFlow') +
      secondaryRow('Nước tiêu thụ (tổng tích lũy)', 'waterConsumptionTotal') + secondaryRow('Lưu lượng nước', 'waterFlow') + '</div>' + vfdSection() +
      '<div class="notice compact-notice">Giá trị `--` là chưa có dữ liệu runtime; không quy đổi thành 0. NOT CONFIGURED = kỹ sư PLC khai báo N/A.</div>' +
      '<a href="#vent_history" data-nav="vent_history" class="text-link">Xem lịch sử →</a></aside></div>' + footer() + '</section>';
  }
  function seriesPath(key) {
    var values = vm.history.map(function (row) { return row[key]; });
    var valid = values.filter(function (item) { return typeof item === 'number'; });
    if (!valid.length) return '';
    var min = Math.min.apply(null, valid), max = Math.max.apply(null, valid), penDown = false, step = 620 / Math.max(values.length - 1, 1);
    return values.map(function (item, index) {
      if (typeof item !== 'number') { penDown = false; return ''; }
      var x = 55 + index * step;
      var y = 245 - ((item - min) / (max - min || 1)) * 175;
      var command = penDown ? 'L' : 'M'; penDown = true;
      return command + x.toFixed(1) + ' ' + y.toFixed(1);
    }).join(' ');
  }
  function historyQualityClass(quality) { return ['CURRENT', 'STALE', 'OFFLINE'].indexOf(quality) >= 0 ? quality : 'UNKNOWN'; }
  function historyValue(item, unit) { return isMissing(item) ? '--' : esc(item) + ' ' + unit; }
  function airWater() {
    var keys = ['airSpeed', 'airFlow', 'waterConsumptionTotal'];
    var hasData = vm.history.some(function (row) { return keys.some(function (key) { return typeof row[key] === 'number'; }); });
    return '<section class="panel air-water"><div class="panel__head"><div><h2>Gió & nước</h2>' +
      '<p>Chỉ đọc · nước là bộ đếm tổng tích lũy; lượng theo ngày/lứa tính delta ở platform khi có dữ liệu.</p></div>' +
      '<span class="muted">m/s · m3/h · L</span></div>' + (hasData ? '' : '<div class="notice compact-notice">Chưa có dữ liệu gió & nước từ PLC; không hiển thị giá trị giả.</div>') +
      '<div class="table-wrap"><table class="data-table"><thead><tr><th>Thời gian</th><th>Tốc độ gió</th><th>Lưu lượng gió</th><th>Nước tiêu thụ (tổng)</th><th>Chất lượng</th></tr></thead><tbody>' +
      vm.history.slice().reverse().map(function (row) { return '<tr><td>' + new Date(row.ts).toLocaleString('vi-VN') + '</td><td>' + historyValue(row.airSpeed, 'm/s') +
        '</td><td>' + historyValue(row.airFlow, 'm3/h') + '</td><td>' + historyValue(row.waterConsumptionTotal, 'L') + '</td><td><span class="pill quality-' +
        historyQualityClass(row.quality) + '">' + esc(row.quality) + '</span></td></tr>'; }).join('') + '</tbody></table></div></section>';
  }
  function history() {
    return '<section class="view"><section class="panel"><div class="panel__head"><div><h2>Lịch sử môi trường · 6 giờ</h2>' +
      '<p>Điểm thiếu tạo khoảng trống; không chuyển thành 0.</p></div><span class="muted">°C · %RH</span></div><div class="legend">' +
      '<span><i style="background:#00d4e0"></i>Trong nhà</span><span><i style="background:#ffc857"></i>Ngoài trời</span>' +
      '<span><i style="background:#ff8fcf"></i>Cảm nhận</span><span><i style="background:#6aa9ff"></i>Độ ẩm</span></div><div class="chart-wrap">' +
      '<svg class="chart" viewBox="0 0 720 280"><path class="grid" d="M55 70H675M55 128H675M55 187H675M55 245H675"/>' +
      '<path class="inside" d="' + seriesPath('indoorTemperatureAvg') + '"/><path class="outside" d="' + seriesPath('outdoorTemperature') + '"/>' +
      '<path class="perceived" d="' + seriesPath('perceivedTemperature') + '"/><path class="humidity" d="' + seriesPath('relativeHumidity') + '"/>' +
      '<text x="55" y="266">02:30</text><text x="625" y="266">08:30</text></svg></div></section><section class="panel table-wrap env-table">' +
      '<table class="data-table"><thead><tr><th>Thời gian</th><th>Nhiệt độ trong</th><th>Nhiệt độ ngoài</th><th>Nhiệt độ cảm nhận</th><th>Độ ẩm</th><th>Chất lượng</th></tr></thead><tbody>' +
      vm.history.slice().reverse().map(function (row) { return '<tr><td>' + new Date(row.ts).toLocaleString('vi-VN') + '</td><td>' + historyValue(row.indoorTemperatureAvg, '°C') +
        '</td><td>' + historyValue(row.outdoorTemperature, '°C') + '</td><td>' + historyValue(row.perceivedTemperature, '°C') + '</td><td>' +
        historyValue(row.relativeHumidity, '%RH') + '</td><td><span class="pill quality-' + historyQualityClass(row.quality) + '">' + esc(row.quality) + '</span></td></tr>'; }).join('') +
      '</tbody></table></section>' + airWater() + footer() + '</section>';
  }
  function alarms() {
    return '<section class="view"><section class="panel"><div class="panel__head"><div><h2>Cảnh báo & lịch sử</h2><p>Read-only; không có thao tác vòng đời. PLC = cờ quy trình/phần cứng; PLATFORM = kết nối/độ tươi dữ liệu.</p></div></div>' +
      '<div class="table-wrap"><table class="data-table"><thead><tr><th>Mức</th><th>Loại / nội dung</th><th>Nguồn</th><th>Đối tượng</th><th>Thời gian</th><th>Trạng thái</th></tr></thead><tbody>' +
      vm.alarms.map(function (alarm) { return '<tr><td><span class="pill status-' + alarm.severity + '">' + esc(alarm.severity) + '</span></td><td><b>' + esc(alarm.type) +
        '</b><br><span class="muted">' + esc(alarm.message) + '</span></td><td>' + sourceTag(alarm) + '</td><td>' + esc(alarm.originator) + '</td><td>' + new Date(alarm.created).toLocaleString('vi-VN') +
        '</td><td>' + esc(alarm.status) + '</td></tr>'; }).join('') + '</tbody></table></div></section><p class="demo-limit">Fixture minh họa · alarm scope, retention và export production chưa được xác minh.</p>' + footer() + '</section>';
  }
  function settingValue(item) {
    var text = item.configured === false ? 'N/A' : displayText(item);
    return '<span class="setting-value" data-setting-key="' + esc(item.key) + '"' + (item.configured === false ? ' title="NOT CONFIGURED"' : '') + '>' + esc(text) + '</span>';
  }
  function settingsGroupId(index) { return 'vent-settings-group-' + index; }
  function settingsGroup(group, index) {
    var scalars = group.scalars.length ? '<div class="settings-list">' + group.scalars.map(function (item) {
      return '<div class="settings-row"><span>' + esc(item.label) + (item.contractStatus === 'OPTIONAL' ? ' <i class="derived-tag">OPTIONAL</i>' : '') + '</span>' +
        settingValue(item) + '<small>' + esc(item.unit) + '</small></div>'; }).join('') + '</div>' : '';
    var matrices = group.matrices.map(function (matrix) {
      return '<div class="table-wrap"><table class="data-table settings-matrix"><thead><tr><th>' + esc(matrix.rowLabel) + '</th>' + matrix.fields.map(function (field) {
        return '<th>' + esc(field.label) + (field.optional ? '*' : '') + (field.unit ? ' <small>' + esc(field.unit) + '</small>' : '') + '</th>'; }).join('') +
        '</tr></thead><tbody>' + matrix.slots.map(function (slot) {
          return '<tr><td>' + esc(matrix.rowLabel) + ' ' + esc(slot) + '</td>' + matrix.fields.map(function (field) {
            var item = matrix.cells[slot + ':' + field.id];
            return '<td>' + (item ? settingValue(item) : '') + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
    }).join('');
    var optional = group.matrices.some(function (m) { return m.fields.some(function (f) { return f.optional; }); });
    var note = group.matrices.some(function (m) { return m.prefix === 'stage'; }) ?
      '<p class="settings-note">9 slot = năng lực cấu hình tối đa của bộ điều khiển, không phải số cấp đang dùng.</p>' : '';
    return '<section class="panel settings-group" id="' + settingsGroupId(index) + '"><div class="panel__head"><div><h2>' + esc(group.name) + '</h2>' +
      '<p>' + group.count + ' thông số · chỉ đọc' + (optional ? ' · * = OPTIONAL' : '') + '</p></div></div>' + note + scalars + matrices + '</section>';
  }
  function settings() {
    var total = vm.settings.reduce(function (sum, group) { return sum + group.count; }, 0);
    return '<section class="view"><section class="panel"><div class="panel__head"><div><h2>Cài đặt bộ điều khiển</h2>' +
      '<p>READ-ONLY · ' + total + ' thông số theo Data Contract v' + esc(vm.contractVersion) + ' · `--` = chưa có dữ liệu PLC · không ghi tham số</p></div></div>' +
      '<nav class="settings-index" aria-label="Nhóm cài đặt">' + vm.settings.map(function (group, index) {
        return '<a href="#' + settingsGroupId(index) + '" data-scroll="' + settingsGroupId(index) + '">' + esc(group.name.replace('CÀI ĐẶT - ', '')) + ' <small>' + group.count + '</small></a>';
      }).join('') + '</nav></section>' + vm.settings.map(settingsGroup).join('') + footer() + '</section>';
  }
  function footer() { return '<footer class="footer"><span>Giám sát chỉ đọc · Fixture ' + esc(vm.fixtureVersion) + ' · Contract v' + esc(vm.contractVersion) + '</span><span>Sinh lúc ' + new Date(vm.generatedAt).toLocaleString('vi-VN') + '</span></footer>'; }
  // Điều hướng đi qua navigate(): bản standalone đổi hash, ThingsBoard gọi stateController.
  function render(container, viewModel, state, navigate) {
    vm = viewModel;
    state = normalizeState(state);
    var views = {default: overview, vent_detail: detail, vent_history: history, vent_alarms: alarms, vent_settings: settings};
    container.innerHTML = header(state) + views[state]();
    container.__ventNavigate = navigate;
    if (!container.__ventNavBound) {
      container.__ventNavBound = true;
      container.addEventListener('click', function (event) {
        var scroll = event.target.closest('[data-scroll]');
        if (scroll && container.contains(scroll)) {
          event.preventDefault();
          var section = container.querySelector('#' + scroll.getAttribute('data-scroll'));
          if (section) section.scrollIntoView({block: 'start'});
          return;
        }
        var target = event.target.closest('[data-nav]');
        if (!target || !container.contains(target)) return;
        event.preventDefault();
        container.__ventNavigate(normalizeState(target.getAttribute('data-nav')));
      });
    }
    return state;
  }
  root.VentilationDashboard = { STATES: STATES, render: render };
  if (root !== window) return;
  var app = document.getElementById("app");
  if (!app) return;
  function renderFromHash(data) {
    var id = location.hash.replace(/^#/, "");
    if (id.indexOf("vent-settings-group-") === 0) return;
    render(app, data, id || "default", function (next) { location.hash = next; });
  }
  new root.VentilationAdapter.FixtureSource('../fixtures/ventilation/demo.json').load().then(function (data) {
    renderFromHash(data);
    window.addEventListener('hashchange', function () { renderFromHash(data); });
  }).catch(function (error) { app.innerHTML = '<p class="error">Không nạp được fixture demo: ' + esc(error.message) + '</p>'; });
}(window));
