# VENT-007 — Align Ventilation Data Contract v0.2 With Dashboard

## Status

`active — implementation checkpoint (tests pass); docs/screenshot review pending`

## Objective

Bring the repository dashboard/data model in line with Data Contract v0.2 (APPROVED PROJECT
INTERFACE TEMPLATE) and the decisions of 2026-09-17, without touching live ThingsBoard.

## Scope

- Copy contract v0.2 into `docs/ventilation/contract/` (JSON present; Excel pending from user).
- Alignment report current model ↔ contract; exact files/keys list.
- After review: fixture, adapter, renderer (incl. read-only `vent_settings`), tests, screenshots on this branch.

## Forbidden scope

Live ThingsBoard changes or deployment; PLC/Gateway/Modbus integration; resuming VENT-005;
editing VENT-002 evidence (`config/ventilation_data_contract.json`, `docs/ventilation/runtime/*`);
write/RPC/parameter controls in `vent_settings`.

## Inputs

- `docs/ventilation/contract/SIBA_Ventilation_Agent_DataContract_v0.2.json` (sha256 f25cd7ab…60db)
- `docs/ventilation/contract/contract_v0.2_decisions.md`

## Expected outputs

- `docs/ventilation/contract/vent007_alignment_report.md`
- Updated fixture/adapter/app/tests/docs/evidence (after review)

## Model routing

| Work package | Model/effort | Owner | Reason |
|---|---|---|---|
| Alignment + implementation | Claude Opus 5 (Claude Code) | executor | MAIN review by ChatGPT Web |

## Dependencies

- Stacked on `feat/VENT-006-tb-demo-deploy` @ `018d625`.
- VENT-002 NOT READY FOR REAL DATA (plc_source unconfirmed); VENT-005 PAUSED.

## Acceptance criteria

- [x] Contract JSON copied verbatim; decisions recorded separately.
- [x] Alignment report with key-by-key comparison and exact file list.
- [x] Review of report: owner decisions 1–13 (2026-09-17).
- [x] Per-device FAULT and stageCount removed; fanStage only.
- [x] controllerOnline/dataQuality classified PLATFORM_DERIVED.
- [x] New monitoring keys classified and added.
- [x] `vent_settings` read-only state (224 cells, default `--`).
- [x] Fixture v2/tests updated (48 pass); standalone screenshots regenerated (not yet visually re-reviewed after last fixes).

## Required evidence

- [ ] Tests, `git diff --check`, secret scan, screenshots.

## Gate

Code changes only after the alignment report is reviewed. Live deployment requires a separate task.

## Ownership

### Mutable files

`docs/ventilation/contract/`, `fixtures/ventilation/`, `widgets/`, `dashboard/`, `tests/`,
`deploy/thingsboard/build*` (local build only), dashboard docs, this record.

### Browser/runtime session

Local headless Firefox only.

## Handoff checkpoint — 2026-09-17 (user token limit)

Done on this branch:
- `docs/ventilation/contract/contract_v0.2_decisions.json` (machine-readable decisions) and
  `tools/build_contract_module.py` → generated `widgets/ventilation-contract-v02.js` (single key source, `--check`).
- `widgets/ventilation-adapter.js` rewritten for contract keys: enums, run 0/1, flags, NOT_CONFIGURED via
  `mapping.notConfigured`, PLATFORM_DERIVED block, classification, settings groups/matrices, 7 history keys.
- `fixtures/ventilation/demo.json` v2.0.0 (contract keys, uint16/float32, platform block, notConfigured,
  system fault only, PLC/PLATFORM alarms, settings `{}`, new adapterTestVariants).
- `dashboard/app.js` + `dashboard.css`: 5th tab `vent_settings` (read-only), system flags strip, operation
  grid, controller panel (fanStage only, platform tags), NOT CONFIGURED muted fan/pump, "Gió & nước" table.
- `index.html` loads the contract module; TB build (local only, NOT deployed) embeds it; `STATES` has 5 states.
- Tests: new `tests/test_contract_v02.py`; rewritten `test_dashboard_demo.py`, `test_dashboard_browser.py`;
  updated `test_thingsboard_widget_payload.py`. Full suite 48/48 OK.
- Standalone evidence regenerated incl. `vent-settings-1920/390.png`.

Remaining:
- Visually re-review regenerated screenshots after the final CSS/label fixes.
- Update docs: `docs/ventilation/dashboard/{canonical_view_model,fixture_schema,widget_inventory,state_navigation,visual_parity_report}.md`,
  `docs/ventilation/states/vent_detail.md`, new `docs/ventilation/states/vent_settings.md`.
- Note in `deploy/thingsboard/verify_vent_demo_ui.py` that it verifies the VENT-006 live build only.
- ChatGPT Web review. Live deploy of the 5-state build needs a separate approved task.

## Notes

- Excel template not found on this machine on 2026-09-17; user to add.
