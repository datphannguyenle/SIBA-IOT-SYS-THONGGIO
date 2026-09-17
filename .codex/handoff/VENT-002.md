# Handoff — VENT-002

## STATUS

`review — NOT READY FOR IMPLEMENTATION`

Authenticated inspection is complete. It confirmed the shared Farm/Area/Barn hierarchy
but found no deployed ventilation controller/profile/dashboard/alias/data scope.

## MODELS USED

- MAIN: evidence integration, independent runtime validation, safety audit and readiness
  decision. Preferred route was GPT-6 Astra/ultra; exact runtime identity was not exposed.
- Luna/low: exhaustive local PLC/Gateway/config mapping search.
- Terra/medium: exclusive owner of the primary authenticated GET-only runtime inventory.
- No Luna/medium or Terra/high escalation.

## FINDINGS

- **confirmed** — Authenticated tenant-admin reads succeeded.
- **confirmed** — Live hierarchy has 1 Farm, 3 Areas and 67 Barns linked by
  `FarmToArea` and `AreaToBarn`.
- **confirmed absence** — No VentilationController device/type/profile, ventilation
  dashboard/state/alias or locally approved mapping exists.
- **confirmed** — All nine dashboards and all 7,464 accessible alarms were inspected;
  neither exposes an identifiable ventilation scope.
- **uncertain** — All 21 semantic runtime bindings and all controller/equipment semantics.
- **derived** — `controller_online` remains a design need only.

## EVIDENCE

- Paginated authenticated GETs: tenant assets/devices/dashboards, device profiles and
  alarms.
- Relation GETs for the Farm, 3 Areas and 67 Barns.
- Dashboard detail GETs for all nine dashboards.
- Bounded telemetry-key GET scan across 154 non-Feeder/non-Silo/non-production-
  Deodorizer devices, including 127 Gateways.
- Local evidence paths:
  `/home/siba-iot-2/thingsboard-docker/docs/he-thong/thong-gio.md` and
  `/home/siba-iot-2/thingsboard-docker/docs/nen-tang/du-lieu.md`.
- Technical PDF pp. 6, 8–10, 12–26 and 38–61.

## RUNTIME ACCESS

- Authentication: successful using credentials supplied through systemd user environment.
- Account authority: `TENANT_ADMIN` with tenant context.
- Credential/token/JWT/cookie values: never printed, logged, saved or committed.
- Authentication used `POST /api/auth/login` only; every other ThingsBoard request was GET.

## ENTITY TOPOLOGY

`PARTIALLY CONFIRMED`: Farm→Area→Barn is live and assigned to one tenant/customer.
Barn→VentilationController is absent; declared controller cardinality is 0 across 67 Barns.
Multi-farm isolation cannot be tested because only one Farm/customer scope exists.

## ALIASES

`CONFIRMED ABSENT FOR VENTILATION`: no current Farm/controller collection/selected
Barn/selected controller/alarm-scope alias exists for ventilation.

## TELEMETRY

`0 confirmed · 0 rejected · 21 unresolved/derived`. There is no owning ventilation entity,
raw mapping, actual key, sample, timestamp, scale, cadence or stale threshold.

## EQUIPMENT FEEDBACK

Fan/pump relays are documented commands, not proven physical feedback. Louver 0–10 V
feedback circuits are document facts only; live keys/calibration/samples do not exist.

## CONTROLLER STATE

Auto/Manual, Step/VFD and stage are document capabilities only. No runtime key, enum,
sample or stage-count source exists. The 6/9 maxima were not promoted.

## CONNECTIVITY / FRESHNESS

No controller exists to bind authoritative connectivity. No cadence/threshold evidence
exists; every `stale_after_sec` remains null. Missing telemetry is not offline.

## ALARMS

All 7,464 accessible alarm records were paginated; no ventilation-identifiable originator,
type or details were found. History GET capability exists generically, but ventilation
scope, propagation, retention and export remain unresolved/absent.

## CHANGES

- Updated all seven VENT-002 runtime evidence documents with authenticated findings.
- Updated the contract verification metadata; no field classification was promoted.
- Updated this handoff and kept the task in `review`.
- No production artifact or ThingsBoard state was changed.

## SAFETY AUDIT

`PASS — AUTHENTICATED READ-ONLY`

- Across MAIN and Terra, 8 POST requests were made, all to `/api/auth/login` only.
- All post-authentication ThingsBoard calls were GET.
- No refresh, PUT, PATCH, DELETE, RPC, telemetry/attribute write, device/PLC command,
  alarm mutation, entity/relation/alias/dashboard/profile/rule-chain/user mutation or
  deployment occurred.
- Temporary clients stored credentials/tokens in memory only and were removed.

## TESTS

- Authenticated `/api/auth/user`: 200, tenant-admin scope.
- Paginated asset/device/profile/dashboard/alarm counts cross-checked by MAIN.
- All 71 Farm/Area/Barn outgoing relation sets queried.
- All nine dashboard configurations checked for ventilation states/aliases.
- All 21 contract candidates retained without unsupported promotion.
- JSON validation, required-output checks, secret scan and `git diff --check`.
- Independent Luna checklist required before commit.

## CONFIRMED

- Authenticated access and tenant inventory.
- Farm→Area→Barn relation types/directions/counts and current ownership scope.
- Current absence of a declared ventilation controller/profile/dashboard/alias.
- Current absence of an identifiable ventilation alarm scope.
- Read-only safety compliance.

## DERIVED

- `controller_online` remains a design requirement, not a live field.
- Safe connectivity precedence remains a future contract proposal.

## REJECTED

- No contract field is rejected for V1.
- The unrelated crusher key `cooling_fan` is rejected only as ventilation mapping
  evidence; it is not one of the 21 fields.

## UNCERTAIN

Twenty fields remain `uncertain`; `controller_online` remains `derived`. Raw mappings,
samples, equipment feedback, modes/stage, conditional metrics, connectivity/freshness,
ventilation alarms/history/export and multi-farm isolation remain unresolved.

## BLOCKERS

1. No approved ventilation controller profile/entities or Barn relations.
2. No PLC/Gateway semantic mapping or timestamped samples.
3. No physical feedback, controller-state or connectivity/freshness contract.
4. No ventilation alarm/history/export datasource.
5. All four required V1 states lack implementation-critical data.

## RISKS

- Implementing now would fabricate keys, aliases, topology or thresholds.
- Existing Gateway/deodorization/crusher data could be bound to the wrong domain.
- Relay commands could be mislabeled as physical equipment feedback.
- Provisioning is a state-changing task and is not authorized by VENT-002.

## NEXT RECOMMENDED ACTION

ChatGPT Web should keep `APPROVED — IMPLEMENTATION READY` ungranted and decide how to
authorize a separate ventilation provisioning/data-onboarding task. After real entities,
mappings and read-only samples exist, rerun the unresolved VENT-002 checks.
