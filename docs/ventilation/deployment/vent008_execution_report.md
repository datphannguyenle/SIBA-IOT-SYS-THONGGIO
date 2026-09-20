# VENT-008 — Controlled isolated demo update

20/09/2026 · Source deployed: `4cb5eb2` · branch `feat/VENT-008-live-demo-v03`.

## Result

**LIVE DEMO VERIFIED — ready for visual review.** Not production data readiness.

- Dashboard: `DB-30-VEN-DETAIL-V1-DEMO`, `b9ff4d70-b26a-11f1-83ad-9912edc644d2`, version **2**.
- Widget: `tenant.siba_vent_demo.vent_demo_view`, `b9fa9280-b26a-11f1-83ad-9912edc644d2`, version **3**.
- Five states: overview, monitoring, history, alarms, 224 read-only settings.
- URL on this host: http://localhost:8080/dashboards/b9ff4d70-b26a-11f1-83ad-9912edc644d2
- Private-network URL: http://100.86.144.207:8080/dashboards/b9ff4d70-b26a-11f1-83ad-9912edc644d2
- Local login endpoint returned HTTP 200; login and dashboard load verified in fresh Firefox sessions.
  Remote clients still need network access and their own valid login; their connectivity is not proven here.

## Authorization and scope

Latest user instruction authorizes continuing the current checkpoint and completing this dashboard;
the user additionally requested modern online references and original imagery applied to the UI.
Only the two existing isolated demo objects were updated. No production implementation gate was
self-granted, no PR merged, no entity/provisioning/PLC/device mutation, and no shared bundle update.

## Execution audit

1. Source, builder, read-only boundary and tests reviewed; initial 50-test baseline expanded to 67 tests.
2. First widget POST returned 500 because embedded original PNG exceeded the database varchar(1000000)
   limit. Stopped immediately. GET reconciliation proved widget/dashboard fingerprints and protected
   snapshot unchanged. No dashboard POST in this failed attempt.
3. Original PNG preserved. Same-resolution WebP encoding is **162478 bytes**; complete descriptor
   **327490 characters**. Builder now rejects descriptors over 900000 characters before any write.
4. New explicit `webp` run after reconciliation: exactly two successful POST updates, widget then dashboard.
   Versions 2→3 and 1→2. No create/delete calls. Do not describe the whole turn as only two attempted POSTs:
   there was one earlier rejected request plus the two successful updates.
5. GET read-back matches intended widget descriptor/configuration. All protected dashboard versions/hashes,
   shared bundle membership and tenant asset/device/dashboard/widget counts match the before snapshot.

Evidence under `evidence/`:

- `vent008_execution.json`, `vent008_initial_reconciliation.json` — failed attempt and no-change proof.
- `vent008_before_update_webp.json` — exact pre-update rollback objects and tenant baseline.
- `vent008_execution_webp.json` — successful action journal/source commit.
- `vent008_regression_webp.json` — payload equality/protected regression PASS.

## Verification

- `python3 -m unittest discover -s tests -q`: **67/67 PASS**, including null/zero, enum boundaries,
  missing history, Barn context, same-state recovery, chart gaps/scales, actual fan movement and
  reduced-motion preference, 224 read-only settings, no write/secret UI surface, embed/load artwork,
  oversized payload rejection, exact demo targets, indeterminate-write non-retry, reverse-order
  rollback and refusal to overwrite concurrent edits (offline mocks).
- `build_vent_demo.py --check`, `git diff --check`: PASS at handoff.
- Twenty standalone viewport/state checks and screenshots: measured 1920×1080,1366×768,820×1180,390×844.
- Twenty live viewport/state checks: same actual inner dimensions, no page/widget horizontal overflow.
  Original WebP loaded at 1536×1024 in every overview. Fan transform changes over time on every detail view.
  All four Barn navigation checks select ND2-2 without leaking ND2-1 readings, then recover the sample
  within the same detail state.
- Final live report: `vent008_ui_verification_20260920T074059+0700.json` — **ok: true**.
- Earlier report `vent008_ui_verification_20260920T073920+0700.json` had all 20 state checks passing but
  failed a verifier label comparison (`ND2-2 DEMO` vs heading `ND2-2`). Corrected the verifier to compare
  the actual label node to the heading; no UI mutation was needed. The failed report is retained.
- MAIN visually inspected live overview/history and mobile settings, plus standalone detail/mobile overview.
  `vent008-*.png` live captures accompany the report. Screenshots prove sampled states, not every browser/device.

## Reuse and imagery

`docs/ventilation/dashboard/ui_standard_v1.md` documents the reference UI boundaries;
`modern_reference_review.md` links Grafana, IBM Carbon and ThingsBoard primary references.
`dashboard/assets/README.md` records the built-in imagegen prompt/provenance. Original PNG retained,
optimized WebP embedded locally. The concept illustration is labelled, not an installation drawing.

## Rollback

If rollback is authorized/needed, acquire shared deployment lock and use:

```text
python3 deploy/thingsboard/update_vent_demo.py rollback --confirm-rollback --run-id webp
```

It restores previous dashboard configuration first, then previous widget content. Fingerprints must
still match this run's verified writes; concurrent changes stop rollback. No deletion or blind retry.
Rollback logic has offline guard tests; actual rollback was **not executed** on the working live demo.

## Remaining boundaries

VENT-002 remains not ready for real-data implementation; VENT-005 remains paused. Contract v0.3 is
an interface template, not proof of physical PLC sources. Production telemetry/aliases, freshness,
feedback provenance, alarm scope/history/export and deployment still require direct evidence/gates.
No screen-reader or real touch-device audit; Firefox headless mobile emulation is not a physical phone.
The reusable UI is implemented; the full physical ventilation system is not claimed complete.

## Orchestration

Luna low completed bounded inventory. Terra medium prepared UI and independent verification code,
then both delegates hit usage limits. MAIN checked source, corrected test/animation/navigation issues,
handled imagegen, safe update, live verification and handoff locally. No automatic expensive model
fallback or effort escalation. Imagegen influenced only original illustrative artwork, not status data.
