# Canonical view model (Data Contract v0.3 / VENT-007)

The adapter (`widgets/ventilation-adapter.js`) acts as the compatibility boundary between
raw ThingsBoard/fixture telemetry and the canonical view model consumed by `dashboard/app.js`.
The authoritative schema is defined by **Data Contract v0.3** (`widgets/ventilation-contract-v03.js`),
comprising 265 variables (PLC mirror `D550–D959`, Modbus holding registers `4x-1 .. 4x-410`).

## 1. Structure

The adapter produces a canonical view object exposing:
- `scope`: current scope metadata (`barnId`, `barnName`, `facilityId`).
- `summary`: farm-level aggregated status counters (`online`, `running`, `warning`, `stopped`).
- `barns`: list of barns for farm overview (`id`, `name`, `status`, `stage`, `tempIndoor`, `tempTarget`, `humidity`, `operatingMode`).
- `metrics`: dictionary of decoded canonical metrics with `{value, rawValue, unit, quality, classification, contractStatus, configured}`.
- `controller`: decoded controller state (`mode`, `basis`, `fanControlMode`, `dehumidification`, `stage`, `online`, `dataQuality`).
- `equipment`: list of equipment models (`fans`, `pumps`, `louvers`, `counters`).
- `systemFaults`: system-level fault and alarm indicators (`equipmentFaultActive`, etc.).
- `settings`: hierarchical groups of the 224 read-only settings parameters.
- `history`: environmental telemetry series and "Gió & nước" table.
- `alarms`: normalized alarm entries with explicit `source` (`PLC` vs `PLATFORM`).

## 2. Equipment State Semantics

In accordance with Data Contract v0.3:
- Each fan (`fan01Run` .. `fan06Run`) and cooling pump (`coolingPump01Run`, `coolingPump02Run`) uses a single `uint16` variable: `0 = STOPPED`, `1 = RUNNING`.
- Any missing, null, or invalid code is decoded as `UNKNOWN`.
- Equipment marked unconfigured via `mapping.notConfigured` decodes as `NOT_CONFIGURED` and renders muted with a "NOT CONFIGURED" badge. It is never shown as `STOPPED` or `FAULT`.
- Per-device fault telemetry keys (`fanXXFault`, `coolingPumpXXFault`) were **removed** from the model; device fault is reported at system level via `equipmentFaultActive`.

## 3. Controller Stage Semantics

- The controller displays `fanStage` as an absolute integer (e.g. `4`).
- `stageCount` was **removed** from the contract. The UI never displays a synthetic ratio (e.g. `4 / 6` is forbidden); the 9 slots in the contract represent maximum engineering configuration capacity, not an active denominator.

## 4. Platform-Derived Variables

- `controllerOnline` and `dataQuality` are classified as `PLATFORM_DERIVED`. They do not originate from PLC D-registers and are provided by the connectivity and platform health monitoring layer.

## 5. Read-Only Settings (224 variables)

- Contract v0.3 defines 224 settings variables (179 PROPOSED, 45 OPTIONAL) covering temperature profiles, ventilation stages, run/stop delays, and calibration offsets.
- These are exposed in the canonical model under `settings` for display in the read-only `#vent_settings` tab.
- All settings render `--` by default until confirmed telemetry or attributes are supplied. No mutation, writing, or RPC is allowed in V1.
