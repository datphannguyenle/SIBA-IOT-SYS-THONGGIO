# VENT-005 — Provisioning Manifest and Dry Run

## Status

`active — dry run complete, blockers unresolved`

## Objective

Convert the approved VENT-004 architecture into an exact, reviewable and idempotent
mutation manifest without changing ThingsBoard state.

## Scope

- Select the first-rollout Barn from live read-only evidence.
- Resolve or explicitly block canonical SITE/AREA/BUILDING codes.
- Confirm or block controller cardinality.
- Preflight names, profiles, ownership and relations.
- Produce create/reuse/no-op, API and reverse-order rollback manifests.

## Forbidden scope

- Any ThingsBoard create, update or delete operation.
- Gateway configuration changes.
- Telemetry or attribute writes.
- Dashboard, rule-chain or alarm creation.
- RPC, command widget, alarm mutation or PLC/device command.
- Treating proposed codes or document examples as approved runtime facts.

## Inputs

- Approved VENT-004 provisioning plan.
- SIBA-TB-STD-001 Rev A decision and errata.
- VENT-002 authenticated runtime evidence.
- Current authenticated GET-only tenant inventory.

## Expected outputs

- `docs/ventilation/provisioning/rollout_scope.md`.
- `docs/ventilation/provisioning/entity_manifest.md`.
- `docs/ventilation/provisioning/profile_manifest.md`.
- `docs/ventilation/provisioning/relation_manifest.md`.
- `docs/ventilation/provisioning/api_mutation_manifest.md`.
- `docs/ventilation/provisioning/rollback_manifest.md`.
- `docs/ventilation/provisioning/dry_run_report.md`.

## Model routing

| Work package | Model/effort | Owner | Reason |
|---|---|---|---|
| Runtime evidence, manifest architecture and final safety review | MAIN | MAIN | One bounded read-only session and cross-document gate integration |

## Dependencies

- VENT-004 is approved as a plan only.
- Exact production SITE/AREA codes and controller cardinality require owner approval.
- `RC-20-VEN-PROCESS-V1` is absent and rule-chain creation is outside this task.

## Acceptance criteria

- [x] One exact live Barn is selected for the pilot with ID, parent and ownership evidence.
- [ ] SITE, AREA and BUILDING codes are approved, not merely derived.
- [ ] Controller cardinality has an authoritative project/owner confirmation.
- [x] Candidate exact target names are documented and collision-checked.
- [x] Profile, entity, relation, API and rollback manifests are documented.
- [x] Every action is marked `CREATE`, `REUSE`, `NO-OP` or `BLOCKED`.
- [x] Dry-run findings distinguish runtime facts from proposals.
- [x] No non-authentication POST, PUT, PATCH, DELETE or ThingsBoard mutation occurred.

## Required evidence

- [x] Exact live Barn/Gateway/customer IDs and current relations.
- [x] Full tenant name scan and exact-name lookups.
- [x] Profile and rule-chain inventories.
- [x] Live OpenAPI operation IDs and schemas for planned API paths.
- [x] Authentication-only POST and GET-only request accounting.
- [ ] Reviewer resolution of blockers.

## Gate

`APPROVED — CONTROLLED PROVISIONING EXECUTION`

Codex must not self-grant this gate. Approval must explicitly resolve the canonical
codes, cardinality and blocked profile dependency before execution.

## Ownership

### Mutable files

- This task record and the seven provisioning documents listed above.

### Browser/runtime session

- Read-only ThingsBoard API inspection only; no mutable browser session.

## Notes

- The deterministic pilot candidate is `abc-dong-anh/ND2-1`, the first live Barn with
  `barnType=1F1`. Selection of the live object is exact; its new canonical codes remain
  proposed pending reviewer/owner approval.
- Dry-run result is `BLOCKED — NOT READY FOR CONTROLLED EXECUTION`.
