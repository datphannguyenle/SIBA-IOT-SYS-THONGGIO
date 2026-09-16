# Responsive matrix

All entries are design targets, not runtime verification.

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

External Khử mùi runtime passed 1600×960 and 390×844 with no root horizontal overflow and
local schematic pan. Ventilation at all four targets remains **unverified** until a future
approved implementation has runtime evidence.
