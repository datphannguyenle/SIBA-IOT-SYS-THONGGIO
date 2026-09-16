# Handoff — VENT-001

## STATUS

`review`

Baseline, evidence package and four-state design plan are complete. No production
implementation or runtime mutation was performed. Gate remains pending reviewer decision.

## MODELS USED

- MAIN — preferred/requested route GPT-6 Astra (`gpt-6-astra`) / `ultra`; owned scope,
  architecture, evidence integration, conflict resolution, final package review and gate
  boundary. Runtime model identity was not independently exposed by a tool, so this is
  recorded as requested routing rather than a measured runtime fact.
- `gpt-5.6-luna` / `low` — repository inventory and checklist evidence.
- `gpt-5.6-luna` / `low` — PDF/document structured extraction with page references.
- `gpt-5.6-terra` / `medium` — read-only trace of external Khử mùi builder/widgets/runtime
  evidence. No escalation to high.

## FINDINGS

- **confirmed** — Target repo had no production code, ThingsBoard export, mapping or
  runtime artifact before VENT-001 outputs.
- **confirmed** — PDF documents six fans, two pumps, two louver feedback signals, monitored
  environmental fields, alarm/history screens, 6-level step mode and 9-level VFD mode.
- **confirmed** — PDF does not supply PLC raw tags, engineering conversions, telemetry
  freshness or ThingsBoard schema.
- **confirmed external reference** — Khử mùi has reusable shell/header/footer/KPI and
  read-only chart/alarm/state patterns; `deo_*` logic remains domain-specific.
- **derived** — Selected-entity state navigation and separate `vent_*` specifications are
  suitable candidates, not approved implementation facts.
- **uncertain** — entity topology, alias scope, semantic mapping, air/flow/water source,
  fan/pump feedback provenance, alarms, retention and export capability.

## EVIDENCE

- Repository baseline: `docs/ventilation/repo_baseline.md`.
- Data contract: `config/ventilation_data_contract.json` and
  `docs/ventilation/data_dictionary.md`.
- Source document: *TÀI LIỆU KỸ THUẬT THIẾT BỊ ĐIỀU KHIỂN THÔNG GIÓ*, especially
  pp. 6, 8–26, 38–61.
- External design reference:
  `/home/siba-iot-2/thingsboard-docker/tb-custom-ui/deploy/build_dashboard_deo.py`,
  shared widgets/theme, and
  `/home/siba-iot-2/thingsboard-docker/docs/he-thong/khu-mui/ui-polish-production-2026-09-14/RESULT.md`.
- Topology and design classification: `entity_topology.md`,
  `design_system_baseline.md`, `reusable_components.md`.

## CHANGES

- Activated VENT-001 and prepared it for review.
- Added repository/reuse/runtime baselines.
- Added 21-field draft semantic data contract and dictionary.
- Added proposed entity topology with explicit evidence gaps.
- Added design-system baseline, four state briefs, responsive/acceptance matrices and
  widget plan.
- Added read-only safety audit.
- No JavaScript, Python, HTML, CSS, dashboard, widget, builder, deploy or ThingsBoard
  object was created.

## TESTS

- Required output file existence check.
- JSON parse/schema-field/unique-key/classification assertions with `jq`.
- Verified air speed, airflow, water and ventilation stage remain `uncertain`.
- `git diff --check`.
- Production-code extension scan: none.
- Raw PLC register binding pattern scan: none.
- Read-only mutation keyword review: matches occur only in prohibitions/audit/evidence gaps.
- Lifecycle and worktree diff review before commit.

## UNCERTAIN

- Runtime topology and per-Barn controller cardinality.
- All raw tags, types, scaling, range, cadence and stale thresholds.
- Fan/pump actual-feedback source.
- Air speed, airflow and water-consumption production calculation/source.
- Alarm schema/scope/retention and history/export availability.
- How external shared component source will be packaged into this repository.

## RISKS

- Implementing before mappings are confirmed could display fabricated zero/STOPPED states.
- Copying `deo_*` logic could import chemical-domain semantics into ventilation.
- Hard-coding 6 or 9 levels could misrepresent the controller’s active mode.
- External absolute evidence paths are machine-local; durable source documents/exports
  should be added or referenced stably before implementation.
- `APPROVED — DESIGN ONLY` has not been granted by this task.

## NEXT RECOMMENDED ACTION

ChatGPT Web reviews VENT-001 evidence/design outputs and decides whether to grant
`APPROVED — DESIGN ONLY`. Do not implement or deploy before that decision.
