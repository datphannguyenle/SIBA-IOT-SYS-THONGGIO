# VENT-002 — Runtime and Data Binding Verification

## Status

`backlog`

## Objective

Produce implementation-ready, read-only evidence for every runtime dependency that
VENT-001 left uncertain.

## Scope

### 1. Entity topology

Verify the actual:

- Farm, Area, Barn and VentilationController entities.
- Relation type and direction.
- Controller cardinality per Barn.
- Customer/tenant isolation.

### 2. ThingsBoard aliases

Verify aliases for:

- Current Farm.
- Controller collection.
- Selected Barn.
- Selected controller.
- Alarm scope.

### 3. Semantic telemetry mapping

For every V1 semantic key, record:

- Semantic key.
- Actual ThingsBoard key.
- PLC/Gateway source.
- Raw source/tag, when available.
- Type and encoding.
- Unit.
- Scale/conversion.
- Valid range.
- Timestamp semantics.
- Sampling cadence.
- Stale threshold.
- One observed read-only runtime sample.

### 4. Equipment feedback

Confirm whether:

- Fan status is actual feedback or command state.
- Pump status is actual feedback or command state.
- Louver position is actual feedback.
- A failure/fault source is available.

### 5. Controller state

Confirm:

- Auto/Manual source and encoding.
- Step/VFD source and encoding.
- Current stage source.
- Valid stage count and its source.
- The documented 6/9 modes are not assumed to equal current runtime configuration.

### 6. Conditional measurements

Confirm or explicitly reject for V1:

- `air_speed`.
- `air_flow`.
- `water_consumption`.

### 7. Connectivity and freshness

Define evidence-backed semantics for:

- `ONLINE`.
- `OFFLINE`.
- `STALE`.
- `UNKNOWN`.

Do not derive `OFFLINE` solely from missing telemetry unless that behavior is the
confirmed platform contract.

### 8. Alarms

Confirm:

- Originator.
- Alarm type and severity.
- Active/history query.
- Barn/Farm scoping.
- Retention.
- Read-only history/export availability.

## Safety boundary

VENT-002 remains read-only.

No:

- RPC.
- Attribute write.
- Device command.
- Parameter write.
- Alarm acknowledge, clear or shelve.
- ThingsBoard mutation.

Use read-only API/runtime inspection only.

## Required outputs

- `docs/ventilation/runtime/entity_topology_verified.md`
- `docs/ventilation/runtime/alias_contract.md`
- `docs/ventilation/runtime/telemetry_mapping.md`
- `docs/ventilation/runtime/equipment_feedback.md`
- `docs/ventilation/runtime/connectivity_freshness.md`
- `docs/ventilation/runtime/alarm_contract.md`
- `docs/ventilation/runtime/implementation_readiness.md`
- Updated `config/ventilation_data_contract.json`

Only promote `uncertain` to `confirmed` when direct evidence exists. A field's presence
in the technical PDF alone is not sufficient evidence for promotion.

## Acceptance criteria

- [ ] Actual entity topology, relations, cardinality and isolation are evidenced.
- [ ] Required ThingsBoard aliases and scopes are evidenced.
- [ ] Every V1 semantic key has the required mapping fields and a read-only sample, or a
      clearly recorded unresolved evidence gap.
- [ ] Equipment feedback and fault provenance are distinguished from command state.
- [ ] Controller modes, stage and valid stage count are runtime-evidenced.
- [ ] Conditional measurements are confirmed or explicitly rejected for V1.
- [ ] Connectivity and freshness states have evidence-backed definitions.
- [ ] Alarm scope, queries, retention and history/export capability are evidenced.
- [ ] No uncertain field is promoted without direct evidence.
- [ ] No write, command, alarm mutation, production implementation or deployment occurs.
- [ ] On completion, the task moves from `active` to `review` with a handoff.

## Gate

`APPROVED — IMPLEMENTATION READY`

Codex must not self-grant this gate. ChatGPT Web must review VENT-002 before any
dashboard implementation begins.

## Activation

This task is intentionally left in `backlog`. Activation and execution are outside the
scope of the VENT-001 closure turn.
