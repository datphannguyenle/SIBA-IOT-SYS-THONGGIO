# VENT-008 — Controlled Live Update to Ventilation Dashboard v0.3

## Status

`review — isolated demo updated and live browser verification PASS` (20/09/2026).

Latest checkpoint: source `4cb5eb2`, widget live version **3**, dashboard live version **2**,
five states. Two updates succeeded; API read-back matches build and protected tenant baseline
is unchanged. One earlier HTTP 500 size rejection was reconciled read-only (no state change)
and preserved in its own journal. Do not rerun deployment; see `.codex/handoff/VENT-008.md`.
Final report: `docs/ventilation/deployment/vent008_execution_report.md`.
67/67 tests PASS; 20 live viewport/state checks + 4 Barn-navigation checks PASS.
No self-granted implementation-ready gate; awaiting visual review and separate physical-data work.

The preflight-only checkpoint below is historical. The user's subsequent instruction
to continue the current checkpoint with full authority to finish the dashboard authorizes
the bounded existing demo update. This is **not** a self-granted ChatGPT Web approval,
not `APPROVED — IMPLEMENTATION READY`, and not authorization for physical/device writes.
Live changes and browser verification must be evidenced separately before completion.

## Objective

Prepare and execute a controlled live update of the existing VENT-006 isolated ThingsBoard demo
to the approved VENT-007 5-state Data Contract v0.3 build, with full rollback capability and zero
production entity impact.

## Historical preflight target versions — superseded by Status above

- **Widget Type**:
  - ID: `b9fa9280-b26a-11f1-83ad-9912edc644d2`
  - FQN: `siba_vent_demo.vent_demo_view` (full: `tenant.siba_vent_demo.vent_demo_view`)
  - Current Version on Live: `2`
- **Dashboard**:
  - ID: `b9ff4d70-b26a-11f1-83ad-9912edc644d2`
  - Title: `DB-30-VEN-DETAIL-V1-DEMO`
  - Current Version on Live: `1`
  - Current States on Live (4): `default`, `vent_detail`, `vent_history`, `vent_alarms`
  - Current Widgets on Live (4): all 4 widget configurations identical to local build

## Contract Source Baseline

- Data Contract v0.3:
  - JSON SHA-256: `a3cab3669962e988f42f94acee09260ec086deef4ee41210596483647ac23b68`
  - Excel SHA-256: `fbe8a1c8901afa29286e0e95c110c972d2d810fc1233f4de15c7f80411303ba5`
- 265 variables, 224 read-only settings, PLC mirror `D550–D959`, Modbus `4x-1 .. 4x-410`.

## Scope

1. **Pre-flight verification & live inspection** (DONE):
   - Authenticate to ThingsBoard via secure token without logging credentials.
   - Inspect live widget type and dashboard.
   - Confirm IDs, titles, state counts, isolation parameters.
   - Save sanitized rollback backup to `docs/ventilation/deployment/evidence/vent008_preflight_live_backup.json`.
   - Produce detailed diff and mutation plan.
2. **Controlled live update** (authorized by subsequent user instruction; DONE and verified):
   - Update widget type via `POST /api/widgetType`.
   - Update dashboard via `POST /api/dashboard`.
   - Re-verify UI in headless Firefox.
   - Document execution manifest and verification report.

## Forbidden Scope

- Any mutation prior to explicit gate approval.
- Modifying or affecting any protected dashboard (`SIBA · Khử mùi`, `MUGE · Tổng quan trại`, etc.).
- Creating new dashboards, widgets, bundles, devices, assets, or relations.
- Writing attributes, telemetry, or RPC.
- Connecting to live PLC or Gateway.
- Resuming VENT-005.

## Historical Pre-Flight Findings

- Live widget type is intact at version 2, cleanly isolated.
- Live dashboard is intact at version 1, containing 4 isolated widgets (`datasources: []`, `actions: {}`, `entityAliases: {}`).
- Sanitized rollback backup captured: `docs/ventilation/deployment/evidence/vent008_preflight_live_backup.json` (50,942 bytes).
- Local build in `deploy/thingsboard/build/` is up-to-date with contract v0.3, passing all 50 tests.
- Proposed mutation requires exactly 2 POST requests:
  1. `POST /api/widgetType` (updates CSS for `.NOT_CONFIGURED` & settings, controller script embedding contract v0.3).
  2. `POST /api/dashboard` (adds 5th state `vent_settings` and widget `2026fdb9-6bd1-53e2-b10d-95d80ccda410`).

## Rollback Procedure

In case of failure or visual regression:
- Use `update_vent_demo.py rollback --confirm-rollback --run-id webp` under the deployment lock;
  current rollback payloads are in `docs/ventilation/deployment/evidence/vent008_before_update_webp.json`.
  The original `vent008_preflight_live_backup.json` remains historical and unchanged.
- Restores widget type to VENT-006 refinement CSS / controller script.
- Restores dashboard configuration to 4 states (`default`, `vent_detail`, `vent_history`, `vent_alarms`).

## Gate

Historical preflight gate: `WAITING FOR CHATGPT WEB DEPLOYMENT GATE`; zero mutations at
that checkpoint. Superseded for this isolated demo only by the subsequent explicit user
authorization recorded above. VENT-002 real-data readiness and VENT-005 provisioning stay blocked/paused.

## Completion acceptance

- Preserve SIBA visual parity and v0.3 contract; no stageCount or per-equipment fault invention.
- Correct Barn selection context, history scales/gaps, read-only filters and reduced-motion behavior.
- All five states tested in real desktop/tablet/mobile browser viewports.
- Only existing widget/dashboard IDs updated, with exact before backup and guarded reverse rollback.
- Protected dashboards/bundle unchanged; asset/device/dashboard/widget counts unchanged.
- Record source commit, build equality, tests, browser evidence and unresolved PLC/runtime boundaries.
- Reviewer receives a complete UI reference package; no PR merge or production integration in this task.
