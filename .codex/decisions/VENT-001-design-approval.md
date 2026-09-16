# VENT-001 design approval

## Decision

`APPROVED — DESIGN ONLY`

Recorded: 2026-09-16

This decision accepts the VENT-001 baseline/design package. It does not authorize
production dashboard implementation or deployment.

## Approved

- Repository baseline.
- Semantic contract structure.
- Uncertainty classification.
- Proposed entity topology as a hypothesis.
- Four-state dashboard design.
- Responsive design plan.
- Read-only widget boundaries.
- V1 safety boundary.

## Not approved / still unconfirmed

- PLC raw tags/registers.
- ThingsBoard entity/alias bindings.
- Data types and enum encodings.
- Engineering scaling.
- Freshness/stale thresholds.
- Fan/pump feedback provenance.
- Air speed, airflow and water production source.
- Alarm mappings/scope.
- History/export runtime capability.
- Production dashboard implementation.
- Deployment.

## Next task

VENT-002 — Runtime and Data Binding Verification.

VENT-002 must produce implementation-ready, read-only evidence for every runtime
dependency that VENT-001 left uncertain. Its completion remains subject to the separate
`APPROVED — IMPLEMENTATION READY` gate, which Codex must not self-grant.
