# VENT-002 implementation readiness

## Decision package

| Area | Required | Status | Evidence | Blocker | Implementation impact |
|---|---|---|---|---|---|
| Entity topology | actual entities/relations/isolation | unresolved | GET probes returned 401; no export | authenticated entity/relation inventory | cannot build aliases or datasource scope |
| Farm alias | one isolated Farm | unresolved | no dashboard/runtime alias | filter/root/boundary unknown | overview cannot be safely scoped |
| Barn selection | selected Barn contract | unresolved | no state/alias config | parameter/entity shape unknown | detail navigation blocked |
| Controller selection | exactly one controller | unresolved | no controller inventory | relation/cardinality unknown | detail datasource blocked |
| Telemetry mapping | every V1 key mapped and sampled | unresolved: 0/21 confirmed | contract and source inventory | no gateway map or samples | all live widgets blocked |
| Environmental KPIs | key/unit/scale/sample | unresolved | PDF only | runtime mapping absent | KPI implementation blocked |
| Fan feedback | physical feedback provenance | unresolved | relay command documented only | no feedback signal/sample | cannot show running/stopped |
| Pump feedback | physical feedback provenance | unresolved | relay command documented only | no feedback signal/sample | cannot show running/stopped |
| Louver feedback | key, 0–10 V conversion/sample | partial hardware fact only | PDF pp. 6, 9–10 | scale and runtime key absent | position display blocked |
| Controller mode | Auto/Manual key/enum/sample | unresolved | PDF only | runtime source absent | mode display blocked |
| Control mode | Step/VFD key/enum/sample | unresolved | PDF only | runtime source absent | control-mode display blocked |
| Ventilation stage | current-stage key/sample | unresolved | PDF capability only | runtime source absent | stage display blocked |
| Stage count | runtime/config source | unresolved | 6/9 are document maxima | no runtime count evidence | must not render x/6 or x/9 |
| Air speed | source/unit/scale/sample | unresolved | display mention only | no source | omit from V1 until resolved |
| Air flow | source/formula/unit/sample | unresolved | unrelated external key only | no ventilation evidence | omit from V1 until resolved |
| Water consumption | pulse scale/reset/unit/sample | unresolved | pulse input documented | mapping absent | omit from V1 until resolved |
| Connectivity | authoritative online/offline source | unresolved | generic platform candidates only | controller signal absent | offline indicator blocked |
| Freshness | cadence and thresholds | unresolved | no samples | all thresholds null | stale classification blocked |
| Alarm scope | originator/relation/query | unresolved | no successful query | scope unavailable | alarm state blocked |
| Alarm history | retention/status semantics | unresolved | PDF HMI only | TB runtime unavailable | history state blocked |
| History query | keys, retention, timezone | unresolved | no telemetry history sample | runtime unavailable | trend implementation blocked |
| Export | deployed read-only capability | unresolved | PDF HMI only | TB edition/widget/permission unknown | export must remain absent |
| Responsive/runtime dependencies | real content density and widget capability | design targets only | VENT-001 matrix | no implementation/runtime dataset | visual runtime verification deferred |

## Readiness status

`NOT READY FOR IMPLEMENTATION`

The investigation is complete for the evidence currently accessible, but the runtime
authorization boundary prevented every implementation-critical binding from being
verified. No production dashboard implementation should begin.

## Minimum unblock package

1. An approved authenticated read session that permits GET-only entity, relation,
   dashboard, telemetry, attribute and alarm queries.
2. Official ventilation device/profile identity and PLC/Gateway mapping.
3. One timestamped real sample for every field proposed for V1.
4. Direct proof separating equipment command/request state from actual feedback.
5. Sampling/transport cadence evidence for stale thresholds.

The `APPROVED — IMPLEMENTATION READY` gate remains exclusively with ChatGPT Web and is
not granted by this document.
