# VENT-001 design acceptance matrix

This matrix evaluates the baseline/design package. It does not approve implementation.

| Area | Acceptance criterion | Evidence in this task | Status |
|---|---|---|---|
| Repo baseline | Existing/absent artifacts and external references are separated | `repo_baseline.md` | pass |
| Reuse | No reuse percentage; general vs business-specific classified | `reusable_components.md` | pass |
| Data contract | Every candidate has required fields and classification | `config/ventilation_data_contract.json` | pass |
| Missing data | `null != 0`, missing → `--` | contract + state docs | pass |
| State semantics | NORMAL/WARNING/FAULT/OFFLINE/STALE/UNKNOWN distinguished | `vent_detail.md`, audit | pass |
| Stage behavior | 6-step/9-VFD documented, not runtime-hard-coded | dictionary/detail | pass |
| Conditional metrics | air speed/airflow/water remain uncertain | contract/dictionary | pass |
| Topology | candidate topology remains proposed/uncertain | `entity_topology.md` | pass |
| Overview | farm scope; no one-Barn detail | `states/default.md` | pass |
| Detail | feedback-only schematic; no control | `states/vent_detail.md` | pass |
| History | built-in export only if verified | `states/vent_history.md` | pass |
| Alarms | read-only; no ack/clear/shelve | `states/vent_alarms.md` | pass |
| Responsive | four target viewports planned | `responsive_matrix.md` | pass design / runtime pending |
| Safety | no write path proposed or implemented | `v1_readonly_audit.md` | pass |
| Runtime evidence | topology/mapping/freshness samples available | none | pending blocker for implementation |
| Design gate | reviewer grants `APPROVED — DESIGN ONLY` | not granted in task | pending |

## Gate blockers before implementation

- Confirm entity topology and alias scope.
- Confirm PLC/Gateway semantic mapping, type, scale, unit and freshness.
- Confirm fan/pump feedback provenance.
- Confirm alarm schema/scope and history/export capability.
- Complete reviewer decision; task authors do not self-approve the gate.
