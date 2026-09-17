# Canonical view model

The adapter is the explicit compatibility boundary between VENT-002 legacy snake-case
evidence/fixtures and the Rev A dashboard contract. It exposes `scope`, `summary`,
`barns`, `metrics`, `controller`, `equipment`, `louvers`, `history`, and `alarms`.
`dashboard/app.js` consumes only canonical camel-case names.

Canonical metrics are `indoorTemperature01`, `indoorTemperature02`,
`indoorTemperatureAvg`, `outdoorTemperature`, `perceivedTemperature`,
`relativeHumidity`, `airSpeed`, `airFlow`, `waterConsumptionTotal`, `operatingMode`,
`fanControlMode`, `fanStage`, `stageCount`, `controllerOnline`, `dataQuality`,
`roofInletPosition`, `sideInletPosition`, six `fanXXRun`/`fanXXFault` pairs, and two
`coolingPumpXXRun`/`coolingPumpXXFault` pairs.

`safeMetric()` preserves `false`, `0` and `null` as distinct values. Equipment state is
derived from separate run/fault semantics: fault true → `FAULT`; fault false plus run
true → `RUNNING`; fault false plus run false → `STOPPED`; otherwise → `UNKNOWN`.
Stage display uses `n / count` only when `stageCount` exists; otherwise it displays the
current stage without a fake denominator.

The equipment list is derived from the canonical `fanXXRun/Fault` and
`coolingPumpXXRun/Fault` metrics, not re-read from raw input. Only strict booleans count:
`0` or a string never becomes `RUNNING`/`STOPPED`. History rows map missing samples to
`null` (drawn as gaps, shown as `--`) and a missing row quality to `UNKNOWN`, never
`CURRENT`. These rules are executed in Firefox by `tests/test_dashboard_browser.py`.

Production replacement must map confirmed ThingsBoard data into exactly this model. The
adapter must not infer `OFFLINE` from absent telemetry, treat a command as feedback, or
hard-code stage counts from the PDF.
