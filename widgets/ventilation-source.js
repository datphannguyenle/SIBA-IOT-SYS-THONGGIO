(function (root) {
  "use strict";
  // VENT-010: boundary between an untrusted TB subscription and the v0.3 semantic VM.
  // It never assumes a PLC key, cadence, entity, or connectivity state.
  var PLATFORM = ["controllerOnline", "dataQuality"];

  function missing(value) { return value === null || value === undefined || value === ""; }
  function numberOrNull(value) {
    if (missing(value)) return null;
    if (typeof value === "number") return isFinite(value) ? value : null;
    if (typeof value !== "string" || !value.trim()) return null;
    var parsed = Number(value);
    return isFinite(parsed) ? parsed : null;
  }
  function timestamp(value) {
    if (typeof value === "number" && isFinite(value)) return value;
    if (typeof value === "string" && value) {
      var parsed = Date.parse(value);
      return isFinite(parsed) ? parsed : null;
    }
    return null;
  }
  function sample(value, ts) {
    return {value: numberOrNull(value), rawValue: missing(value) ? null : value, ts: timestamp(ts)};
  }
  function keyOf(row) {
    return row && row.dataKey && (row.dataKey.name || row.dataKey.label) || row && (row.key || row.name);
  }
  function identityText(value) {
    if (!value) return null;
    if (typeof value === "string") return value;
    if (typeof value === "object") return value.id || value.entityId || null;
    return null;
  }
  // entityId của TB là object {entityType, id}; phải lấy id dạng chuỗi, nếu không mọi nhà gom thành một.
  function rowIdentity(row) {
    var ds = row && (row.datasource || row.dataSource) || {};
    return identityText(ds.entityId) || ds.entityName || identityText(ds.entity && ds.entity.id) ||
      (ds.entity && ds.entity.name) || null;
  }
  function scopedRows(ctx, identity) {
    ctx = ctx || {};
    var rows = [].concat(Array.isArray(ctx.data) ? ctx.data : [], Array.isArray(ctx.latestData) ? ctx.latestData : []);
    var ids = {};
    rows.forEach(function (row) { var id = rowIdentity(row); if (id) ids[id] = true; });
    var found = Object.keys(ids);
    if (identity) return {rows: rows.filter(function (row) { return rowIdentity(row) === identity; }),
      status: found.indexOf(identity) >= 0 ? "SELECTED" : "IDENTITY_NOT_FOUND", entityIds: found};
    if (found.length > 1) return {rows: [], status: "MULTIPLE_ENTITIES_REJECTED", entityIds: found};
    return {rows: rows, status: found.length ? "SINGLE_ENTITY" : "ENTITY_UNKNOWN", entityIds: found};
  }
  function addRows(target, rows) {
    if (!Array.isArray(rows)) return;
    rows.forEach(function (row) {
      var key = keyOf(row), data = row && row.data;
      if (!key || !Array.isArray(data) || !data.length) return;
      var point = data[data.length - 1], newest = null;
      data.forEach(function (candidate) {
        if (!Array.isArray(candidate) || timestamp(candidate[0]) === null) return;
        if (!newest || timestamp(candidate[0]) > timestamp(newest[0])) newest = candidate;
      });
      if (newest) point = newest;
      if (!Array.isArray(point)) return;
      var next = sample(point[1], point[0]), old = target[key];
      if (!old || (next.ts !== null && (old.ts === null || next.ts >= old.ts))) target[key] = next;
    });
  }
  function addObject(target, object) {
    if (!object || typeof object !== "object" || Array.isArray(object)) return;
    Object.keys(object).forEach(function (key) {
      var entry = object[key], next;
      if (Array.isArray(entry)) {
        if (!entry.length) return;
        var point = entry[entry.length - 1], newest = null;
        entry.forEach(function (candidate) {
          if (!Array.isArray(candidate) || timestamp(candidate[0]) === null) return;
          if (!newest || timestamp(candidate[0]) > timestamp(newest[0])) newest = candidate;
        });
        if (newest) point = newest;
        next = Array.isArray(point) ? sample(point[1], point[0]) : sample(point, null);
      } else if (entry && typeof entry === "object") next = sample(entry.value, entry.ts);
      else next = sample(entry, null);
      var old = target[key];
      if (!old || (next.ts !== null && (old.ts === null || next.ts >= old.ts))) target[key] = next;
    });
  }
  // Both ctx.data and ctx.latestData occur in TB widgets; select the newest point when both are present.
  function subscriptionSamples(ctx, identity) {
    var out = {};
    ctx = ctx || {};
    var scoped = scopedRows(ctx, identity);
    addRows(out, scoped.rows);
    // Object-shaped latestData has no per-row entity identity; only accept it when scope is unambiguous.
    if (!Array.isArray(ctx.latestData) && !identity && scoped.status !== "MULTIPLE_ENTITIES_REJECTED") addObject(out, ctx.latestData);
    return {samples: out, scope: scoped};
  }
  function positive(value) { return typeof value === "number" && isFinite(value) && value > 0; }
  // Danh sách nhà ở màn Tổng quan đọc NHIỀU entity; widget chi tiết vẫn giữ quy tắc một entity.
  function entityGroups(ctx) {
    var rows = [].concat(Array.isArray(ctx && ctx.data) ? ctx.data : [],
      Array.isArray(ctx && ctx.latestData) ? ctx.latestData : []);
    var groups = [], index = {};
    rows.forEach(function (row) {
      var ds = row && (row.datasource || row.dataSource) || {};
      var id = identityText(ds.entityId) || identityText(ds.entity && ds.entity.id) || ds.entityName || null;
      if (!id) return;
      var group = index[id];
      if (!group) {
        group = index[id] = {id: id, label: ds.entityLabel || ds.entityName || (ds.entity && ds.entity.name) || id,
          name: ds.entityName || null, entityType: entityTypeOf(ds), rows: []};
        groups.push(group);
      }
      group.rows.push(row);
    });
    return groups;
  }
  // Alias stateEntity của TB cần cả loại entity, không chỉ id; thiếu loại là không bind được.
  function entityTypeOf(ds) {
    var id = ds && ds.entityId;
    if (id && typeof id === "object" && id.entityType) return id.entityType;
    return ds.entityType || (ds.entity && ds.entity.id && ds.entity.id.entityType) || null;
  }
  function decodeCode(table, raw) {
    if (typeof raw !== "number" || !isFinite(raw) || Math.floor(raw) !== raw) return "UNKNOWN";
    return Object.prototype.hasOwnProperty.call(table, String(raw)) ? table[String(raw)] : "UNKNOWN";
  }
  // Chỉ xét cờ ĐÃ được khai trong keyMap; cờ chưa khai là không áp dụng, không phải "bình thường".
  function barnAlarmState(states) {
    if (states.indexOf("ACTIVE_MAJOR") >= 0) return "MAJOR";
    if (states.indexOf("ACTIVE_WARNING") >= 0) return "WARNING";
    if (!states.length || states.indexOf("UNKNOWN") >= 0) return "UNKNOWN";
    return "NONE";
  }
  // Mỗi nhà là một entity riêng; không trộn số liệu giữa các nhà và không đoán khi thiếu mapping.
  function barnsFromEntities(ctx, settings, now) {
    var c = root.VentilationContract, keyMap = settings.keyMap || {}, freshness = settings.freshnessMs || {};
    var wanted = ["fanStage", "operatingMode", "controllerOnline", "equipmentFaultActive", "externalHighTemperatureAlarm"];
    return entityGroups(ctx).map(function (group) {
      var samples = {};
      addRows(samples, group.rows);
      var invalidKeys = simulationInvalidKeys(samples, settings);
      var values = {}, numbers = {}, qualities = [];
      wanted.forEach(function (semantic) {
        var actual = keyMap[semantic];
        // Tổng quan nhiều entity cũng phải che giá trị cũ mà snapshot SIM mới
        // đánh dấu vắng mặt; nếu không card nhà sẽ giữ stage/mode của chu kỳ trước.
        var item = invalidKeys[semantic] ? null :
          (typeof actual === "string" && actual ? samples[actual] : null);
        values[semantic] = item ? item.rawValue : null;
        // TB có thể giao telemetry số dưới dạng chuỗi; mã enum/cờ phải giải trên số đã chuẩn hóa,
        // nếu không mọi nhà đều ra UNKNOWN. controllerOnline vẫn dùng giá trị thô vì nó là boolean.
        numbers[semantic] = item ? item.value : null;
        // Độ tươi chỉ xét khóa ĐO ĐƯỢC. controllerOnline lấy từ attribute `active`, mà TB chỉ
        // cập nhật mốc thời gian của nó khi trạng thái ĐỔI — tính vào đây thì mọi nhà đều "cũ".
        if (typeof actual === "string" && actual && PLATFORM.indexOf(semantic) < 0) {
          qualities.push(qualityFor(item, freshness[semantic], now));
        }
      });
      var online = platformValue("controllerOnline", values.controllerOnline);
      var alarmStates = [];
      [["equipmentFaultActive", "MAJOR"], ["externalHighTemperatureAlarm", "WARNING"]].forEach(function (pair) {
        if (typeof keyMap[pair[0]] !== "string" || !keyMap[pair[0]]) return;
        var state = numbers[pair[0]] === null ? "UNKNOWN" : decodeCode(c.flagDisplayCodes, numbers[pair[0]]);
        alarmStates.push(state === "ACTIVE" ? "ACTIVE_" + pair[1] : state);
      });
      var stage = numbers.fanStage;
      return {id: group.id, label: group.label, entityType: group.entityType,
        identity: "LIVE_ENTITY", synthetic: false,
        connectivity: online === true ? "ONLINE" : (online === false ? "OFFLINE" : "UNKNOWN"),
        freshness: qualities.indexOf("STALE") >= 0 ? "STALE" :
          (qualities.length && qualities.indexOf("UNKNOWN") < 0 ? "CURRENT" : "UNKNOWN"),
        mode: numbers.operatingMode === null ? "UNKNOWN" : decodeCode(c.enums.operatingMode, numbers.operatingMode),
        stage: typeof stage === "number" && isFinite(stage) && Math.floor(stage) === stage ? stage : null,
        alarm: barnAlarmState(alarmStates)};
    });
  }
  function barnSummary(barns) {
    // Số cảnh báo đang mở thuộc phạm vi alarm của nền tảng, không suy từ danh sách nhà.
    return {barns: barns.length, online: barns.filter(function (b) { return b.connectivity === "ONLINE"; }).length,
      attention: barns.filter(function (b) { return b.freshness !== "CURRENT" || b.alarm === "MAJOR" || b.alarm === "WARNING"; }).length,
      activeAlarms: null};
  }
  function qualityFor(item, freshnessMs, now) {
    // A timestamp without an explicitly configured and valid threshold is intentionally UNKNOWN.
    if (!item || item.rawValue === null || item.ts === null || item.ts < 0 || item.ts > now || !positive(freshnessMs)) return "UNKNOWN";
    return now - item.ts > freshnessMs ? "STALE" : "CURRENT";
  }
  function mappedKeys() {
    var c = root.VentilationContract;
    if (!c || c.version !== "0.3") throw new Error("VentilationContract v0.3 is required");
    return c.variables.map(function (row) { return row[0]; })
      .concat(c.platformDerived || PLATFORM);
  }
  function isSetting(key) {
    var c = root.VentilationContract;
    return c.variables.some(function (row) { return row[0] === key && row[2] === "setting"; });
  }
  function fixtureRows(raw) {
    var rows = [], latest = raw.latest || {}, platform = raw.platform || {};
    Object.keys(latest).forEach(function (key) { var item = latest[key] || {}; rows.push({dataKey: {name: key}, data: [[item.ts, item.value]]}); });
    Object.keys(platform).forEach(function (key) {
      if (key.charAt(0) === "_") return;
      var item = platform[key] || {}; rows.push({dataKey: {name: key}, data: [[item.ts, item.value]]});
    });
    return rows;
  }
  function historyFromRows(rows, keyMap, freshness, now) {
    var values = {}, stamps = {};
    var wanted = root.VentilationAdapter.HISTORY_KEYS || [];
    rows.forEach(function (row) {
      var actual = keyOf(row), data = row && row.data;
      if (!actual || !Array.isArray(data)) return;
      wanted.forEach(function (semantic) {
        if (keyMap[semantic] !== actual) return;
        data.forEach(function (point) {
          if (!Array.isArray(point)) return;
          var ts = timestamp(point[0]);
          if (ts === null) return;
          if (!values[ts]) values[ts] = {};
          values[ts][semantic] = numberOrNull(point[1]); stamps[ts] = true;
        });
      });
    });
    return Object.keys(stamps).map(Number).sort(function (a, b) { return a - b; }).map(function (ts) {
      var row = {ts: ts}, present = values[ts], observed = false;
      wanted.forEach(function (semantic) {
        row[semantic] = Object.prototype.hasOwnProperty.call(present, semantic) ? present[semantic] : null;
        // Mốc thời gian lịch sử vốn ở quá khứ; freshness chỉ dành cho dữ liệu mới nhất.
        observed = observed || row[semantic] !== null;
      });
      row.quality = observed ? "HISTORICAL" : "UNKNOWN";
      return row;
    });
  }
  function readableAlarmText(value, seen, depth) {
    if (missing(value)) return null;
    if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
    if (typeof value !== "object") return String(value);
    seen = seen || []; depth = depth || 0;
    if (seen.indexOf(value) >= 0) return "[tham chiếu vòng]";
    if (depth >= 3) return "[…]";
    seen.push(value);
    var text = Array.isArray(value) ? value.map(function (item) {
      return readableAlarmText(item, seen, depth + 1) || "--";
    }).join(", ") : Object.keys(value).sort().map(function (key) {
      return key + ": " + (readableAlarmText(value[key], seen, depth + 1) || "--");
    }).join(" · ");
    seen.pop();
    return text || null;
  }
  function normalizeAlarms(alarms) {
    if (!Array.isArray(alarms)) return [];
    return alarms.filter(function (alarm) { return alarm && typeof alarm === "object"; }).map(function (alarm) {
      var copy = Object.assign({}, alarm), raw = alarm.status || "UNKNOWN";
      copy.rawStatus = raw;
      copy.active = raw === "ACTIVE_ACK" || raw === "ACTIVE_UNACK";
      copy.acknowledged = raw === "ACTIVE_ACK" || raw === "CLEARED_ACK";
      copy.status = copy.active ? "ACTIVE" : (raw.indexOf("CLEARED") === 0 ? "RECOVERED" : raw);
      copy.created = alarm.createdTime !== undefined ? alarm.createdTime : (alarm.created !== undefined ? alarm.created : null);
      copy.originator = alarm.originatorName || alarm.originator || null;
      copy.message = readableAlarmText(alarm.message) || readableAlarmText(alarm.details);
      copy.source = alarm.source || "THINGSBOARD";
      return copy;
    });
  }
  function alarmSubscription(ctx, demo) {
    if (demo) return {alarms: [], status: "FIXTURE"};
    var block = ctx && ctx.defaultSubscription && ctx.defaultSubscription.alarms;
    if (block && Array.isArray(block.data)) return {alarms: normalizeAlarms(block.data), status: "LOADED"};
    // Kept only for a local fake ctx; production binding reads defaultSubscription.alarms.data above.
    if (ctx && Array.isArray(ctx.alarms)) return {alarms: normalizeAlarms(ctx.alarms), status: "LOADED"};
    return {alarms: [], status: "NOT_LOADED"};
  }
  function platformValue(key, value) {
    if (key !== "controllerOnline") return value;
    if (value === true || value === false) return value;
    if (value === "true") return true;
    if (value === "false") return false;
    return null;
  }
  function liveContext(ctx, settings) {
    var configured = settings.context && typeof settings.context === "object" ? settings.context : {};
    var params = ctx && ctx.stateController && ctx.stateController.getStateParams ? ctx.stateController.getStateParams() || {} : {};
    var selectedId = params.selectedBarnId || params.selectedBarn || params.selectedControllerId || params.selectedController ||
      params.barnId || configured.barnId || configured.controllerId || null;
    var selectedName = params.selectedBarnName || params.selectedControllerName || params.barnLabel ||
      configured.barnLabel || configured.controllerName || null;
    return {farm: configured.farm || null, area: configured.area || null, selectedBarn: selectedName,
      selectedBarnId: selectedId, selectedControllerId: configured.controllerId || params.selectedControllerId || null,
      status: (configured.farm || configured.area || selectedId || selectedName) ? "CONFIGURED" : "UNKNOWN"};
  }
  // Chỉ là provenance hiển thị; không đổi sourceMode, subscription hay dữ liệu.
  // settings.provenance: "SIM"/"DEMO"/"LIVE" hoặc {kind, label, note}.
  function sourceProvenance(settings, demo) {
    var configured = settings.provenance, value = configured && typeof configured === "object" ? configured : {kind: configured};
    var kind = typeof value.kind === "string" ? value.kind.toUpperCase() :
      (settings.simulation === true ? "SIM" : (demo ? "DEMO" : "LIVE"));
    if (["SIM", "DEMO", "LIVE"].indexOf(kind) < 0) kind = demo ? "DEMO" : "LIVE";
    var defaults = {SIM: "Dữ liệu mô phỏng", DEMO: "Dữ liệu minh họa", LIVE: "Dữ liệu trực tiếp"};
    return {kind: kind, label: typeof value.label === "string" && value.label ? value.label : defaults[kind],
      note: typeof value.note === "string" ? value.note : ""};
  }
  // VENT-011 phát simInvalidKeys cùng snapshot để phân biệt "giá trị trước đó còn lưu"
  // với một giá trị hiện tại. Metadata chỉ có hiệu lực khi instance tự nhận simulation.
  function simulationInvalidKeys(samples, settings) {
    if (settings.simulation !== true) return {};
    var key = typeof settings.invalidKeysTelemetryKey === "string" && settings.invalidKeysTelemetryKey ?
      settings.invalidKeysTelemetryKey : "simInvalidKeys";
    var sample = samples[key], raw = sample && sample.rawValue, list = raw;
    if (typeof raw === "string") {
      try { list = JSON.parse(raw); } catch (ignore) { return {}; }
    }
    if (!Array.isArray(list)) return {};
    return list.reduce(function (out, semantic) {
      if (typeof semantic === "string" && semantic) out[semantic] = true;
      return out;
    }, {});
  }
  function rawFromSubscription(ctx, settings, fixture) {
    settings = settings || {};
    var demo = settings.sourceMode === "demo";
    if (demo && (!fixture || fixture.demo !== true)) throw new Error("Demo mode requires an explicit demo fixture");
    var useSubscription = demo && settings.demoUseSubscription === true;
    var sourceCtx = demo && !useSubscription ? {data: fixtureRows(fixture)} : ctx;
    // Màn Tổng quan đọc nhiều entity; mọi widget chi tiết vẫn bị ràng buộc một entity.
    var multiEntity = !demo && settings.component === "overview";
    var liveBarns = multiEntity ? barnsFromEntities(ctx, settings, Date.now()) : null;
    var scoped = multiEntity ? {samples: {}, scope: {rows: [], status: "MULTI_ENTITY_LIST",
        entityIds: liveBarns.map(function (b) { return b.id; })}}
      : subscriptionSamples(sourceCtx, settings.sourceIdentity || null);
    var samples = scoped.samples;
    var keyMap = settings.keyMap && typeof settings.keyMap === "object" ? settings.keyMap : {};
    var freshness = settings.freshnessMs && typeof settings.freshnessMs === "object" ? settings.freshnessMs : {};
    var invalidKeys = simulationInvalidKeys(samples, settings);
    var now = Date.now(), latest = {}, platform = {}, settingValues = {}, base = demo ? fixture : {};
    var notConfigured = demo ? (((base.mapping || {}).notConfigured || []).slice()) : [];
    var unresolved = demo ? [] : mappedKeys().filter(function (semantic) {
      return typeof keyMap[semantic] !== "string" || !keyMap[semantic];
    }), observed = {};
    mappedKeys().forEach(function (semantic) {
      var actual = demo ? (useSubscription ? (keyMap[semantic] || semantic) : semantic) : keyMap[semantic];
      // Chỉ che giá trị mới nhất. historyFromRows giữ nguyên các mẫu lịch sử thực tế của nó.
      var item = invalidKeys[semantic] ? null : (typeof actual === "string" && actual ? samples[actual] : null);
      if (item) observed[semantic] = {actualKey: actual, value: item.rawValue, ts: item.ts};
      var fixtureItem = demo && !useSubscription ? ((PLATFORM.indexOf(semantic) >= 0 ? base.platform : base.latest) || {})[semantic] : null;
      var output = {value: item ? item.value : null, ts: demo && fixtureItem ? fixtureItem.ts : (item ? item.ts : null),
        quality: demo && fixtureItem ? fixtureItem.quality : qualityFor(item, freshness[semantic], now)};
      if (PLATFORM.indexOf(semantic) >= 0) {
        output.value = item ? platformValue(semantic, item.rawValue) : null;
        platform[semantic] = output;
      }
      else if (isSetting(semantic)) settingValues[semantic] = output;
      else latest[semantic] = output;
    });
    var history = demo && !useSubscription ? base.history : historyFromRows(scoped.scope.rows, keyMap, freshness, now);
    var alarmState = alarmSubscription(ctx, demo);
    var alarms = demo ? base.alarms : alarmState.alarms;
    var context = demo ? (base.scope || {}) : liveContext(ctx, settings);
    return {demo: true, contract: demo ? fixture.contract : {version: "0.3"}, latest: latest, platform: platform,
      mapping: {notConfigured: notConfigured}, fixtureVersion: base.fixtureVersion, generatedAt: base.generatedAt,
      badgeLabel: base.badgeLabel, scope: context,
      summary: multiEntity ? barnSummary(liveBarns) : base.summary,
      barns: multiEntity ? liveBarns : base.barns, history: base.history,
      settings: demo && !useSubscription ? base.settings : settingValues, alarms: alarms,
      _source: {mode: demo ? "demo" : "live", keyMap: keyMap, observed: observed,
        unresolved: unresolved, invalidKeys: Object.keys(invalidKeys), sourceIdentity: settings.sourceIdentity || null,
        freshness: freshness, datasources: (ctx && ctx.datasources) || [], scope: scoped.scope,
        history: history, alarms: demo ? "FIXTURE" : alarmState.status, provenance: sourceProvenance(settings, demo),
        alarmScope: settings.alarmScope || "Chưa xác minh phạm vi"}};
  }
  function createViewModel(ctx, settings, fixture) {
    if (!root.VentilationAdapter || !root.VentilationAdapter.createViewModel) throw new Error("VentilationAdapter is required");
    settings = settings || {};
    var raw = rawFromSubscription(ctx, settings, fixture);
    raw.history = raw._source.history;
    var vm = root.VentilationAdapter.createViewModel(raw);
    // Freshness is not a successful decoding claim: invalid enum/run encodings remain UNKNOWN.
    Object.keys(vm.metrics).forEach(function (key) {
      var metric = vm.metrics[key], observed = raw._source.observed[key];
      if (observed && observed.value !== null && (metric.value === "UNKNOWN" || metric.value === null)) metric.quality = "UNKNOWN";
    });
    vm.equipment.forEach(function (item) { item.quality = vm.metrics[item.key].quality; });
    var live = raw._source.mode === "live";
    vm.source = live ? "thingsboard" : "fixture";
    vm.sourceMode = raw._source.mode;
    vm.demo = !live;
    vm.badgeLabel = live ? "" : vm.badgeLabel;
    vm.provenance = raw._source.provenance;
    vm.mapping = {status: live ? (raw._source.unresolved.length ? "UNRESOLVED" : "MAPPED") : "FIXTURE",
      unresolved: raw._source.unresolved, invalidKeys: raw._source.invalidKeys, keyMap: raw._source.keyMap, sourceIdentity: raw._source.sourceIdentity,
      scope: raw._source.scope.status, entityIds: raw._source.scope.entityIds,
      observations: raw._source.observed};
    // Keep source provenance outside a metric so observed values cannot be mistaken for verified feedback.
    vm.sourceInfo = {identity: raw._source.sourceIdentity, datasources: raw._source.datasources,
      freshnessConfigured: Object.keys(raw._source.freshness).filter(function (key) { return positive(raw._source.freshness[key]); }),
      alarms: raw._source.alarms, context: vm.scope};
    vm.alarmsSource = {status: raw._source.alarms, loaded: raw._source.alarms !== "NOT_LOADED",
      display: raw._source.alarms === "NOT_LOADED" ? "-- / chưa nạp" : null,
      scope: raw._source.alarmScope};
    return vm;
  }
  root.VentilationSource = {createViewModel: createViewModel, subscriptionSamples: subscriptionSamples,
    rawFromSubscription: rawFromSubscription};
}(window));
