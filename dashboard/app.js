(function (root) {
  "use strict";
  var STATES = ["default", "vent_detail", "vent_history", "vent_alarms", "vent_settings"];
  var labels = {default: "Tổng quan", vent_detail: "Giám sát", vent_history: "Lịch sử", vent_alarms: "Cảnh báo", vent_settings: "Cài đặt"};
  var ENUM_LABELS = {MANUAL: "MANUAL", AUTO: "AUTO", ACTUAL_TEMPERATURE: "Nhiệt độ thực", PERCEIVED_TEMPERATURE: "Nhiệt độ cảm nhận",
    STEP: "STEP", VFD: "VFD", DISABLED: "Tắt", ENABLED: "Bật"};
  var vm, chartWidth = 720;
  function esc(value) { return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) { return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c]; }); }
  function isMissing(value) { return value === null || value === undefined; }
  function normalizeState(id) { return STATES.indexOf(id) >= 0 ? id : "default"; }
  function metric(key) { return vm.metrics[key] || {value: null, unit: "", quality: "UNKNOWN", configured: true}; }
  var STATUS_LABELS = {RUNNING: "Đang chạy", STOPPED: "Đã dừng", UNKNOWN: "Chưa rõ",
    NOT_CONFIGURED: "Chưa cấu hình", ONLINE: "Trực tuyến", OFFLINE: "Ngoại tuyến", CURRENT: "Hiện tại",
    STALE: "Dữ liệu cũ", NORMAL: "Bình thường", ACTIVE: "Đang bật", WARNING: "Cần chú ý", MAJOR: "Nghiêm trọng",
    NONE: "Không có"};
  function stateLabel(state) { return STATUS_LABELS[state] || state; }
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
      STATES.map(function (item) { return '<a href="#' + item + '" data-nav="' + item + '"' + (item === state ? ' class="active" aria-current="page"' : '') + '>' + labels[item] + '</a>'; }).join("") + '</nav></header>';
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
      '<b class="kpi__value">' + esc(summaryValue(key)) + '</b><span class="kpi__quality">TỔNG HỢP DEMO</span></article>';
  }
  var IDENTITY_TAGS = {PILOT: ['PILOT · DEMO', 'Nhà pilot có thật; trạng thái thông gió là dữ liệu demo'],
    LIVE_BARN_SIMULATED_STATE: ['DEMO', 'Nhà có thật; hệ thông gió chưa xác minh, trạng thái mô phỏng'],
    SYNTHETIC: ['SYNTHETIC', 'Nhà tổng hợp chỉ để minh họa bố cục; không tồn tại']};
  function identityTag(barn) {
    var tag = IDENTITY_TAGS[barn.identity] || IDENTITY_TAGS.SYNTHETIC;
    return ' <em class="identity-' + esc(barn.identity) + '" title="' + esc(tag[1]) + '">' + esc(tag[0]) + '</em>';
  }
  function sourceTag(alarm) { return '<i class="source-tag source-' + esc(alarm.source) + '">' + esc(isMissing(alarm.source) ? 'UNKNOWN' : alarm.source) + '</i>'; }
  function barnCard(barn) {
    var search = [barn.label, barn.connectivity, stateLabel(barn.connectivity), barn.freshness, stateLabel(barn.freshness), barn.mode, barn.alarm, stateLabel(barn.alarm)].join(' ').toLowerCase();
    return '<button type="button" class="barn-card" data-nav="vent_detail" data-barn-id="' + esc(barn.id) + '" data-filter-text="' + esc(search) + '"><b>' + esc(barn.label) + identityTag(barn) + '</b>' +
      '<span class="status-' + esc(barn.connectivity) + '" data-raw-state="' + esc(barn.connectivity) + '">' + esc(stateLabel(barn.connectivity)) + '</span><span class="quality-' + esc(barn.freshness) + '" data-raw-state="' + esc(barn.freshness) + '">Dữ liệu: ' + esc(stateLabel(barn.freshness)) + '</span>' +
      '<span>Chế độ: ' + esc(barn.mode) + ' · Cấp: ' + (isMissing(barn.stage) ? '--' : esc(barn.stage)) + '</span><span class="status-' + esc(barn.alarm) + '" data-raw-state="' + esc(barn.alarm) + '">Cảnh báo: ' + esc(stateLabel(barn.alarm)) + '</span></button>';
  }
  function overview() {
    return '<section class="view"><div class="kpi-grid">' + summaryKpi('Tổng số nhà', 'barns', '⌂') +
      summaryKpi('Đang trực tuyến', 'online', '●') + summaryKpi('Cần chú ý', 'attention', '!') +
      summaryKpi('Cảnh báo đang mở', 'activeAlarms', '△') + '</div><div class="overview-grid"><section class="panel">' +
      '<div class="panel__head"><div><h2>Toàn trại</h2><p>Chọn một nhà để xem ngữ cảnh giám sát. ND2-1 có dữ liệu chi tiết minh họa.</p></div><span class="muted">Trạng thái mọi nhà là mô phỏng</span></div>' +
      '<label class="local-filter"><span>Tìm nhà</span><input type="search" data-filter-input="barn" placeholder="VD: ND2-2, trực tuyến" autocomplete="off"></label>' +
      '<div class="barn-grid" data-filter-list="barn">' + vm.barns.map(barnCard).join('') + '</div><p class="filter-empty" data-filter-empty="barn" hidden>Không tìm thấy nhà phù hợp.</p>' + overviewIllustration() + '</section><section class="panel"><div class="panel__head"><div><h2>Cảnh báo ưu tiên</h2>' +
      '<p>Chỉ xem; không có thao tác vòng đời.</p></div><a href="#vent_alarms" data-nav="vent_alarms" class="muted">Xem tất cả →</a></div><div class="alarm-list">' +
      vm.alarms.map(function (alarm) { return '<article class="alarm-mini ' + alarm.severity + '"><b>' + esc(alarm.type) + sourceTag(alarm) + '</b><span>' +
      esc(alarm.message) + '</span><small>' + esc(alarm.originator) + '</small></article>'; }).join('') + '</div></section></div>' + footer() + '</section>';
  }
  function overviewIllustration() {
    var src = root.VentilationAssets ? root.VentilationAssets.barnIllustration : 'assets/ventilation-barn-v1.webp';
    return '<div class="overview-context"><div class="overview-context__copy"><p class="eyebrow">KHÔNG GIAN GIÁM SÁT</p><h3>Môi trường rõ ràng.<br>Vận hành trong tầm nhìn.</h3><p>Theo dõi môi trường, quạt và cửa khí trong cùng một giao diện.</p><a href="#vent_detail" data-nav="vent_detail" data-barn-id="' + esc(sampleBarnId()) + '" class="text-link">Xem nhà mẫu ND2-1 →</a></div><figure class="barn-illustration"><img src="' + esc(src) + '" width="1536" height="1024" alt="Minh họa kiến trúc nhà thông gió, không phải cấu hình thiết bị thực tế" decoding="async"><figcaption>MINH HỌA · Không phải bản vẽ hiện trạng</figcaption></figure></div>';
  }
  function equipmentCards() {
    return vm.equipment.map(function (item) { return '<article class="equipment-card state-card-' + esc(item.state) + '"><small>' + esc(item.label) + '</small>' +
      '<b class="status-' + esc(item.state) + '" data-raw-state="' + esc(item.state) + '">' + esc(stateLabel(item.state)) + '</b><span class="muted">' +
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
        return '<g class="fan ' + esc(fan.state) + ' quality-' + esc(fan.quality) + ' connectivity-' + esc(vm.controller.online) + '" data-raw-state="' + esc(fan.state) + '"><circle cx="' + x + '" cy="116" r="29"/><g class="fan-blades" transform="rotate(0 ' + x + ' 116)"><path d="M' + x + ' 112 C' + (x + 7) + ' 91 ' + (x + 25) + ' 91 ' + (x + 23) + ' 105 C' + (x + 21) + ' 119 ' + (x + 7) + ' 120 ' + x + ' 120Z"/><path d="M' + (x + 3) + ' 118 C' + (x - 9) + ' 128 ' + (x - 3) + ' 146 ' + (x + 9) + ' 139 C' + (x + 21) + ' 132 ' + (x + 14) + ' 119 ' + (x + 3) + ' 118Z"/><path d="M' + (x - 4) + ' 116 C' + (x - 19) + ' 113 ' + (x - 27) + ' 128 ' + (x - 15) + ' 136 C' + (x - 3) + ' 143 ' + (x + 5) + ' 127 ' + (x - 4) + ' 116Z"/><circle class="fan-hub" cx="' + x + '" cy="116" r="5"/></g><text class="svg-label" x="' + x + '" y="166">' + esc(fan.label) +
          '</text><text class="svg-sub state-' + esc(fan.state) + '" data-raw-state="' + esc(fan.state) + '" x="' + x + '" y="183">' + esc(stateLabel(fan.state)) + '</text></g>';
      }).join('') + louverShape(vm.louvers[0], 26) + louverShape(vm.louvers[1], 198) + '</svg></div>';
  }
  // Cờ cấp hệ thống: không suy ra quạt/bơm nào lỗi.
  function systemFlags() {
    var names = {equipmentFaultActive: 'Lỗi thiết bị tổng', externalHighTemperatureAlarm: 'Thermostat nhiệt độ cao'};
    return '<div class="system-flags" aria-label="Cờ trạng thái cấp hệ thống">' + vm.systemFlags.map(function (flag) {
      return '<span class="system-flag flag-' + esc(flag.value) + '" data-raw-state="' + esc(flag.value) + '"><small>' + esc(names[flag.key]) + '</small><b>' + esc(stateLabel(flag.value)) + '</b></span>';
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
  function selectedBarn() {
    if (vm.__selectedBarnId) return vm.barns.filter(function (barn) { return barn.id === vm.__selectedBarnId; })[0] || null;
    return vm.barns.filter(function (barn) { return barn.label === vm.scope.selectedBarn; })[0] || vm.barns[0] || null;
  }
  function sampleBarnId() {
    var barn = vm.barns.filter(function (item) { return item.label === vm.scope.selectedBarn; })[0] || vm.barns[0] || {};
    return barn.id;
  }
  function selectedBarnNotice(barn, destination) {
    destination = destination || 'chi tiết giám sát';
    if (!barn) return '<section class="view"><section class="panel selected-barn-context"><div class="panel__head"><div><p class="eyebrow">NHÀ ĐƯỢC CHỌN</p><h2>Không tìm thấy nhà</h2><p>Mã nhà được chọn không có trong dữ liệu minh họa này.</p></div></div><div class="notice compact-notice">Hãy chọn nhà mẫu để xem thông tin chi tiết minh họa.</div><a href="#vent_detail" data-nav="vent_detail" data-barn-id="' + esc(sampleBarnId()) + '" class="text-link">Xem nhà mẫu ND2-1 →</a></section>' + footer() + '</section>';
    return '<section class="view"><section class="panel selected-barn-context"><div class="panel__head"><div><p class="eyebrow">NHÀ ĐƯỢC CHỌN · ' + identityTag(barn) + '</p><h2>' + esc(barn.label) + '</h2><p>Nhà này mới có thông tin tóm tắt minh họa. Chưa có dữ liệu chi tiết để hiển thị.</p></div>' +
      '<span class="status-' + esc(barn.connectivity) + '" data-raw-state="' + esc(barn.connectivity) + '">' + esc(stateLabel(barn.connectivity)) + '</span></div><div class="barn-context-grid">' +
      '<div><small>Độ tươi dữ liệu</small><b class="quality-' + esc(barn.freshness) + '" data-raw-state="' + esc(barn.freshness) + '">' + esc(stateLabel(barn.freshness)) + '</b></div><div><small>Chế độ</small><b>' + esc(barn.mode) + '</b></div><div><small>Cấp hiển thị</small><b>' + (isMissing(barn.stage) ? '--' : esc(barn.stage)) + '</b></div><div><small>Cảnh báo</small><b class="status-' + esc(barn.alarm) + '" data-raw-state="' + esc(barn.alarm) + '">' + esc(stateLabel(barn.alarm)) + '</b></div></div>' +
      '<div class="notice compact-notice">Nhà này mới có thông tin tóm tắt minh họa. Chưa có dữ liệu chi tiết để hiển thị ' + esc(destination) + '.</div><div class="context-links"><a href="#vent_detail" data-nav="vent_detail" data-barn-id="' + esc(sampleBarnId()) + '" class="text-link">Xem nhà mẫu ND2-1 →</a><a href="#default" data-nav="default" class="text-link">Quay lại toàn trại</a></div></section>' + footer() + '</section>';
  }
  function detail() {
    var barn = selectedBarn();
    if (!barn || barn.label !== vm.scope.selectedBarn) return selectedBarnNotice(barn);
    var quality = metric('dataQuality');
    return '<section class="view"><div class="kpi-grid">' + kpi('Nhiệt độ trung bình', 'indoorTemperatureAvg', '°') +
      kpi('Nhiệt độ ngoài trời', 'outdoorTemperature', '°') + kpi('Nhiệt độ cảm nhận', 'perceivedTemperature', '≈') +
      kpi('Độ ẩm trong nhà', 'relativeHumidity', '%') + '</div><div class="detail-layout"><section class="panel detail-main">' +
      '<div class="panel__head"><div><h2>Giám sát nhà ' + esc(vm.scope.selectedBarn) + '</h2><p>Sơ đồ chỉ xem · dữ liệu minh họa</p></div>' +
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
  function historyDomain(keys, padding) {
    var values = vm.history.reduce(function (all, row) { return all.concat(keys.map(function (key) { return row[key]; })); }, []).filter(function (item) { return typeof item === 'number'; });
    if (!values.length) return {min: 0, max: 1};
    var min = Math.min.apply(null, values), max = Math.max.apply(null, values), range = max - min || 1;
    return {min: Math.floor((min - range * padding) * 2) / 2, max: Math.ceil((max + range * padding) * 2) / 2};
  }
  function seriesPath(key, domain) {
    var values = vm.history.map(function (row) { return row[key]; });
    var penDown = false, step = (chartWidth - 100) / Math.max(values.length - 1, 1);
    return values.map(function (item, index) {
      if (typeof item !== 'number') { penDown = false; return ''; }
      var x = 55 + index * step;
      var y = 245 - ((item - domain.min) / (domain.max - domain.min || 1)) * 175;
      var command = penDown ? 'L' : 'M'; penDown = true;
      return command + x.toFixed(1) + ' ' + y.toFixed(1);
    }).join(' ');
  }
  function samplePoints(tempDomain, humidityDomain) {
    var series = [{key:'indoorTemperatureAvg', domain:tempDomain, color:'#00d4e0', label:'Nhiệt độ trong nhà', unit:'°C'}, {key:'outdoorTemperature', domain:tempDomain, color:'#ffc857', label:'Nhiệt độ ngoài trời', unit:'°C'}, {key:'perceivedTemperature', domain:tempDomain, color:'#ff8fcf', label:'Nhiệt độ cảm nhận', unit:'°C'}, {key:'relativeHumidity', domain:humidityDomain, color:'#6aa9ff', label:'Độ ẩm', unit:'%RH'}];
    var step = (chartWidth - 100) / Math.max(vm.history.length - 1, 1);
    return vm.history.map(function (row, index) {
      var x = 55 + index * step, details = series.filter(function (item) { return typeof row[item.key] === 'number'; }).map(function (item) { return item.label + ': ' + row[item.key] + ' ' + item.unit; });
      if (!details.length) return '';
      var label = new Date(row.ts).toLocaleString('vi-VN') + ' · ' + details.join(' · ');
      return '<g class="chart-sample" tabindex="0" role="img" aria-label="' + esc(label) + '"><title>' + esc(label) + '</title>' + series.map(function (item) {
        if (typeof row[item.key] !== 'number') return '';
        var y = 245 - ((row[item.key] - item.domain.min) / (item.domain.max - item.domain.min || 1)) * 175;
        return '<circle class="chart-point" cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="4" fill="' + item.color + '"/>';
      }).join('') + '</g>';
    }).join('');
  }
  function axisLabels(domain, side, unit) {
    return [0, 1, 2, 3].map(function (index) {
      var y = 245 - index * (175 / 3), value = domain.min + (domain.max - domain.min) * index / 3;
      return '<text class="axis-label axis-' + side + '" x="' + (side === 'left' ? 46 : chartWidth - 37) + '" y="' + (y + 4) + '">' + esc(value.toFixed(1).replace(/\.0$/, '') + unit) + '</text>';
    }).join('');
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
    var barn = selectedBarn();
    if (!barn || barn.label !== vm.scope.selectedBarn) return selectedBarnNotice(barn, 'lịch sử môi trường');
    if (!vm.history.length) return '<section class="view"><section class="panel"><h2>Lịch sử môi trường</h2><p class="notice">Chưa có mẫu lịch sử. Không thay dữ liệu thiếu bằng 0.</p></section>' + footer() + '</section>';
    var tempDomain = historyDomain(['indoorTemperatureAvg', 'outdoorTemperature', 'perceivedTemperature'], .12);
    var humidityDomain = historyDomain(['relativeHumidity'], .25);
    var first = vm.history[0], last = vm.history[vm.history.length - 1];
    return '<section class="view"><section class="panel"><div class="panel__head"><div><h2>Lịch sử môi trường · 6 giờ</h2>' +
      '<p>Ba đường nhiệt độ dùng cùng trục °C bên trái; %RH dùng trục riêng bên phải. Điểm thiếu tạo khoảng trống.</p></div><span class="muted">°C ↔ %RH</span></div><div class="legend">' +
      '<span><i style="background:#00d4e0"></i>Trong nhà</span><span><i style="background:#ffc857"></i>Ngoài trời</span>' +
      '<span><i style="background:#ff8fcf"></i>Cảm nhận</span><span><i style="background:#6aa9ff"></i>Độ ẩm</span></div><div class="chart-wrap">' +
      '<svg class="chart" viewBox="0 0 ' + chartWidth + ' 280" role="img" aria-label="Biểu đồ nhiệt độ và độ ẩm trong sáu giờ"><path class="grid" d="' + [70,128,187,245].map(function(y){return 'M55 ' + y + 'H' + (chartWidth - 45);}).join('') + 'M55 45V245M' + (chartWidth - 45) + ' 45V245"/>' +
      axisLabels(tempDomain, 'left', '°C') + axisLabels(humidityDomain, 'right', '%') +
      '<path class="inside" d="' + seriesPath('indoorTemperatureAvg', tempDomain) + '"/><path class="outside" d="' + seriesPath('outdoorTemperature', tempDomain) + '"/>' +
      '<path class="perceived" d="' + seriesPath('perceivedTemperature', tempDomain) + '"/><path class="humidity" d="' + seriesPath('relativeHumidity', humidityDomain) + '"/>' +
      samplePoints(tempDomain, humidityDomain) +
      '<text x="55" y="266">' + esc(new Date(first.ts).toLocaleTimeString('vi-VN', {hour:'2-digit',minute:'2-digit'})) + '</text><text x="' + (chartWidth - 95) + '" y="266">' + esc(new Date(last.ts).toLocaleTimeString('vi-VN', {hour:'2-digit',minute:'2-digit'})) + '</text></svg></div></section><section class="panel table-wrap env-table">' +
      '<table class="data-table"><thead><tr><th>Thời gian</th><th>Nhiệt độ trong</th><th>Nhiệt độ ngoài</th><th>Nhiệt độ cảm nhận</th><th>Độ ẩm</th><th>Chất lượng</th></tr></thead><tbody>' +
      vm.history.slice().reverse().map(function (row) { return '<tr><td>' + new Date(row.ts).toLocaleString('vi-VN') + '</td><td>' + historyValue(row.indoorTemperatureAvg, '°C') +
        '</td><td>' + historyValue(row.outdoorTemperature, '°C') + '</td><td>' + historyValue(row.perceivedTemperature, '°C') + '</td><td>' +
        historyValue(row.relativeHumidity, '%RH') + '</td><td><span class="pill quality-' + historyQualityClass(row.quality) + '">' + esc(row.quality) + '</span></td></tr>'; }).join('') +
      '</tbody></table></section>' + airWater() + footer() + '</section>';
  }
  function alarms() {
    return '<section class="view"><section class="panel"><div class="panel__head"><div><h2>Cảnh báo & lịch sử</h2><p>Phạm vi toàn trại trong dữ liệu minh họa · chỉ xem; không có thao tác vòng đời. PLC = cờ quy trình/phần cứng; PLATFORM = kết nối/độ tươi dữ liệu.</p></div></div>' +
      '<label class="local-filter"><span>Lọc cảnh báo</span><input type="search" data-filter-input="alarm" placeholder="Mức, loại hoặc đối tượng" autocomplete="off"></label><div class="table-wrap"><table class="data-table"><thead><tr><th>Mức</th><th>Loại / nội dung</th><th>Nguồn</th><th>Đối tượng</th><th>Thời gian</th><th>Trạng thái</th></tr></thead><tbody data-filter-list="alarm">' +
      vm.alarms.map(function (alarm) { return '<tr data-filter-text="' + esc([alarm.severity, alarm.type, alarm.message, alarm.source, alarm.originator, alarm.status].join(' ').toLowerCase()) + '"><td><span class="pill status-' + alarm.severity + '" data-raw-state="' + esc(alarm.severity) + '">' + esc(stateLabel(alarm.severity)) + '</span></td><td><b>' + esc(alarm.type) +
        '</b><br><span class="muted">' + esc(alarm.message) + '</span></td><td>' + sourceTag(alarm) + '</td><td>' + esc(alarm.originator) + '</td><td>' + new Date(alarm.created).toLocaleString('vi-VN') +
        '</td><td data-raw-state="' + esc(alarm.status) + '">' + esc(stateLabel(alarm.status)) + '</td></tr>'; }).join('') + '</tbody></table></div><p class="filter-empty" data-filter-empty="alarm" hidden>Không có cảnh báo phù hợp.</p></section><p class="demo-limit">Dữ liệu minh họa · phạm vi, thời hạn lưu và xuất dữ liệu thực tế chưa được xác minh.</p>' + footer() + '</section>';
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
    var barn = selectedBarn();
    if (!barn || barn.label !== vm.scope.selectedBarn) return selectedBarnNotice(barn, 'cài đặt bộ điều khiển');
    var total = vm.settings.reduce(function (sum, group) { return sum + group.count; }, 0);
    return '<section class="view"><section class="panel"><div class="panel__head"><div><h2>Cài đặt bộ điều khiển</h2>' +
      '<p>Chỉ xem · ' + total + ' thông số trong mẫu dữ liệu v' + esc(vm.contractVersion) + ' · `--` = chưa có dữ liệu PLC · không ghi tham số</p></div></div>' +
      '<label class="local-filter"><span>Tìm thông số</span><input type="search" data-filter-input="settings" placeholder="Tên nhóm hoặc thông số" autocomplete="off"></label><nav class="settings-index" aria-label="Nhóm cài đặt">' + vm.settings.map(function (group, index) {
        return '<a href="#' + settingsGroupId(index) + '" data-scroll="' + settingsGroupId(index) + '">' + esc(group.name.replace('CÀI ĐẶT - ', '')) + ' <small>' + group.count + '</small></a>';
    }).join('') + '</nav></section><div data-filter-list="settings">' + vm.settings.map(settingsGroup).join('') + '</div><p class="filter-empty" data-filter-empty="settings" hidden>Không tìm thấy nhóm cài đặt phù hợp.</p>' + footer() + '</section>';
  }
  function footer() { return '<footer class="footer"><span>Giám sát chỉ xem · Bản minh họa ' + esc(vm.fixtureVersion) + ' · Mẫu dữ liệu v' + esc(vm.contractVersion) + '</span><span>Sinh lúc ' + new Date(vm.generatedAt).toLocaleString('vi-VN') + '</span></footer>'; }
  // Điều hướng đi qua navigate(): bản standalone đổi hash, ThingsBoard gọi stateController.
  function applyLocalFilter(container, kind, query) {
    var list = container.querySelector('[data-filter-list="' + kind + '"]');
    if (!list) return;
    var needle = query.trim().toLocaleLowerCase('vi-VN'), items;
    if (kind === 'settings') items = list.querySelectorAll('.settings-group');
    else items = list.querySelectorAll('[data-filter-text]');
    var visible = 0;
    Array.prototype.forEach.call(items, function (item) {
      var haystack = (item.getAttribute('data-filter-text') || item.textContent || '').toLocaleLowerCase('vi-VN');
      var match = !needle || haystack.indexOf(needle) >= 0;
      item.hidden = !match;
      if (match) visible += 1;
    });
    var empty = container.querySelector('[data-filter-empty="' + kind + '"]');
    if (empty) empty.hidden = visible > 0;
  }
  function render(container, viewModel, state, navigate, stateParams) {
    vm = viewModel;
    chartWidth = Math.max(720, container.clientWidth - 40);
    state = normalizeState(state);
    if (stateParams && stateParams.barnId) vm.__selectedBarnId = stateParams.barnId;
    if (!vm.__selectedBarnId) vm.__selectedBarnId = (vm.barns[0] || {}).id;
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
        var barnId = target.getAttribute('data-barn-id');
        if (barnId) vm.__selectedBarnId = barnId;
        // Giữ ngữ cảnh nhà qua mọi state; thao tác ở card mới thay đổi barnId.
        container.__ventNavigate(normalizeState(target.getAttribute('data-nav')), {barnId: vm.__selectedBarnId});
      });
      container.addEventListener('input', function (event) {
        var input = event.target.closest('[data-filter-input]');
        if (!input || !container.contains(input)) return;
        applyLocalFilter(container, input.getAttribute('data-filter-input'), input.value);
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
    var parts = id.split('?'), params = {}, query = parts[1] || '';
    query.split('&').forEach(function (pair) { var chunks = pair.split('='); if (chunks[0] === 'barnId' && chunks[1]) params.barnId = decodeURIComponent(chunks[1]); });
    render(app, data, parts[0] || "default", function (next, nextParams) { location.hash = next + (nextParams && nextParams.barnId ? '?barnId=' + encodeURIComponent(nextParams.barnId) : ''); }, params);
  }
  new root.VentilationAdapter.FixtureSource('../fixtures/ventilation/demo.json').load().then(function (data) {
    renderFromHash(data);
    window.addEventListener('hashchange', function () { renderFromHash(data); });
    window.addEventListener('resize', function () { if (location.hash.indexOf('vent_history') >= 0) renderFromHash(data); });
  }).catch(function (error) { app.innerHTML = '<p class="error">Không nạp được dữ liệu minh họa: ' + esc(error.message) + '</p>'; });
}(window));
