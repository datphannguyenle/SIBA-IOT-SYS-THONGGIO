# VENT-003 — Production-quality dashboard demo

## Status

`done — APPROVED — VENT-003 DASHBOARD DEMO (commit c30ade1, 2026-09-17)`

## Objective

Deliver a stakeholder-reviewable ventilation dashboard matching the live SIBA
deodorization visual system without waiting for PLC/Gateway bindings.

## Scope

- Four read-only states: `default`, `vent_detail`, `vent_history`, `vent_alarms`.
- Deterministic, isolated fixture data and a replaceable canonical adapter.
- Desktop, tablet and mobile behavior with one platform shell and no dashboard sidebar.
- Explicit `DEMO DATA` marking in every state.
- Repository-only demo and visual evidence; no ThingsBoard deployment.

## Safety boundary

No RPC, device/PLC command, attribute or telemetry write, alarm mutation, entity/profile/
relation/dashboard mutation, production binding or deployment.

## Dependencies and gates

- VENT-002 remains `NOT READY FOR IMPLEMENTATION`; production mapping is unresolved.
- VENT-005 remains paused with provisioning blockers unresolved.
- Fixture values are presentation evidence only and must never be promoted as runtime facts.

## Acceptance

- [x] Four states and navigation implemented.
- [x] Persistent configurable demo badge implemented.
- [x] Null, stale, offline and unknown cases represented without null-to-zero coercion.
- [x] Fixture source is separated from canonical view model.
- [x] Dashboard renderer uses Rev A canonical semantic names only.
- [x] Run/fault, false/zero/null and generic stage behavior are covered by tests.
- [x] Secondary read-only metrics and perceived-temperature history are implemented.
- [x] Responsive repository demo implemented without internal sidebar.
- [x] Static safety and schema checks pass.
- [x] Desktop and mobile visual evidence captured (regenerated 2026-09-17 after the final change).
- [x] Barn identity is explicit (`PILOT`, `LIVE_BARN_SIMULATED_STATE`, `SYNTHETIC`).
- [x] Adapter and all four states executed in headless Firefox by `tests/test_dashboard_browser.py`.
- [x] ChatGPT Web review: `APPROVED — VENT-003 DASHBOARD DEMO`; no further standalone polishing unless packaging requires it.

## Handoff log

- 2026-09-17: a previous agent stopped with the canonical model, secondary metrics,
  perceived-temperature history and DEMO-05/06 naming uncommitted and evidence stale.
  The continuation preserved that work and added: equipment derived from canonical
  metrics, history quality default `UNKNOWN`, explicit Barn identity, neutral alarm
  originators, fixture edge-case/stage variants, synoptic spacing and semantic colors,
  real browser tests, and regenerated evidence. No ThingsBoard access was used.

## Ownership

This task owns `dashboard/`, `widgets/`, `fixtures/ventilation/`, `.stitch/DESIGN.md`,
the dashboard documents, tests and this task record. It does not own or modify the
VENT-002 runtime contract or VENT-005 manifests.
