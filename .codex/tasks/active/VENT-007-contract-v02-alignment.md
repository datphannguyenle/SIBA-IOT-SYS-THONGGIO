# VENT-007 — Align Ventilation Data Contract v0.2 With Dashboard

## Status

`active — alignment report delivered; awaiting review before code`

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
- [ ] Review of report (section 6 questions).
- [ ] Per-device FAULT and stageCount removed; fanStage only.
- [ ] controllerOnline/dataQuality classified PLATFORM_DERIVED.
- [ ] New monitoring keys classified and added.
- [ ] `vent_settings` read-only state.
- [ ] Fixture/tests updated; standalone screenshots regenerated.

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

## Notes

- Excel template not found on this machine on 2026-09-17; user to add.
