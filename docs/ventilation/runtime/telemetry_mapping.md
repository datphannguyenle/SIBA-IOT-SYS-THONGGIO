# VENT-002 telemetry mapping verification

## Result

`0 confirmed · 0 rejected · 21 unresolved/derived`

The host was reachable, but no authenticated read session was available. Therefore no
actual ThingsBoard key, PLC/Gateway source, raw tag, type, encoding, range, cadence,
timestamp or sample could be observed. PDF presence alone was not used as runtime proof.

`—` below means no direct runtime/config evidence was available; it does not mean the
field is absent.

| Semantic key | ThingsBoard key | Source device / PLC-Gateway / raw tag | Type / encoding | Unit / scale / valid range | Timestamp / cadence / observed interval | Stale threshold | Sample timestamp / value | Classification | Evidence / notes |
|---|---|---|---|---|---|---|---|---|---|
| `temperature_indoor` | — | — / — / — | — | °C from PDF only / — / — | — | null | — / — | uncertain | No runtime sample; PDF does not bind a key |
| `temperature_outdoor` | — | — / — / — | — | °C from PDF only / — / — | — | null | — / — | uncertain | No runtime sample |
| `temperature_feel` | — | — / — / — | — | °C from PDF only / — / — | — | null | — / — | uncertain | Source/calculation unknown |
| `humidity` | — | — / — / — | — | %RH from PDF only / — / — | — | null | — / — | uncertain | No runtime sample |
| `air_speed` | — | — / — / — | — | — / — / — | — | null | — / — | uncertain | `UNRESOLVED`; no listed sensor/mapping |
| `air_flow` | — | — / — / — | — | — / — / — | — | null | — / — | uncertain | `UNRESOLVED`; deodorization key is not ventilation evidence |
| `water_consumption` | — | — / — / — | — | — / pulse conversion unknown / — | — | null | — / — | uncertain | `UNRESOLVED`; PDF names a pulse input only |
| `fan_01_status` | — | — / — / — | — | — | — | null | — / — | uncertain | Command-versus-feedback unresolved |
| `fan_02_status` | — | — / — / — | — | — | — | null | — / — | uncertain | Command-versus-feedback unresolved |
| `fan_03_status` | — | — / — / — | — | — | — | null | — / — | uncertain | Command-versus-feedback unresolved |
| `fan_04_status` | — | — / — / — | — | — | — | null | — / — | uncertain | Command-versus-feedback unresolved |
| `fan_05_status` | — | — / — / — | — | — | — | null | — / — | uncertain | Command-versus-feedback unresolved |
| `fan_06_status` | — | — / — / — | — | — | — | null | — / — | uncertain | Command-versus-feedback unresolved |
| `pump_01_status` | — | — / — / — | — | — | — | null | — / — | uncertain | Command-versus-feedback unresolved |
| `pump_02_status` | — | — / — / — | — | — | — | null | — / — | uncertain | Command-versus-feedback unresolved |
| `roof_louver_position` | — | — / — / — | — | 0–10 V hardware signal / conversion unknown / range unknown | — | null | — / — | uncertain | Feedback path documented; runtime mapping absent |
| `side_louver_position` | — | — / — / — | — | 0–10 V hardware signal / conversion unknown / range unknown | — | null | — / — | uncertain | Feedback path documented; runtime mapping absent |
| `operation_mode` | — | — / — / — | enum unknown | — | — | null | — / — | uncertain | Manual/Auto document capability only |
| `fan_control_mode` | — | — / — / — | enum unknown | — | — | null | — / — | uncertain | Step/VFD document capability only |
| `ventilation_stage` | — | — / — / — | numeric/enum unknown | level / — / runtime count unknown | — | null | — / — | uncertain | Do not infer count 6 or 9 |
| `controller_online` | — | ThingsBoard/Gateway candidate / — / not a PLC tag | boolean candidate | — | — | null | — / — | derived | Design need only; source and timeout unresolved |

## Conditional measurements decision

| Field | V1 decision | Reason |
|---|---|---|
| `air_speed` | `UNRESOLVED` | no key, source, unit, conversion or sample |
| `air_flow` | `UNRESOLVED` | no ventilation source/formula/sample; external domain data cannot be reused |
| `water_consumption` | `UNRESOLVED` | pulse exists in documentation but pulse scale/reset/unit/sample are unknown |

None can be displayed in V1 until the evidence set required by the task is complete.

## Runtime access evidence

- Unauthenticated entity and dashboard GET probes returned HTTP 401.
- `TB_URL`, `TB_USER` and `TB_PASSWORD` were not present in the process environment.
- Existing device-token cache values were neither read nor used; device tokens are a
  telemetry-write transport, not tenant read authorization.
