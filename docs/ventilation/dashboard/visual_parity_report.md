# Visual parity report (VENT-007 / Data Contract v0.3)

## VENT-008 local refinement — 20/09/2026

Standalone parity: PASS for the bounded refinement. Navy/cyan flat SIBA shell, original
panel radius, white preview sidebar and teal header remain. MAIN inspected new desktop
overview/detail/history and mobile overview captures; all 20 captures passed measured
viewport/overflow checks. New original barn illustration is labelled conceptual, below
Barn selection; it does not replace status graphics. Reference review and provenance:
`modern_reference_review.md`, `dashboard/assets/README.md`.

Source tests: 67/67 PASS including same-state Barn recovery, embedded image load,
actual fan animation/reduced-motion, 224 settings and 390px layout. Live ThingsBoard
verification is separate; do not treat this standalone result as deployment evidence.
The subsequent VENT-008 live verification also passed all 20 measured viewport/state checks
and all four Barn-navigation checks; see `../deployment/vent008_execution_report.md`.

The VENT-007 evidence section below is historical; measured VENT-008 captures supersede
its unverified mobile-size claims. Contract data/fixture values remain unchanged.

## Result

`VISUAL PARITY: PASS` (Updated for VENT-007, 2026-09-18).

The repository demo aligns fully with Data Contract v0.3 while maintaining the established
compact SIBA visual grammar: dark theme canvas, flat bordered panels, cyan active headers,
persistent amber demo badge, compact typography, and strict read-only boundaries.

## Evidence Set

Standalone headless Firefox captures in `docs/ventilation/dashboard/evidence/`:
- `default-1920.png`: Farm overview (1920x1080) with barn identity badges, stage integer, and environmental KPIs.
- `default-390.png`: Mobile overview (390x844) with responsive stacking.
- `vent-detail-1920.png`: Single-barn monitor (1920x1080) with 6-fan/2-pump schematic, muted NOT CONFIGURED equipment, system fault strip, and controller summary.
- `vent-detail-390.png`: Mobile barn monitor (390x844).
- `vent-history-1920.png`: Six-hour history curves and "Gió & nước" telemetry table.
- `vent-alarms-1920.png`: Read-only alarm table with explicit `PLC` vs `PLATFORM` source classification.
- `vent-settings-1920.png`: New 5th state (1920x1080) showing the 224 read-only settings grid across functional groups, defaulting to `--`.
- `vent-settings-390.png`: Mobile settings view (390x844) with smooth horizontal table scroll.

## Key Visual Alignments in VENT-007

1. **5th State (`vent_settings`)**:
   - Added 5th tab "Cài đặt" to the header navigation.
   - Categorized read-only settings matrix (Nhiệt độ, Thời gian, Cấp thông gió, Quạt, Bơm, Cửa khí, Hiệu chỉnh).
   - All 224 settings cells render `--` in demo/baseline, with no input fields, sliders, or write buttons.
2. **Equipment & Fault Semantics**:
   - Muted display with clear "NOT CONFIGURED" badge for unconfigured hardware (e.g. Quạt 06).
   - Removed per-fan fault color overrides; system hardware fault is consolidated in the system fault strip (`equipmentFaultActive`).
3. **Controller Summary**:
   - `fanStage` is displayed as an absolute integer (e.g. `4`) without a synthetic denominator (`4 / 6` removed).
   - Platform connectivity tags (`controllerOnline`, `dataQuality`) are explicitly marked `PLATFORM`.
4. **ThingsBoard Typography Neutralization**:
   - Explicit CSS resets neutralize `mat-typography` overrides in ThingsBoard runtime, guaranteeing consistent font sizes and line heights.
   - Header margin reserved for ThingsBoard toolbar floating action button (FAB).
