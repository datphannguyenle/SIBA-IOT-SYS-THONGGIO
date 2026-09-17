(function (root) {
  "use strict";
  var QUALITY = ["CURRENT", "STALE", "OFFLINE", "UNKNOWN"];
  var BARN_IDENTITY = ["PILOT", "LIVE_BARN_SIMULATED_STATE", "SYNTHETIC"];
  var CANONICAL_MAP = {
    indoorTemperature01: "temperature_indoor_01", indoorTemperature02: "temperature_indoor_02",
    indoorTemperatureAvg: "temperature_indoor", outdoorTemperature: "temperature_outdoor",
    perceivedTemperature: "temperature_feel", relativeHumidity: "humidity",
    airSpeed: "air_speed", airFlow: "air_flow", waterConsumptionTotal: "water_consumption",
    operatingMode: "operation_mode", fanControlMode: "fan_control_mode",
    fanStage: "ventilation_stage", stageCount: "ventilation_stage_count",
    controllerOnline: "controller_online", dataQuality: "data_quality",
    roofInletPosition: "roof_louver_position", sideInletPosition: "side_louver_position"
  };
  var HISTORY_MAP = {
    indoorTemperatureAvg: "temperature_indoor", outdoorTemperature: "temperature_outdoor",
    perceivedTemperature: "temperature_feel", relativeHumidity: "humidity"
  };
  (function addEquipmentKeys() {
    for (var i = 1; i <= 6; i += 1) {
      var fan = String(i).padStart(2, "0");
      CANONICAL_MAP["fan" + fan + "Run"] = "fan_" + fan + "_run";
      CANONICAL_MAP["fan" + fan + "Fault"] = "fan_" + fan + "_fault";
    }
    for (var p = 1; p <= 2; p += 1) {
      var pump = String(p).padStart(2, "0");
      CANONICAL_MAP["coolingPump" + pump + "Run"] = "pump_" + pump + "_run";
      CANONICAL_MAP["coolingPump" + pump + "Fault"] = "pump_" + pump + "_fault";
    }
  }());
  function isMissing(value) { return value === null || value === undefined; }
  // Giữ nguyên false/0; chỉ null/undefined mới là "chưa có dữ liệu".
  function safeMetric(metric) {
    metric = metric && typeof metric === "object" ? metric : {};
    return { value: metric.value === undefined ? null : metric.value,
      unit: isMissing(metric.unit) ? "" : metric.unit,
      quality: QUALITY.indexOf(metric.quality) >= 0 ? metric.quality : "UNKNOWN",
      ts: metric.ts === undefined ? null : metric.ts };
  }
  function combinedQuality(runMetric, faultMetric) {
    var qualities = [runMetric.quality, faultMetric.quality];
    if (qualities.indexOf("OFFLINE") >= 0) return "OFFLINE";
    if (qualities.indexOf("STALE") >= 0) return "STALE";
    if (qualities.indexOf("UNKNOWN") >= 0) return "UNKNOWN";
    return "CURRENT";
  }
  // Suy diễn hiển thị demo; không khẳng định phản hồi vật lý đã được xác minh.
  function equipmentState(runMetric, faultMetric) {
    if (faultMetric.value === true) return "FAULT";
    if (faultMetric.value === false && runMetric.value === true) return "RUNNING";
    if (faultMetric.value === false && runMetric.value === false) return "STOPPED";
    return "UNKNOWN";
  }
  function equipment(metrics, canonicalPrefix, labelPrefix, count) {
    var rows = [];
    for (var i = 1; i <= count; i += 1) {
      var suffix = String(i).padStart(2, "0");
      var run = metrics[canonicalPrefix + suffix + "Run"], fault = metrics[canonicalPrefix + suffix + "Fault"];
      rows.push({ key: canonicalPrefix + suffix, label: labelPrefix + " " + suffix,
        run: run, fault: fault, state: equipmentState(run, fault),
        quality: combinedQuality(run, fault) });
    }
    return rows;
  }
  // Chỉ hiện mẫu số khi stageCount có thật; không tự suy 6/9.
  function stageDisplay(stageMetric, countMetric) {
    if (isMissing(stageMetric.value)) return "--";
    if (isMissing(countMetric.value)) return String(stageMetric.value);
    return String(stageMetric.value) + " / " + String(countMetric.value);
  }
  function controllerOnlineState(metric) {
    if (metric.value === true) return "ONLINE";
    if (metric.value === false) return "OFFLINE";
    return "UNKNOWN";
  }
  function mapHistory(row) {
    var mapped = { ts: row.ts, quality: isMissing(row.quality) ? "UNKNOWN" : row.quality };
    Object.keys(HISTORY_MAP).forEach(function (key) {
      var sample = row[HISTORY_MAP[key]];
      mapped[key] = sample === undefined ? null : sample;
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
    var latest = raw.latest || {}, metrics = {};
    Object.keys(CANONICAL_MAP).forEach(function (canonicalKey) {
      metrics[canonicalKey] = safeMetric(latest[CANONICAL_MAP[canonicalKey]]);
    });
    return { source: "fixture", demo: true, badgeLabel: raw.badgeLabel || "DEMO DATA",
      fixtureVersion: raw.fixtureVersion, generatedAt: raw.generatedAt, scope: raw.scope || {},
      summary: raw.summary || {}, barns: (raw.barns || []).map(mapBarn),
      metrics: metrics,
      controller: { online: controllerOnlineState(metrics.controllerOnline),
        stageDisplay: stageDisplay(metrics.fanStage, metrics.stageCount) },
      equipment: equipment(metrics, "fan", "Quạt", 6)
        .concat(equipment(metrics, "coolingPump", "Bơm làm mát", 2)),
      louvers: [Object.assign({key: "roofInletPosition", label: "Cửa chớp trần"}, metrics.roofInletPosition),
        Object.assign({key: "sideInletPosition", label: "Cửa chớp hông"}, metrics.sideInletPosition)],
      history: (raw.history || []).map(mapHistory),
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
  root.VentilationAdapter = { createViewModel: createViewModel, equipmentState: equipmentState,
    stageDisplay: stageDisplay, safeMetric: safeMetric, mapHistory: mapHistory,
    CANONICAL_MAP: CANONICAL_MAP, FixtureSource: FixtureSource, ThingsBoardSource: ThingsBoardSource };
}(window));
