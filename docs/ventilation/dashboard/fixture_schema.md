# Fixture schema

`fixtures/ventilation/demo.json` is deterministic and must carry `demo: true`. Its top
level fields are `fixtureVersion`, `generatedAt`, configurable `badgeLabel`, `scope`,
`summary`, `barns`, `latest`, `history` and `alarms`.

Latest values use `{value, unit?, quality, ts?}`. Allowed quality values are `CURRENT`,
`STALE`, `OFFLINE`, `UNKNOWN`. Missing values are explicit JSON `null`, rendered as `--`,
and never coerced to zero. The fixture intentionally includes stale louver feedback,
unknown fan/pump feedback, an offline Barn, an unknown Barn, and a missing history point.

All engineering-looking values and alarms are demonstration data only. `% demo` on louver
positions is deliberate because the production 0–10 V scale remains unconfirmed.
