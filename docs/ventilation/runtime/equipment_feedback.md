# VENT-002 equipment feedback verification

## Result

`UNRESOLVED FOR RUNTIME`

The technical document distinguishes relay outputs from louver analog feedback, but no
live key or sample was available. Command/request state is not classified as physical
feedback.

## Fans and pumps

| Equipment | Command state | Requested state | Actual feedback | Fault feedback | Observed sample/timestamp | Classification |
|---|---|---|---|---|---|---|
| Fan 01 | relay output documented; runtime key unknown | unknown | not evidenced | shared equipment-fault input documented; attribution unknown | unavailable | uncertain |
| Fan 02 | relay output documented; runtime key unknown | unknown | not evidenced | shared equipment-fault input documented; attribution unknown | unavailable | uncertain |
| Fan 03 | relay output documented; runtime key unknown | unknown | not evidenced | shared equipment-fault input documented; attribution unknown | unavailable | uncertain |
| Fan 04 | relay output documented; runtime key unknown | unknown | not evidenced | shared equipment-fault input documented; attribution unknown | unavailable | uncertain |
| Fan 05 | relay output documented; runtime key unknown | unknown | not evidenced | shared equipment-fault input documented; attribution unknown | unavailable | uncertain |
| Fan 06 | relay output documented; runtime key unknown | unknown | not evidenced | shared equipment-fault input documented; attribution unknown | unavailable | uncertain |
| Pump 01 | relay output documented; runtime key unknown | unknown | not evidenced | shared equipment-fault input documented; attribution unknown | unavailable | uncertain |
| Pump 02 | relay output documented; runtime key unknown | unknown | not evidenced | shared equipment-fault input documented; attribution unknown | unavailable | uncertain |

The PDF HMI uses running/stopped presentation, but it does not prove a separate electrical
feedback input. Until a PLC/Gateway mapping demonstrates otherwise, all fan and pump
`*_status` candidates remain uncertain and must not be labeled physical running feedback.

## Louvers

| Equipment | Command state | Requested state | Actual feedback | Fault feedback | Range/conversion | Sample/timestamp | Classification |
|---|---|---|---|---|---|---|---|
| Roof louver | open/close relay outputs documented | runtime key unknown | 0–10 V position input documented | not evidenced | endpoints, calibration and percent conversion unknown | unavailable | uncertain runtime mapping |
| Side louver | open/close relay outputs documented | runtime key unknown | 0–10 V position input documented | not evidenced | endpoints, calibration and percent conversion unknown | unavailable | uncertain runtime mapping |

The existence of an analog feedback circuit is a confirmed hardware fact, not a confirmed
ThingsBoard telemetry binding. Do not display percent position without calibration and a
real timestamped sample.

## Evidence

- Technical PDF pp. 8–10: fan/pump/louver relay outputs and louver 0–10 V feedback inputs.
- No ventilation gateway mapping, live telemetry response or device profile was found.
- Runtime GET access was blocked by HTTP 401.

## Blockers

- Official PLC/Gateway mapping separating command/request/feedback/fault signals.
- Runtime keys, enum/value semantics and one timestamped sample per equipment group.
- Confirmation whether the shared equipment-fault input can identify a specific device.
