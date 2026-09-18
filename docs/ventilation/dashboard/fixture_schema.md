# Fixture schema (Fixture v2.0.0 / Data Contract v0.3)

`fixtures/ventilation/demo.json` is a deterministic fixture carrying `demo: true`.
Its top-level fields are `fixtureVersion` (`2.0.0`), `generatedAt`, `contract`,
configurable `badgeLabel`, `scope`, `summary`, `barns`, `latest`, `platform`,
`mapping`, `settings`, `history`, `alarms`, and `adapterTestVariants`.

## 1. Contract Binding

The fixture explicitly declares its contract binding under `contract`:
- `version`: `"0.3"`
- `sha256`: `"6cce2e264f5a698cbdd7ab157a21101c968671c55836dcde3ecdf6170f987244"`
- `classification`: `"APPROVED PROJECT INTERFACE TEMPLATE — not runtime verified"`

If the fixture contract version does not match the loaded `VentilationContract.version`,
the adapter rejects it with an explicit error.

## 2. Telemetry (`latest`)

Telemetry in `latest` uses camelCase keys matching Data Contract v0.3 and simulated PLC data encodings:
- Enums are encoded as integers (`uint16`):
  - `operatingMode`: `0 = MANUAL`, `1 = AUTO`
  - `controlBasis`: `0 = ACTUAL_TEMPERATURE`, `1 = PERCEIVED_TEMPERATURE`
  - `fanControlMode`: `0 = STEP`, `1 = VFD`
  - `dehumidificationEnabled`: `0 = DISABLED`, `1 = ENABLED`
- Equipment run signals use `uint16`: `0 = STOPPED`, `1 = RUNNING`.
- Process and hardware alarms: `0 = NORMAL`, `1 = ACTIVE`.
- Environmental measurements use `float32` values.
- Quality tags follow `CURRENT`, `STALE`, `OFFLINE`, `UNKNOWN`.
- Missing values are represented as `null` (rendering as `--`) and never coerced to zero.

## 3. Platform Block (`platform`)

Contains platform-derived telemetry that is not mapped to PLC registers:
- `controllerOnline`: connection status monitored by the platform.
- `dataQuality`: overall data quality assessment.

## 4. Hardware Configuration (`mapping.notConfigured`)

- Defines equipment keys not physically present or unconfigured in the barn (e.g. `["fan06Run"]`).
- The adapter decodes these as `NOT_CONFIGURED`, rendering them muted with an explicit label.

## 5. Read-Only Settings (`settings`)

- Contains key-value pairs for the 224 settings variables defined in Contract v0.3.
- In demo/baseline mode, this object is empty `{}` or contains `null`, resulting in `--` rendered across all 224 cells in the `#vent_settings` tab.

## 6. History (`history`)

- Contains time-series rows using canonical contract keys: `indoorTemperatureAvg`, `outdoorTemperature`, `perceivedTemperature`, `relativeHumidity`, and "Gió & nước" metrics (`airSpeed`, `airFlow`, `waterConsumptionTotal`).

## 7. Alarms (`alarms`)

- Normalized alarms carry an explicit `source` attribute (`PLC` for controller alarms, `PLATFORM` for connectivity/stale data alarms).
