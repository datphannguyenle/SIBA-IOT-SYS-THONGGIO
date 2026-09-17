(function (root) {
  "use strict";
  var QUALITY = ["CURRENT", "STALE", "OFFLINE", "UNKNOWN"];
  function safeMetric(metric) {
    metric = metric || {};
    var quality = QUALITY.indexOf(metric.quality) >= 0 ? metric.quality : "UNKNOWN";
    return { value: metric.value === undefined ? null : metric.value, unit: metric.unit || "", quality: quality, ts: metric.ts || null };
  }
  function equipment(latest, prefix, count) {
    var rows = [];
    for (var i = 1; i <= count; i += 1) {
      var key = prefix + "_" + String(i).padStart(2, "0") + "_status";
      var metric = safeMetric(latest[key]);
      rows.push({ key: key, label: (prefix === "fan" ? "Quạt " : "Bơm ") + String(i).padStart(2, "0"), state: metric.value || "UNKNOWN", quality: metric.quality });
    }
    return rows;
  }
  function createViewModel(raw) {
    if (!raw || raw.demo !== true) throw new Error("Fixture source must be explicitly marked demo");
    var latest = raw.latest || {};
    var canonical = {};
    Object.keys(latest).forEach(function (key) { canonical[key] = safeMetric(latest[key]); });
    return {
      source: "fixture", demo: true, badgeLabel: raw.badgeLabel || "DEMO DATA", fixtureVersion: raw.fixtureVersion,
      generatedAt: raw.generatedAt, scope: raw.scope || {}, summary: raw.summary || {},
      barns: (raw.barns || []).map(function (b) { return Object.assign({}, b); }),
      metrics: canonical,
      equipment: equipment(latest, "fan", 6).concat(equipment(latest, "pump", 2)),
      louvers: [
        Object.assign({key:"roof_louver_position",label:"Cửa chớp trần"}, safeMetric(latest.roof_louver_position)),
        Object.assign({key:"side_louver_position",label:"Cửa chớp hông"}, safeMetric(latest.side_louver_position))
      ],
      history: (raw.history || []).map(function (row) { return Object.assign({}, row); }),
      alarms: (raw.alarms || []).map(function (row) { return Object.assign({}, row); })
    };
  }
  function FixtureSource(url) { this.url = url; }
  FixtureSource.prototype.load = function () {
    // The repository demo is intentionally deterministic: load its local fixture before
    // first paint so browser screenshots and stakeholder reviews never capture a spinner.
    // This adapter is not the future ThingsBoard transport.
    try {
      var request = new XMLHttpRequest();
      request.open("GET", this.url, false);
      request.send(null);
      if (request.status !== 200) throw new Error("Fixture load failed");
      return Promise.resolve(createViewModel(JSON.parse(request.responseText)));
    } catch (error) { return Promise.reject(error); }
  };
  function ThingsBoardSource() {}
  ThingsBoardSource.prototype.load = function () { return Promise.reject(new Error("ThingsBoard source is intentionally unconfigured until VENT-002 is implementation-ready")); };
  root.VentilationAdapter = { createViewModel:createViewModel, FixtureSource:FixtureSource, ThingsBoardSource:ThingsBoardSource };
}(window));
