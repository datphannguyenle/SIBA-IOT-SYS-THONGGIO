# Handoff — VENT-002

## STATUS

`review — NOT READY FOR IMPLEMENTATION`

Investigation is complete for accessible evidence. Authenticated ThingsBoard reads were
not available, so implementation-critical bindings remain unresolved.

## MODELS USED

- MAIN: decomposition, evidence integration, conflict resolution, safety review and
  readiness decision package. Preferred route was GPT-6 Astra/ultra; exact runtime model
  identity was not independently exposed.
- Luna/low: ventilation source/config inventory and all-field mapping checklist.
- Luna/low: PDF/I/O provenance and false-confirmation checklist.
- Terra/medium: exclusive owner of the read-only ThingsBoard runtime trace.
- No Luna/medium or Terra/high escalation was used.

## FINDINGS

- **confirmed** — ThingsBoard and gateway services were running and the host was
  reachable.
- **confirmed** — Unauthenticated entity/dashboard GET requests returned HTTP 401.
- **confirmed** — No ventilation config, builder, widget, dashboard export, gateway map
  or runtime artifact exists in the inspected repositories.
- **confirmed** — All 21 contract fields lack direct ventilation mapping and real samples.
- **confirmed document fact** — Fan/pump/louver relay outputs are commands; louver
  position has a documented 0–10 V feedback circuit.
- **uncertain** — All runtime topology, aliases, telemetry bindings, fan/pump feedback,
  modes, stage, connectivity, freshness and alarm contracts.
- **derived** — Safe state handling preserves `STALE`, `OFFLINE` and `UNKNOWN` as separate
  concepts, but actual signals and thresholds remain unresolved.

## EVIDENCE

- Runtime probes: `GET /api/tenant/devices?pageSize=1&page=0` and
  `GET /api/dashboards?pageSize=1&page=0` returned HTTP 401.
- External ventilation profile:
  `/home/siba-iot-2/thingsboard-docker/docs/he-thong/thong-gio.md`.
- External data rules:
  `/home/siba-iot-2/thingsboard-docker/docs/nen-tang/du-lieu.md`.
- Technical PDF pp. 6, 8–10, 12–26 and 38–61.
- Runtime output documents under `docs/ventilation/runtime/`.

## RUNTIME ACCESS

- Host/network: reachable.
- ThingsBoard authenticated read session: unavailable.
- `TB_URL`, `TB_USER`, `TB_PASSWORD`: absent from the process environment.
- Existing secret/cache values: not read, printed or used.
- Login was not attempted because the client uses `POST /api/auth/login`, while this task
  explicitly prohibited POST against ThingsBoard.

## ENTITY TOPOLOGY

`UNRESOLVED`. The proposed `Farm -> Area -> Barn -> VentilationController` topology,
relations, controller cardinality and customer/tenant isolation were not confirmed or
rejected.

## ALIASES

`UNRESOLVED`. Current Farm, controller collection, selected Barn/controller and alarm
scope have no ventilation dashboard/export or live resolution result.

## TELEMETRY

`0 confirmed · 0 rejected · 21 unresolved/derived`. No actual ThingsBoard key, raw tag,
type, encoding, scale, valid range, cadence, stale threshold or sample was observed.

## EQUIPMENT FEEDBACK

Fan 01–06 and pump 01–02 have documented relay command outputs but no proven physical
feedback. Roof and side louvers have documented 0–10 V position feedback circuits, but
their runtime keys, calibration and samples are unresolved.

## CONTROLLER STATE

Auto/Manual, Step/VFD and stage capabilities are documented only. Runtime keys and enums
are unresolved. The document's 6/9 maxima were not converted into a runtime stage count.

## CONNECTIVITY / FRESHNESS

Authoritative connectivity signals, sampling cadence and stale thresholds are unresolved.
All `stale_after_sec` values remain null. Missing telemetry was not treated as offline.

## ALARMS

Ventilation originator, type, severity, status, propagation, scope, retention, history and
export remain unresolved. Existing deodorization behavior is reference-only.

## CHANGES

- Added seven runtime verification documents.
- Updated `config/ventilation_data_contract.json` with the VENT-002 verification result;
  no field was promoted or rejected.
- Moved VENT-002 from `active` to `review` without marking it done.
- Added this handoff.

## SAFETY AUDIT

`PASS — READ-ONLY INVESTIGATION`

- Runtime actions were limited to GET probes; both returned HTTP 401.
- No ThingsBoard `POST`, `PUT`, `PATCH` or `DELETE` was issued.
- No login POST was attempted.
- No RPC, device/PLC command, attribute write or parameter write occurred.
- No alarm, entity, relation, alias, dashboard or telemetry mutation occurred.
- No credential, token, JWT, cookie or secret value was read, printed or committed.
- No production implementation or deployment artifact was created.

## TESTS

- JSON parse and classification/count validation.
- Required-output and lifecycle checks.
- `git diff --check`.
- Secret-pattern and production-artifact review.
- Read-only safety audit of commands and runtime actions.
- Independent Luna evidence checklist.

## CONFIRMED

- Runtime host reachability and authentication boundary.
- Static absence of ventilation implementation/mapping artifacts in inspected sources.
- PDF hardware I/O direction and louver feedback signal type.
- No runtime mutation and no production implementation.

## DERIVED

- Connectivity/freshness precedence is a safe candidate framework only.
- `controller_online` remains a derived design need, not a confirmed runtime field.

## REJECTED

None. Absence of authenticated evidence was not converted into evidence that a runtime
field does not exist.

## UNCERTAIN

All actual topology, aliases, semantic bindings, samples, equipment feedback provenance,
mode/stage encodings, conditional measurements, connectivity, freshness, alarms,
history and export capability.

## BLOCKERS

1. No approved authenticated GET-capable ThingsBoard session.
2. No official ventilation device/profile scope.
3. No PLC/Gateway mapping or timestamped samples.
4. No direct feedback, cadence, freshness or alarm evidence.

## RISKS

- Implementing now would require fabricated keys, topology or thresholds.
- Relay command state could be mislabeled as physical fan/pump feedback.
- Reusing deodorization keys could bind the wrong system.
- Hard-coding 6/9 or inferring offline from missing telemetry would violate V1 rules.

## NEXT RECOMMENDED ACTION

ChatGPT Web should review the evidence package and keep implementation blocked. Provide an
approved authenticated read session plus the official ventilation device/profile and
PLC/Gateway mapping, then rerun the unresolved VENT-002 checks before considering
`APPROVED — IMPLEMENTATION READY`.
