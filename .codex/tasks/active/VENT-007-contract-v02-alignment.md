# VENT-007 — Align Ventilation Data Contract (v0.2/v0.3) With Dashboard

## Status

`review — implementation and documentation complete; 49/49 tests pass; ready for ChatGPT Web review`

## Objective

Bring the repository dashboard/data model in line with Data Contract v0.3 (superseding v0.2 as
the CURRENT ventilation interface) and project decisions, preserving v0.2 as historical evidence,
without touching live ThingsBoard.

## Scope

- Copy/preserve contract v0.2 into `docs/ventilation/contract/` as historical baseline.
- Establish Data Contract v0.3 as current interface:
  - Architecture: Separate PLC from deodorization system.
  - PLC mirror address block: `D550–D959` (shifted -450 from v0.2 `D1000–D1409`).
  - Modbus Holding Registers: `4x-1 .. 4x-410` (unchanged).
  - 265 keys, types, widths, enums, dashboard semantics unchanged.
  - Generate template Excel `SIBA_Ventilation_PLC_HMI_TB_Mapping_TEMPLATE_v0.3.xlsx`.
- Alignment report current model ↔ contract v0.2/v0.3; exact files/keys list.
- Generated contract module `widgets/ventilation-contract-v03.js` from v0.3 JSON + decisions.
- Fixture v2.0.0, adapter, renderer (incl. read-only `vent_settings`), 5 states.
- Tests (49/49 pass), standalone screenshot evidence regenerated and reviewed.
- Full documentation update across dashboard specifications and states.

## Forbidden scope

Live ThingsBoard changes or deployment; PLC/Gateway/Modbus integration; resuming VENT-005;
editing VENT-002 evidence (`config/ventilation_data_contract.json`, `docs/ventilation/runtime/*`);
write/RPC/parameter controls in `vent_settings`.

## Inputs

- `docs/ventilation/contract/SIBA_Ventilation_Agent_DataContract_v0.3.json` (sha256 `6cce2e...7244`)
- `docs/ventilation/contract/SIBA_Ventilation_PLC_HMI_TB_Mapping_TEMPLATE_v0.3.xlsx`
- `docs/ventilation/contract/contract_v0.3_decisions.json` / `.md`
- `docs/ventilation/contract/SIBA_Ventilation_Agent_DataContract_v0.2.json` (historical baseline)

## Expected outputs

- `docs/ventilation/contract/vent007_alignment_report.md`
- Updated fixture/adapter/app/tests/docs/evidence on branch `feat/VENT-007-contract-v02-alignment`.

## Model routing

| Work package | Model/effort | Owner | Reason |
|---|---|---|---|
| Alignment + implementation + docs | Gemini 3.8 Flash | executor | MAIN review by ChatGPT Web |

## Dependencies

- Stacked on `feat/VENT-006-tb-demo-deploy` @ `018d625`.
- VENT-002 NOT READY FOR REAL DATA (plc_source unconfirmed); VENT-005 PAUSED.

## Acceptance criteria

- [x] Contract JSON v0.3 established as current source; v0.2 preserved verbatim.
- [x] Excel template v0.3 created and formatted with 265 variables and README.
- [x] Alignment report with key-by-key comparison and owner decisions recorded.
- [x] Per-device FAULT and stageCount removed; fanStage only.
- [x] controllerOnline/dataQuality classified PLATFORM_DERIVED.
- [x] New monitoring keys classified and added.
- [x] `vent_settings` read-only state (224 cells, default `--`).
- [x] Fixture v2.0.0 and tests updated (49 pass); standalone screenshots regenerated and reviewed.
- [x] Documentation updated (`canonical_view_model.md`, `fixture_schema.md`, `widget_inventory.md`, `state_navigation.md`, `visual_parity_report.md`, `vent_detail.md`, `vent_settings.md`).
- [x] Prominent note added to `deploy/thingsboard/verify_vent_demo_ui.py` that it verifies VENT-006 live only.
- [x] Code checks, `git diff --check`, and secret scan complete.

## Required evidence

- [x] Tests: 49/49 pass (`python3 -m unittest discover -s tests`).
- [x] `git diff --check`: clean (no whitespace or conflict markers).
- [x] Secret scan: passed (no passwords, tokens, or credentials).
- [x] Screenshots: all 8 states in `docs/ventilation/dashboard/evidence/` reviewed.

## Gate

Implementation and documentation complete on `feat/VENT-007-contract-v02-alignment`.
READY FOR CHATGPT WEB REVIEW. Live deployment of the 5-state build requires a separate approved task.

## Ownership

### Mutable files

`docs/ventilation/contract/`, `fixtures/ventilation/`, `widgets/`, `dashboard/`, `tests/`,
`deploy/thingsboard/build*` (local build only), dashboard docs, this record.

### Browser/runtime session

Local headless Firefox only.
