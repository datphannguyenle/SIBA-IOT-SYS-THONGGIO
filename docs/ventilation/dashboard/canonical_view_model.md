# Canonical view model

The adapter exposes `scope`, `summary`, `barns`, `metrics`, `equipment`, `louvers`,
`history`, and `alarms`. UI renderers never read PLC registers or ThingsBoard key names.

`safeMetric()` preserves `null`, normalizes invalid/missing quality to `UNKNOWN`, and
retains timestamps. Equipment records are derived only from canonical semantic keys
`fan_01_status`…`fan_06_status` and `pump_01_status`…`pump_02_status`.

Production replacement must map confirmed ThingsBoard data into exactly this model. The
adapter must not infer `OFFLINE` from absent telemetry, treat a command as feedback, or
hard-code stage counts from the PDF.
