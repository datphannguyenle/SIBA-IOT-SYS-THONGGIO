# VENT-008 checkpoint — 20/09/2026

## STATUS

Active; UI completion, isolated demo deployment pending. Resume from actual worktree and
live object versions, not from older VENT-003 instructions. Branch: `feat/VENT-008-live-demo-v03`.

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
- 64 tests passed before final chart-width refinement. Must rerun after latest source/build.
- 20 standalone captures at 1920×1080,1366×768,820×1180,390×844 in dashboard/evidence;
  actual viewport measurements in vent008_capture.json. Refresh after latest chart change.

## CHANGES

UI app/CSS, embedded original PNG in dashboard/assets, builder state params and resize,
tests, reference/reuse docs; new `update_vent_demo.py` and `verify_vent008_ui.py`.
User's original `vent008_preflight_live_backup.json` preserved unchanged.

## TESTS

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` — last completed
64/64 PASS, 14 seconds. Includes actual motion/reduced-motion, missing history,
safe search inputs, exact demo IDs, timeout non-retry, embedded original image.

## UNCERTAIN / RISKS

No live update yet at this checkpoint. Full live five-state browser verification pending.
PLC source/mapping and runtime freshness/alarms/export not promoted; VENT-002 not ready,
VENT-005 paused. Never present illustrative building topology as physical installation.
Remote PR #3 remains open on older branch; no merge or branch rewriting authorized here.

## NEXT RECOMMENDED ACTION

1. Final build + 64-test suite + diff/secret/mutation checks; regenerate screenshots.
2. Save source commit. Acquire shared `deploy.lock` (only own `thong-gio.lock` currently held).
3. Fresh preflight, then `update_vent_demo.py execute --confirm-update` only under latest
   user authorization for current-checkpoint isolated demo; exactly existing widget/dashboard.
4. New updater writes backup+execution journal BEFORE network writes; if record already
   exists inspect it and GET live objects before any retry. Never duplicate uncertain writes.
5. Run new live verifier, inspect screenshots and actual browser interactions. Keep old verifier historical.
6. Update source docs/task/profile and evidence, commit/push existing VENT-008 branch; no PR merge.
7. Release owned locks only after handoff. Current source goal remains active until verified usable UI.
