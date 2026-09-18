# Widget inventory (VENT-007 / Data Contract v0.3)

| Surface | Origin | Status | Scope / Rules |
|---|---|---|---|
| Compact header, 5 tabs, demo badge | Reused SIBA Khử mùi pattern | Implemented | Local navigation across 5 states; persistent amber demo badge |
| Farm/Barn grid (`default`) | Adapted from read-only Khử mùi grid | Implemented | Displays barn status cards with stage integer, indoor/target temp, humidity |
| Ventilation schematic (`vent_detail`) | New ventilation-specific surface | Implemented | Visualizes 6 fans, 2 pumps, roof/side louvers; unconfigured equipment muted |
| Equipment feedback strip (`vent_detail`) | New ventilation-specific surface | Implemented | Displays RUNNING / STOPPED / UNKNOWN / NOT_CONFIGURED status |
| System fault & alarm strip (`vent_detail`) | New ventilation-specific surface | Implemented | Displays `equipmentFaultActive` and active PLC/platform alarm flags |
| Controller + secondary metrics (`vent_detail`) | New canonical read-only summary | Implemented | `fanStage` displayed as integer (no denominator); platform connectivity badges |
| History chart and sample table (`vent_history`) | New fixture renderer | Implemented | Environmental curves + "Gió & nước" telemetry table |
| Alarm table (`vent_alarms`) | Read-only adaptation of system alarm layout | Implemented | Lists alarms with explicit `PLC` vs `PLATFORM` source column |
| Read-only settings matrix (`vent_settings`) | New in VENT-007 | Implemented | 224 settings cells grouped by functional area; strictly read-only, default `--` |
| Preview shell | Standalone review aid only | Implemented | Used in standalone demo only; stripped in ThingsBoard build |

There are no control, parameter write, RPC, or alarm-mutation widgets in V1.
