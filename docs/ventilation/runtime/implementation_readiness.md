# VENT-002 implementation readiness

## Decision matrix

| Area | Required | Status | Evidence | Blocker / implementation impact |
|---|---|---|---|---|
| Entity topology | actual entities/relations/isolation | partial | Farm→Area→Barn confirmed; controller count 0 | controller/profile/relation provisioning required |
| Farm alias | one isolated Farm | absent | nine dashboards inspected | overview scope not configured |
| Barn selection | selected Barn contract | absent | no `vent_*` state/alias | detail navigation blocked |
| Controller selection | exactly one controller | absent | no controller device/profile | all controller datasources blocked |
| Telemetry mapping | every V1 key mapped/sampled | unresolved: 0/21 | authenticated inventory + local search | live widgets blocked |
| Environmental KPIs | key/unit/scale/sample | unresolved | PDF only | detail KPI blocked |
| Fan feedback | physical feedback provenance | unresolved | relay command only | schematic blocked |
| Pump feedback | physical feedback provenance | unresolved | relay command only | schematic blocked |
| Louver feedback | key/conversion/sample | hardware circuit only | PDF 0–10 V input | position display blocked |
| Controller mode | Auto/Manual key/enum/sample | unresolved | PDF only | mode display blocked |
| Control mode | Step/VFD key/enum/sample | unresolved | PDF only | display blocked |
| Stage / stage count | runtime keys/config | unresolved | 6/9 are document maxima | stage display blocked |
| Air speed/flow/water | complete binding or explicit V1 rejection | unresolved | no mapping/source | omit only after reviewer-approved scope decision |
| Connectivity | authoritative signal | unresolved | no controller | overview/detail status blocked |
| Freshness | cadence/thresholds | unresolved | no samples | stale classification blocked |
| Alarm scope/history | originator/query/retention | absent/unresolved | 7,464 alarms scanned; no vent scope | `vent_alarms` blocked |
| History query | mapped keys/retention/timezone | unresolved | no telemetry entity | `vent_history` blocked |
| Export | verified read-only capability | absent | no vent dashboard/widget | must remain absent |
| Responsive runtime | populated widgets/data density | design-only | VENT-001 targets | runtime verification deferred |

## Readiness status

`NOT READY FOR IMPLEMENTATION`

Authenticated inspection resolved the access blocker but confirmed a more fundamental
deployment gap: the ventilation entity/profile/relation, aliases, mappings and data do not
exist. All four required V1 states lack at least one core datasource, so scope is not
silently reduced.

## Required next decision

A separately approved, non-dashboard provisioning/data-onboarding task must define the
controller profile/entities, Barn relations, gateway mapping, telemetry and alarm scope.
After those artifacts produce read-only samples, VENT-002 must verify them before
implementation review.

Codex does not grant `APPROVED — IMPLEMENTATION READY`.
