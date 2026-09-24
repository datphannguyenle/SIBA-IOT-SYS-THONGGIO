# VENT-012 — UI baseline decision

Date: 2026-09-24

Decision: **APPROVED — SIBA OPERATIONS UI V1 REFERENCE**

The current ventilation interface is frozen as `SIBA-OPS-DARK-1.0` and will be the visual
reference when other SIBA systems are redesigned. Runtime reference: dashboard
`DB-30-VEN-DETAIL-V1-GATEWAY-SIM` version 8; source reference: commit `cddc523`.

Approved for reuse:

- navy/cyan visual language and semantic status colors;
- panel, typography, spacing and navigation hierarchy;
- overview without house-level tabs;
- compact house header with state navigation;
- responsive strategy and bounded scrolling;
- modular widget responsibility boundaries;
- explicit missing/stale/offline and SIM provenance treatment.

Not approved by this decision:

- copying ventilation telemetry, alarm thresholds or equipment topology;
- changing another system's data contract or control behavior;
- deploying changes to another dashboard;
- promoting SIM mappings to production;
- enabling any write/RPC/device command.

Any future baseline replacement requires a new version and regression review.
