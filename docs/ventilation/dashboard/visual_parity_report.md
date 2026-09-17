# Visual parity report

## Result

The repository demo reproduces the approved compact SIBA Khử mùi visual grammar: shell
colors, dark canvas, flat bordered panels, compact cyan header, persistent amber demo
badge, tab underline, KPI density, responsive stacking, table styling and local overflow.
Ventilation-specific topology and labels are new and remain read-only.

## Evidence set

- Baseline: `docs/he-thong/khu-mui/desktop-fit-production-2026-09-12/live-1920/`
  and `live-390/` in the existing SIBA workspace.
- Generated demo evidence: `docs/ventilation/dashboard/evidence/` for all four desktop
  states plus mobile `default` and `vent_detail`.

## Deliberate differences

- Standalone evidence includes a preview-only ThingsBoard shell; the dashboard content has
  no internal sidebar.
- All displayed values are visibly marked fixture/demo and are not runtime claims.
- Production aliases, alarm controls/export and data source bindings are absent by design.

## Review limits

Pixel identity is not claimed because the repository demo is standalone HTML rather than
the Angular/Material runtime. Token, hierarchy, spacing, state and responsive parity are
the acceptance targets.
