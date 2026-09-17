# VENT-002 equipment feedback verification

## Result

`UNRESOLVED — no live ventilation controller or mapping`

Authenticated runtime evidence confirms that no ventilation device/profile exists. The
PDF distinguishes relay outputs from louver analog inputs, but cannot provide a live key,
sample or provenance chain.

| Equipment | Command state | Requested state | Physical feedback | Fault feedback | Runtime sample | Classification |
|---|---|---|---|---|---|---|
| Fan 01–06 | relay outputs documented; no key | unknown | not evidenced | shared equipment-fault input documented; attribution unknown | unavailable | uncertain |
| Pump 01–02 | relay outputs documented; no key | unknown | not evidenced | shared equipment-fault input documented; attribution unknown | unavailable | uncertain |
| Roof louver | open/close relays documented | unknown | 0–10 V circuit documented; runtime key absent | not evidenced | unavailable | uncertain runtime mapping |
| Side louver | open/close relays documented | unknown | 0–10 V circuit documented; runtime key absent | not evidenced | unavailable | uncertain runtime mapping |

The fan/pump HMI running/stopped presentation is not proof of physical feedback. No
`*_status` field is promoted. Louver position cannot be shown as percent until endpoints,
calibration, invalid range, key and timestamped sample are confirmed.

## Evidence

- Authenticated GET inventory: zero ventilation controllers/profiles.
- Approved local mapping search: no ventilation connector/map/export.
- Technical PDF pp. 8–10: relay commands and louver 0–10 V feedback circuits.

## Blockers

- Controller entity/profile and official PLC/Gateway mapping.
- Independent command/request/feedback/fault signals and value semantics.
- One timestamped read-only sample per equipment group.
