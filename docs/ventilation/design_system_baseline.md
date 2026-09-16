# Design-system baseline

## Proven external reference

The Khử mùi source/runtime reference lives outside this repository. Its reusable status is
therefore “confirmed external pattern, proposed VENT reuse”, not “available local code”.

### General/shared

- `dashboard-theme.css`: page background, panel shell, title and table styling.
- `header_bar`: dashboard title, selected entity, back navigation and state tabs.
- `footer_bar`: static scope/status copy.
- `kpi_stat_card`: role-based values, missing/stale guards and resize behavior.
- System time-series chart initialized from its default config and themed in settings.
- System alarm table configured read-only.
- Alias → selected state entity navigation pattern.

Evidence: external `docs/nen-tang/style-siba.md`, `docs/nen-tang/kien-truc.md`,
`tb-custom-ui/deploy/build_dashboard_deo.py`, and the corresponding shared widgets.

### Business-specific

- `deo_barn_grid`, `deo_synoptic`, `deo_param_form`, `deo_audit_log`, `chem_station`.
- Chemical process topology, equipment states, run-state precedence, parameter/audit
  behavior and Deodorizer/DosingStation aliases.

These implementations are not reused as ventilation components.

## Visual rules for design plan

- Use the SIBA shell/panel/typography hierarchy; do not create a parallel theme.
- Do not add an internal sidebar: ThingsBoard shell supplies global navigation; dashboard
  state tabs live in the shared header pattern.
- Overview prioritizes exception triage; detail prioritizes environmental state and
  equipment feedback.
- Missing `--`, `UNKNOWN`, `STALE` and `OFFLINE` remain visually and semantically distinct.
- Canvas chart styling must be configured through chart settings.
- Mobile schematic may pan horizontally inside its widget; page-level horizontal overflow
  is not acceptable.

## Responsive evidence and targets

- **confirmed external runtime** — Khử mùi passed 1600×960 and 390×844 without root
  horizontal overflow; local schematic pan was retained. Evidence: external
  `docs/he-thong/khu-mui/ui-polish-production-2026-09-14/RESULT.md`.
- **target, not verified** — Ventilation must cover 1920×1080, 1600×960, 820×1180 and
  390×844. See `responsive_matrix.md`.

## Risks

- External theme has legacy token names and domain/table overrides; do not modify globally
  during a ventilation-only task.
- `compactDeo` and all `deo_*` states are domain-specific.
- No shared code is currently stored in this repository, so reuse remains a conversion
  plan pending implementation authorization.
