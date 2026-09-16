# Reusable component inventory

## Classification

| Candidate | Classification | Evidence | VENT-001 decision |
|---|---|---|---|
| `dashboard-theme.css` | confirmed external general shell | `/home/siba-iot-2/thingsboard-docker/tb-custom-ui/dashboard-theme.css`; external `docs/nen-tang/style-siba.md` | proposed reuse; do not copy/modify in this task |
| `header_bar` | confirmed external shared component | external `widgets/header_bar.*`; state tabs preserve state params | proposed reuse with ventilation settings only |
| `footer_bar` | confirmed external shared component | external `widgets/footer_bar.*` | proposed reuse |
| `kpi_stat_card` | confirmed external shared component | external `widgets/kpi_stat_card.*`; role-based values and missing/stale guards | proposed reuse for confirmed fields only |
| System time-series chart | confirmed external pattern | external `build_dashboard_deo.py` derives system default config | proposed pattern; datasource TBD |
| System alarm table | confirmed external pattern | external `build_dashboard_deo.py` uses read-only alarm table | proposed read-only pattern |
| State entity navigation | confirmed external pattern | external `deo_barn_grid.js`, `header_bar.js`, builder aliases | proposed pattern; ventilation param name TBD |
| `deo_barn_grid` | business-specific | `deo_*` status logic and Deodorizer keys | do not reuse implementation; only exception-first concept |
| `deo_synoptic` | business-specific | chemical process topology/equipment | do not reuse implementation; only stale-safe/read-only concept |
| `deo_param_form` / `deo_audit_log` | prohibited for V1 | parameter/audit behavior is outside V1 | exclude |
| `chem_station` | business-specific | chemical station only | exclude |

## Reuse constraints

- **confirmed** — External architecture reserves `vent_*` and a separate ventilation
  builder rather than importing another domain builder. Evidence: external
  `docs/nen-tang/kien-truc.md`.
- **confirmed** — Theme owns panel shell; widgets own content; canvas chart colors belong
  in widget settings. Evidence: external `docs/nen-tang/style-siba.md`.
- **derived** — Ventilation should reuse interfaces/patterns, not copy `deo_*` business
  logic.
- **uncertain** — Source packaging/import path for this new repository has not been
  established and is not part of VENT-001.

## Explicit non-claims

- No reuse percentage is claimed.
- No shared component is claimed available inside this repo today.
- No external source is modified or vendored by VENT-001.
