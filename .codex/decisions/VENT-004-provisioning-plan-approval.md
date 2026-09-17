# VENT-004 provisioning plan approval

## Decision

`APPROVED — VENTILATION PROVISIONING PLAN`

Recorded: 2026-09-17

## Approved

- The Rev A greenfield-with-legacy-compatibility architecture.
- Preservation of existing `FarmToArea` and `AreaToBarn` relations.
- The proposed Barn → Ventilation System → VentilationController topology.
- Preparation of an exact, idempotent provisioning manifest and dry run.

## Not authorized

- Any ThingsBoard create, update or delete operation.
- Gateway configuration changes.
- Telemetry or attribute writes.
- Dashboard, rule-chain or alarm creation.
- RPC or PLC/device commands.

## Next task

VENT-005 — Provisioning Manifest and Dry Run, subject to the separate gate
`APPROVED — CONTROLLED PROVISIONING EXECUTION`.
