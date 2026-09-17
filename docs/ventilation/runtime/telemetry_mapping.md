# VENT-002 telemetry mapping verification

## Result

`0 confirmed · 0 rejected · 21 unresolved/derived`

Authenticated inventory found no ventilation controller device/profile and the approved
local repositories contain no ventilation PLC/Gateway mapping. Therefore there is no
owning entity from which a V1 runtime sample can be attributed. PDF presence alone was
not used as binding evidence.

`—` means no direct ventilation runtime/config evidence; it does not mean zero or prove
that a future source cannot exist.

| Semantic key | ThingsBoard key | Source device / PLC-Gateway / raw tag | Type / encoding | Unit / scale / valid range | Timestamp / cadence | Stale threshold | Sample | Classification | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| `temperature_indoor` | — | — / — / — | — | °C PDF label / — / — | — | null | — | uncertain | no controller/mapping |
| `temperature_outdoor` | — | — / — / — | — | °C PDF label / — / — | — | null | — | uncertain | no controller/mapping |
| `temperature_feel` | — | — / — / — | — | °C PDF label / — / — | — | null | — | uncertain | calculation/source unknown |
| `humidity` | — | — / — / — | — | %RH PDF label / — / — | — | null | — | uncertain | no controller/mapping |
| `air_speed` | — | — / — / — | — | — / — / — | — | null | — | uncertain | `UNRESOLVED FOR V1` |
| `air_flow` | — | — / — / — | — | — / — / — | — | null | — | uncertain | `UNRESOLVED FOR V1`; deodorization data excluded |
| `water_consumption` | — | — / — / — | — | — / pulse conversion unknown / — | — | null | — | uncertain | `UNRESOLVED FOR V1`; PDF pulse only |
| `fan_01_status` | — | — / — / — | — | — | — | null | — | uncertain | command/feedback unresolved |
| `fan_02_status` | — | — / — / — | — | — | — | null | — | uncertain | command/feedback unresolved |
| `fan_03_status` | — | — / — / — | — | — | — | null | — | uncertain | command/feedback unresolved |
| `fan_04_status` | — | — / — / — | — | — | — | null | — | uncertain | command/feedback unresolved |
| `fan_05_status` | — | — / — / — | — | — | — | null | — | uncertain | command/feedback unresolved |
| `fan_06_status` | — | — / — / — | — | — | — | null | — | uncertain | command/feedback unresolved |
| `pump_01_status` | — | — / — / — | — | — | — | null | — | uncertain | command/feedback unresolved |
| `pump_02_status` | — | — / — / — | — | — | — | null | — | uncertain | command/feedback unresolved |
| `roof_louver_position` | — | — / — / — | — | 0–10 V hardware / conversion unknown / range unknown | — | null | — | uncertain | feedback circuit only; no runtime key |
| `side_louver_position` | — | — / — / — | — | 0–10 V hardware / conversion unknown / range unknown | — | null | — | uncertain | feedback circuit only; no runtime key |
| `operation_mode` | — | — / — / — | enum unknown | — | — | null | — | uncertain | Manual/Auto capability only |
| `fan_control_mode` | — | — / — / — | enum unknown | — | — | null | — | uncertain | Step/VFD capability only |
| `ventilation_stage` | — | — / — / — | numeric/enum unknown | level / — / runtime count unknown | — | null | — | uncertain | do not infer count 6 or 9 |
| `controller_online` | — | no controller / — / not a PLC tag | boolean candidate | — | — | null | — | derived | design need; source unavailable |

## Authenticated key scan

- Tenant inventory: 8,186 devices across 11 non-ventilation device types/profiles.
- A bounded GET-only key scan covered all 154 non-Feeder/non-Silo/non-production-
  Deodorizer devices, including 127 Gateways.
- The only fan-like key found was unrelated `cooling_fan` on a crusher device. It is
  rejected as ventilation mapping evidence and is not one of the 21 contract fields.
- No local raw-tag → gateway-key → ThingsBoard-key chain exists for ventilation.

## Conditional measurements

| Field | V1 decision | Reason |
|---|---|---|
| `air_speed` | `UNRESOLVED` | no source, unit, conversion or sample |
| `air_flow` | `UNRESOLVED` | no ventilation source/formula/sample |
| `water_consumption` | `UNRESOLVED` | pulse scale, reset, unit and sample absent |

They are not confirmed, rejected or eligible for display.
