# VENT-008 checkpoint — 20/09/2026

## STATUS

Review; **isolated demo UPDATED and live browser VERIFIED**. Resume from actual worktree and
live object versions, not from older VENT-003 instructions. Branch: `feat/VENT-008-live-demo-v03`.

Latest source commit: `4cb5eb2`. At 07:38 +07, two successful updates: widget version 3,
dashboard version 2, all five states; payload equality and protected regression PASS.
See `vent008_execution_webp.json` / `vent008_regression_webp.json`. **Do not execute again.**
Initial attempt HTTP 500 exceeded descriptor varchar(1000000); GET proved both original
objects unchanged. Journal and reconciliation preserved. WebP encoding is 162478 bytes,
original PNG retained. 67/67 tests PASS. Live verifier completed: 20 state/viewport checks
and 4 Barn navigation/recovery checks PASS. Final report:
`docs/ventilation/deployment/vent008_execution_report.md` with exact evidence filenames.

## MODELS USED

- MAIN: integration, source review, generated asset, guard scripts, verification and delivery.
- Luna / low: bounded read-only checkpoint inventory completed.
- Terra / medium: app/CSS improvements and independent tests/verifier preparation.
- Both Terra agents reached usage limit after saving their changes. MAIN reviewed and
  continued locally; do not restart them automatically or claim they finished verification.
- External imagegen: original barn illustration; no Stitch redesign or third-party assets.

## FINDINGS / EVIDENCE

- Starting HEAD `7f2bc3e`; v0.3 contract, 265 variables/224 settings already implemented locally.
- Existing live demo was widget version 2, dashboard version 1, four states. Read-only
  preflight confirmed same two IDs and no other dashboard references this namespace.
- Fixed actual 390px settings overflow (wrapper min-width), Barn selection silently showing
  ND2-1, separately normalized temperature curves, and Firefox fan animation requiring
  explicit from/to rotation keyframes.
- Final source/build passed 67 tests, including two offline reverse-rollback/concurrent-edit cases.
- 20 standalone captures at 1920×1080,1366×768,820×1180,390×844 in dashboard/evidence;
  actual viewport measurements in vent008_capture.json. Captures refreshed after chart refinement.

## CHANGES

UI app/CSS, original PNG plus embedded optimized WebP in dashboard/assets, builder state params and resize,
tests, reference/reuse docs; new `update_vent_demo.py` and `verify_vent008_ui.py`.
User's original `vent008_preflight_live_backup.json` preserved unchanged.

## TESTS

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` — last completed
67/67 PASS, 11.789 seconds. Includes actual motion/reduced-motion, missing history,
safe search inputs, exact demo IDs, timeout non-retry, reverse rollback/concurrent-edit guards,
descriptor size budget and embedded original artwork. Actual live rollback was not executed.

## UNCERTAIN / RISKS

Fresh completion audit 20/09/2026 12:48 +07: demo still matches deployed source, but candidate
controller/system names return 404, target profiles are absent in the inspected profile list,
pilot relations have no ventilation controller, and all 265 PLC source mappings remain blank.
See `docs/ventilation/deployment/vent008_completion_audit.md`. Await concrete owner/PLC evidence;
do not substitute another UI polish loop for full-system completion. Blocked audit count: 1.

Full live five-state browser verification and API regression passed. Physical-data readiness is not proven.
PLC source/mapping and runtime freshness/alarms/export not promoted; VENT-002 not ready,
VENT-005 paused. Never present illustrative building topology as physical installation.
Remote PR #3 remains open on older branch; no merge or branch rewriting authorized here.

## NEXT RECOMMENDED ACTION

1. User/ChatGPT Web visual review of the running five-state demo and reusable UI standard.
2. If needed, GET-only reverify: `update_vent_demo.py verify --run-id webp`; never execute this run again.
3. Task is in `.codex/tasks/review/VENT-008-live-demo-v03.md`. Check shared lock directory
   before any new work; final handoff releases this task's locks.
4. Physical integration requires evidence and separate gate; do not infer it from successful demo tests.
5. Original full-system goal is not declared complete merely because this UI/demo milestone passed.
