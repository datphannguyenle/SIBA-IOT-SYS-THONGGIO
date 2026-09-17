# VENT-004 — Greenfield ventilation provisioning plan

## Status

`done`

## Objective

Produce an approval-ready, greenfield-with-legacy-compatibility plan for onboarding
ventilation entities and canonical data without executing ThingsBoard mutations.

## Scope

- Record the Rev A adoption decision and naming errata.
- Preserve the live `FarmToArea` / `AreaToBarn` hierarchy as `LEGACY EXCEPTION`.
- Define the new Barn → Ventilation System → VentilationController target topology.
- Define Rev A technical names, profiles and relation directions.
- Map the 21 VENT-002 design keys to proposed Rev A canonical keys.
- Audit the Markdown Agent Standard against the source DOCX.
- Define prerequisites, ordered future actions, evidence checks and rollback boundaries.

## Forbidden scope

- Any ThingsBoard mutation or deployment.
- Creating or changing an entity, profile, relation, alias, dashboard, rule chain, alarm
  or Gateway connector.
- Renaming production entities or replacing legacy relations.
- Modifying existing deodorization or other production dashboards.
- Promoting an uncertain binding from a standard or PDF alone.
- RPC, command widget, parameter/telemetry/attribute write, alarm mutation or PLC write.
- Production dashboard implementation.

## Inputs

- `SIBA_ThingsBoard_Entity_Data_Standard_RevA.docx`.
- `SIBA_THINGSBOARD_AGENT_STANDARD_RevA.md`.
- VENT-002 runtime evidence and semantic contract.
- Reviewer decision dated 2026-09-17.

## Expected outputs

- `docs/standards/SIBA-TB-STD-001-RevA-errata.md`.
- `docs/standards/legacy-compatibility-policy.md`.
- `docs/standards/agent-standard-fidelity.md`.
- `docs/ventilation/provisioning_plan.md`.

## Model routing

| Work package | Model/effort | Owner | Reason |
|---|---|---|---|
| Decision integration and final review | MAIN | MAIN | Owns architecture, conflicts and gate boundaries |
| Document/runtime evidence reuse | local bounded review | MAIN | Evidence was already gathered and the requested delta is documentation-only |

## Dependencies

- VENT-002 remains in review and establishes the live absence of ventilation scope.
- Rev A is accepted only as a draft/greenfield/acceptance baseline.
- No provisioning mutation is authorized.

## Acceptance criteria

- [x] Canonical hyphen, underscore and lowerCamelCase syntax is explicit.
- [x] Existing Farm/Area/Barn topology is grandfathered and not scheduled for migration.
- [x] New System/Controller names, profiles and relation directions are specified.
- [x] All 21 design keys have proposed migration treatment without unsupported promotion.
- [x] Every major Agent Standard section is classified for DOCX fidelity.
- [x] V1 read-only boundary and `RPC-01` N/A status are explicit.
- [x] Future prerequisites, stop conditions and rollback boundary are documented.
- [x] No ThingsBoard mutation, production implementation or deployment occurs.

## Required evidence

- [x] VENT-002 repository paths and authenticated runtime findings referenced.
- [x] DOCX prose/table ambiguity recorded in the errata.
- [x] Findings remain separated into target design and runtime evidence.
- [x] Reviewer decision on the plan gate.

## Gate

`APPROVED — VENTILATION PROVISIONING PLAN`

ChatGPT Web must decide this gate. Codex must not self-grant it. Approval of this plan
does not itself authorize ThingsBoard writes.

## Ownership

### Mutable files

- The four planning files listed under Expected outputs, plus this task record.

### Browser/runtime session

- None. No runtime session or ThingsBoard mutation is required.

## Notes

- VENT-002 is not closed or promoted by this task.
- The production dashboard implementation gate remains separate.
- Planning completed on 2026-09-17 and moved to review without executing a
  ThingsBoard mutation.
- ChatGPT Web approved the plan on 2026-09-17 with decision
  `APPROVED — VENTILATION PROVISIONING PLAN`. The approval covers the plan only and
  does not authorize ThingsBoard mutations.
