# VENT-006 — Isolated ThingsBoard Ventilation Dashboard Demo Deployment

## Status

`active — visual refinement (APPROVED — VENT-006 CONTROLLED VISUAL REFINEMENT UPDATE)`

## Objective

Deploy the approved VENT-003 demo (commit `c30ade1`) to the live tenant as the strictly
isolated dashboard `DB-30-VEN-DETAIL-V1-DEMO`, fixture data only.

## Scope

- Package adapter + renderer + fixture + CSS into ONE static widget type
  `tenant.siba_vent_demo.vent_demo_view` (no bundle).
- Create ONE dashboard with states `default` (root), `vent_detail`, `vent_history`,
  `vent_alarms`; each state holds one widget instance with `settings.viewState`.
- In-widget navigation through `ctx.stateController.openState(...)`; dashboard uses the
  `default` state controller (live frontend code confirms it replaces, not stacks, state).
- Guarded deploy, rollback and UI-verification scripts; manifest; evidence.

## Forbidden scope

Update of any existing dashboard/widget type/bundle; any bundle create/modify; asset,
device, profile, relation, rule chain, alarm or customer create/assign; telemetry or
attribute write; RPC; Modbus/PLC command; alarm acknowledge/clear/shelve/assign;
production entity binding; `deploy_widgets.py`.

## Inputs

- Approval: ChatGPT Web `APPROVED — CONTROLLED THINGSBOARD DEMO DEPLOYMENT` (2026-09-17).
- Repository demo baseline `c30ade1` (`APPROVED — VENT-003 DASHBOARD DEMO`).
- Read-only live inventory and preflight (2026-09-17).

## Expected outputs

- `deploy/thingsboard/{vent_demo_common,build_vent_demo,deploy_vent_demo,rollback_vent_demo,verify_vent_demo_ui}.py`
- `deploy/thingsboard/build/{widget_type,dashboard}.json`, `deploy/thingsboard/vent006_manifest.json`
- `docs/ventilation/deployment/vent006_{execution_report,verification,rollback}.md` + `evidence/`

## Model routing

| Work package | Model/effort | Owner | Reason |
|---|---|---|---|
| Packaging, guarded deploy, verification | Claude Opus 5 (Claude Code) | executor | Continuation session; MAIN review by ChatGPT Web |

## Dependencies

- VENT-002 remains `NOT READY FOR REAL DATA`; VENT-005 remains paused.
- PR #3 stays open and unmerged; this branch is stacked on `feat/VENT-002-runtime-data-binding`.

## Acceptance criteria

- [x] Standalone demo unchanged after packaging refactor (pixel-identical evidence, 6/6).
- [x] Payloads built deterministically and validated locally (static + namespaced-CSS harness).
- [x] Guard blocks every call except the two authorized creates and manifest-scoped deletes.
- [x] Read-only preflight passes (no collision, protected baseline matches plan).
- [x] Exactly two creates executed and verified by re-read (widget `b9fa9280-…`, dashboard `b9ff4d70-…`).
- [x] Live UI verified at 1920 and 390 (iframe) for all four states; screenshots captured.
- [x] Regression: protected dashboards/bundle unchanged, asset/device counts unchanged.
- [ ] ChatGPT Web review.

## Required evidence

- [x] `docs/ventilation/deployment/evidence/vent006_baseline_pre_mutation.json`
- [x] `vent006_manifest.json`, `vent006_regression.json`, `vent006_ui_verification.json`, screenshots.

## Gate

`active — visual refinement (APPROVED — VENT-006 CONTROLLED VISUAL REFINEMENT UPDATE)` only after creates, UI verification and regression pass.
Never `APPROVED — IMPLEMENTATION READY`.

## Ownership

### Mutable files

`deploy/thingsboard/`, `dashboard/` (packaging refactor only), `tests/`,
`docs/ventilation/deployment/`, this record.

### Browser/runtime session

Headless Firefox sessions started by the scripts; coordination locks `thong-gio.lock` and
`deploy.lock` in `/home/siba-iot-2/thingsboard-docker/docs/phoi-hop/khoa/` during execution.

## Handoff log

- 2026-09-17 14:33: agent's own `execute` call was blocked by Claude Code auto-mode permission
  (production deploy). No mutation had been sent. The user ran
  `deploy_vent_demo.py execute --confirm-create` locally at 14:38.
- Creates, read-back verification, regression and live UI verification all passed.
- Two minor visual drifts found (TB global typography on h2/b; dashboard toolbar FAB overlaps
  the DEMO badge). Fix requires an UPDATE of the created artifacts: outside this approval, not
  performed. See `docs/ventilation/deployment/vent006_verification.md`.

- 2026-09-17: `APPROVED — VENT-006 DEMO DEPLOYED` and `APPROVED — VENT-006 CONTROLLED VISUAL
  REFINEMENT UPDATE`. Repository fix: TB typography reset scoped to `.vent-demo-root`; header
  right reservation for the toolbar FAB (hideToolbar rejected after read-only `?hideToolbar=true`
  probe showed an edit FAB covering the badge). Only the widget type needs an update.

## Notes

- Platform trap found: `GET /api/widgetType?fqn=` needs the `tenant.`/`system.` prefix;
  unqualified lookup returns 400, not 404.
