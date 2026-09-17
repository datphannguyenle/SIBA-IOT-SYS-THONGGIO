# Fixture schema

`fixtures/ventilation/demo.json` is deterministic and must carry `demo: true`. Its top
level fields are `fixtureVersion`, `generatedAt`, configurable `badgeLabel`, `scope`,
`summary`, `barns`, `latest`, `history`, `alarms` and bounded `adapterTestVariants`.

Latest values use `{value, unit?, quality, ts?}`. Allowed quality values are `CURRENT`,
`STALE`, `OFFLINE`, `UNKNOWN`. Missing values are explicit JSON `null`, rendered as `--`,
and never coerced to zero. The fixture intentionally includes stale louver feedback,
unknown fan/pump feedback, an offline Barn, an unknown Barn, and a missing history point.
Each Barn carries an explicit `identity`: `PILOT` (`ND2-1`, a confirmed live Barn whose
ventilation state is simulated), `LIVE_BARN_SIMULATED_STATE` (`ND2-2`…`ND2-4`, confirmed
live Barns with no verified ventilation controller), or `SYNTHETIC` (`DEMO-05`/`DEMO-06`,
layout-only, `synthetic: true`). The adapter treats a missing or unknown identity as
`SYNTHETIC`, and the overview shows the identity tag on every card. Alarm originators say
`bộ điều khiển demo` rather than a provisioning name, because `VEN-PLC-01` is still
blocked in VENT-005.

The raw `latest` object deliberately retains legacy snake-case input names so the adapter
boundary is exercised. Its output uses only Rev A canonical names. Run and fault booleans
are separate and preserve false/null. Fixture stage-count examples 6 and 9 are simulated
capability cases, not production configuration evidence.

`adapterTestVariants` holds `latest` patches consumed only by the browser tests:
`step` (STEP, 3 / 6), `vfd` (VFD, 5 / 9), `unknownStageCount` (stage without
denominator), `zeroStage` (0 / 6) and `edgeCases`, which covers zero, false, null, `STALE`,
`OFFLINE`, `UNKNOWN`, fault-over-run precedence and non-boolean run/fault. Keys listed in
`_edgeCasesMissing` are deleted to exercise truly missing telemetry.

All engineering-looking values and alarms are demonstration data only. `% demo` on louver
positions is deliberate because the production 0–10 V scale remains unconfirmed.
