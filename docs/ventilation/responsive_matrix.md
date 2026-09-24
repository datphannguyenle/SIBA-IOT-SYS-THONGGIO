# Responsive matrix

Baseline `SIBA-OPS-DARK-1.0` has runtime evidence at 1366×768, 1536×734 and 390×844.
The wider 1920×1080 and tablet 820×1180 entries remain compatibility targets.

| State | 1920×1080 | 1600×960 | 820×1180 | 390×844 |
|---|---|---|---|---|
| `default` | KPI row + wide Barn grid + alarm summary | Same hierarchy with denser grid | KPI wrap; 2-column or list grid | One-column cards/list; no root horizontal scroll |
| `vent_detail` | KPI + schematic/summary cluster + trend preview | Primary operational cluster above fold where feasible | KPI wrap; schematic then summary | One column; local schematic pan allowed |
| `vent_history` | Chart/table split or stacked | Chart then bounded table | Stacked chart/table | One column; simplified legend; table local scroll only |
| `vent_alarms` | Full table | Full table with bounded columns | Reduced visible columns/detail drill-in | Priority fields only; local table scroll if unavoidable |

## Cross-viewport invariants

- Shared header keeps selected entity and active state.
- `--`, `UNKNOWN`, `STALE` and `OFFLINE` remain readable, not color-only.
- No control element appears at any breakpoint.
- No page-level horizontal overflow.
- Internal scrolling/panning must be explicit and restricted to dense schematic/table areas.
- Touch targets apply only to navigation/filter actions, never device mutations.

## Reference evidence

VENT-012 live verification passed all five dashboard screens at 1366×768 and 1536×734,
plus overview at 390×844. Evidence: `deployment/evidence/vent012_ui_verify.json`. Detail uses
one bounded page scroll and no nested widget scroll; other desktop states fill the viewport.
