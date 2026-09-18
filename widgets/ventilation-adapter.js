(function (root) {
  "use strict";
  // VENT-007: raw fixture/ThingsBoard dùng key của Data Contract v0.3 và mã hóa PLC (uint16/float32).
  // Adapter chuyển mã sang view model chuẩn; danh sách key/nhóm/enum đến từ VentilationContract (sinh tự động).
  var QUALITY = ["CURRENT", "STALE", "OFFLINE", "UNKNOWN"];
  var BARN_IDENTITY = ["PILOT", "LIVE_BARN_SIMULATED_STATE", "SYNTHETIC"];
  var UNKNOWN = "UNKNOWN", NOT_CONFIGURED = "NOT_CONFIGURED";
  var RUN_KEYS = ["fan01Run", "fan02Run", "fan03Run", "fan04Run", "fan05Run", "fan06Run", "coolingPump01Run", "coolingPump02Run"];
  var FLAG_KEYS = ["equipmentFaultActive", "externalHighTemperatureAlarm", "temperatureLowAlarmActive",
    "temperatureHighAlarmActive", "perceivedTemperatureLowAlarmActive", "perceivedTemperatureHighAlarmActive"];
  var HISTORY_KEYS = ["indoorTemperatureAvg", "outdoorTemperature", "perceivedTemperature", "relativeHumidity",
    "airSpeed", "airFlow", "waterConsumptionTotal"];
  var SLOT_PATTERN = /^(temperatureProfile|perceivedProfile|stage|fan|coolingPump)(\d\d)([A-Z]\w*)$/;
  var SLOT_ROW_LABEL = {temperatureProfile: "Slot", perceivedProfile: "Slot", stage: "Slot", fan: "Quạt", coolingPump: "Bơm"};
  var FIELD_LABEL_REWRITE = [
    [/^chọn quạt (\d)$/, "Quạt $1"], [/^tần số quạt\/VFD kênh (\d)$/, "VFD kênh $1"],
    [/^góc\/vị trí cửa chớp (trần|hông)$/, "Cửa chớp $1"], [/^thời gian chạy.*$/, "Chạy"], [/^thời gian dừng.*$/, "Dừng"]
  ];

  function contract() {
    var c = root.VentilationContract;
    if (!c || c.version !== "0.3") throw new Error("VentilationContract v0.3 is required");
    return c;
  }
  function isMissing(value) { return value === null || value === undefined; }
  function isInteger(value) { return typeof value === "number" && isFinite(value) && Math.floor(value) === value; }
  function variableIndex(c) {
    var index = {};
    c.variables.forEach(function (row) {
      index[row[0]] = {key: row[0], group: row[1], role: row[2], status: row[3], label: row[4], unit: row[5] || "", type: row[6]};
    });
    return index;
  }
  function classify(c, variable) {
    if (variable.role === "setting") return "SETTINGS";
    if (variable.status === "OPTIONAL") return "OPTIONAL";
    var primary = c.organization.overview_or_detail_primary.concat(c.organization.equipment_status);
    return primary.indexOf(variable.key) >= 0 ? "PRIMARY_MONITORING" : "SECONDARY_MONITORING";
  }
  function safeQuality(quality) { return QUALITY.indexOf(quality) >= 0 ? quality : UNKNOWN; }
  function codeLookup(table, raw) {
    if (!isInteger(raw)) return UNKNOWN;
    return Object.prototype.hasOwnProperty.call(table, String(raw)) ? table[String(raw)] : UNKNOWN;
  }
  // Giải mã một giá trị raw theo contract. Không bao giờ ép null thành 0 hay 0 thành null.
  function decode(c, variable, raw) {
    var enumKey = c.enums[variable.key] ? variable.key : c.settingEnumAliases[variable.key];
    if (enumKey) return isMissing(raw) ? null : codeLookup(c.enums[enumKey], raw);
    if (RUN_KEYS.indexOf(variable.key) >= 0) return isMissing(raw) ? UNKNOWN : codeLookup(c.equipmentRunCodes, raw);
    if (FLAG_KEYS.indexOf(variable.key) >= 0) return isMissing(raw) ? UNKNOWN : codeLookup(c.flagDisplayCodes, raw);
    if (variable.type === "uint16") return isInteger(raw) && raw >= 0 && raw <= 65535 ? raw : null;
    return typeof raw === "number" && isFinite(raw) ? raw : null;
  }
  function buildMetric(c, variable, sample, notConfigured) {
    sample = sample && typeof sample === "object" ? sample : {};
    var configured = notConfigured.indexOf(variable.key) < 0;
    var decoded = configured ? decode(c, variable, sample.value) : null;
    var stateful = RUN_KEYS.indexOf(variable.key) >= 0 || FLAG_KEYS.indexOf(variable.key) >= 0;
    return { key: variable.key, label: variable.label, unit: variable.unit, group: variable.group,
      classification: classify(c, variable), contractStatus: variable.status, configured: configured,
      raw: configured && sample.value !== undefined ? sample.value : null,
      value: configured ? decoded : (stateful ? NOT_CONFIGURED : null),
      quality: configured ? safeQuality(sample.quality) : UNKNOWN,
      ts: configured && sample.ts !== undefined ? sample.ts : null };
  }
  function platformMetric(key, sample) {
    sample = sample && typeof sample === "object" ? sample : {};
    return { key: key, classification: "PLATFORM_DERIVED", configured: true, unit: "",
      value: sample.value === undefined ? null : sample.value, quality: safeQuality(sample.quality),
      ts: sample.ts === undefined ? null : sample.ts };
  }
  function equipmentLabel(key) {
    var m = /^(fan|coolingPump)(\d\d)Run$/.exec(key);
    return (m[1] === "fan" ? "Quạt " : "Bơm làm mát ") + m[2];
  }
  function controllerOnlineState(metric) {
    if (metric.value === true) return "ONLINE";
    if (metric.value === false) return "OFFLINE";
    return UNKNOWN;
  }
  // Chỉ hiện cấp hiện tại; không có mẫu số, không suy số cấp từ slot cấu hình.
  function stageDisplay(stageMetric) {
    return stageMetric && isInteger(stageMetric.value) ? String(stageMetric.value) : "--";
  }
  function fieldLabel(label) {
    var text = label.indexOf(" - ") >= 0 ? label.slice(label.lastIndexOf(" - ") + 3) : label;
    FIELD_LABEL_REWRITE.forEach(function (rule) { text = text.replace(rule[0], rule[1]); });
    return text.charAt(0).toUpperCase() + text.slice(1);
  }
  function settingsGroups(c, index, rawSettings, notConfigured) {
    return c.groups.filter(function (g) { return g.role === "setting"; }).map(function (g) {
      var items = c.variables.filter(function (row) { return row[1] === g.name; }).map(function (row) {
        var metric = buildMetric(c, index[row[0]], rawSettings[row[0]], notConfigured);
        return metric;
      });
      var matrices = [], byPrefix = {}, scalars = [];
      items.forEach(function (item) {
        var m = SLOT_PATTERN.exec(item.key);
        if (!m) { scalars.push(item); return; }
        var matrix = byPrefix[m[1]];
        if (!matrix) {
          matrix = byPrefix[m[1]] = {prefix: m[1], rowLabel: SLOT_ROW_LABEL[m[1]], slots: [], fields: [], cells: {}};
          matrices.push(matrix);
        }
        if (matrix.slots.indexOf(m[2]) < 0) matrix.slots.push(m[2]);
        var field = matrix.fields.filter(function (f) { return f.id === m[3]; })[0];
        if (!field) {
          field = {id: m[3], label: fieldLabel(item.label), unit: item.unit, optional: item.contractStatus === "OPTIONAL"};
          matrix.fields.push(field);
        }
        matrix.cells[m[2] + ":" + m[3]] = item;
      });
      return {name: g.name, count: items.length, items: items, scalars: scalars, matrices: matrices};
    });
  }
  function mapHistory(row) {
    var mapped = { ts: row.ts, quality: isMissing(row.quality) ? UNKNOWN : row.quality };
    HISTORY_KEYS.forEach(function (key) {
      var sample = row[key];
      mapped[key] = typeof sample === "number" && isFinite(sample) ? sample : null;
    });
    return mapped;
  }
  // Nhà không khai báo danh tính rõ ràng bị coi là tổng hợp, không bao giờ là nhà live.
  function mapBarn(barn) {
    var copy = Object.assign({}, barn);
    if (BARN_IDENTITY.indexOf(copy.identity) < 0) copy.identity = "SYNTHETIC";
    copy.synthetic = copy.identity === "SYNTHETIC";
    return copy;
  }
  function createViewModel(raw) {
    if (!raw || raw.demo !== true) throw new Error("Fixture source must be explicitly marked demo");
    var c = contract();
    if (!raw.contract || raw.contract.version !== c.version) throw new Error("Fixture contract version must be " + c.version);
    var index = variableIndex(c), latest = raw.latest || {}, platform = raw.platform || {};
    var notConfigured = ((raw.mapping || {}).notConfigured || []).slice();
    var unknownKeys = Object.keys(latest).filter(function (key) { return !index[key] || index[key].role === "setting"; })
      .concat(notConfigured.filter(function (key) { return !index[key]; }));
    var metrics = {};
    c.variables.forEach(function (row) {
      if (row[2] !== "setting") metrics[row[0]] = buildMetric(c, index[row[0]], latest[row[0]], notConfigured);
    });
    c.platformDerived.forEach(function (key) { metrics[key] = platformMetric(key, platform[key]); });
    return { source: "fixture", demo: true, badgeLabel: raw.badgeLabel || "DEMO DATA",
      fixtureVersion: raw.fixtureVersion, generatedAt: raw.generatedAt, contractVersion: c.version,
      scope: raw.scope || {}, summary: raw.summary || {}, barns: (raw.barns || []).map(mapBarn),
      notConfigured: notConfigured, unknownKeys: unknownKeys, metrics: metrics,
      controller: { online: controllerOnlineState(metrics.controllerOnline), stageDisplay: stageDisplay(metrics.fanStage) },
      equipment: RUN_KEYS.map(function (key) {
        var m = metrics[key];
        return { key: key, label: equipmentLabel(key), state: m.value, quality: m.quality, configured: m.configured };
      }),
      systemFlags: ["equipmentFaultActive", "externalHighTemperatureAlarm"].map(function (key) { return metrics[key]; }),
      louvers: [Object.assign({}, metrics.roofInletPosition, {label: "Cửa chớp trần"}),
        Object.assign({}, metrics.sideInletPosition, {label: "Cửa chớp hông"})],
      history: (raw.history || []).map(mapHistory),
      settings: settingsGroups(c, index, raw.settings || {}, notConfigured),
      alarms: (raw.alarms || []).map(function (alarm) { return Object.assign({}, alarm); }) };
  }
  function FixtureSource(url) { this.url = url; }
  FixtureSource.prototype.load = function () {
    try { var request = new XMLHttpRequest(); request.open("GET", this.url, false); request.send(null);
      if (request.status !== 200) throw new Error("Fixture load failed");
      return Promise.resolve(createViewModel(JSON.parse(request.responseText)));
    } catch (error) { return Promise.reject(error); }
  };
  function ThingsBoardSource() {}
  ThingsBoardSource.prototype.load = function () { return Promise.reject(new Error("ThingsBoard source is intentionally unconfigured until VENT-002 is implementation-ready")); };
  root.VentilationAdapter = { createViewModel: createViewModel, stageDisplay: stageDisplay, mapHistory: mapHistory,
    RUN_KEYS: RUN_KEYS, FLAG_KEYS: FLAG_KEYS, HISTORY_KEYS: HISTORY_KEYS,
    FixtureSource: FixtureSource, ThingsBoardSource: ThingsBoardSource };
}(window));
