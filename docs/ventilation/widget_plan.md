# V1 widget plan — design only

## Proposed reuse

| Component/pattern | Purpose | Classification |
|---|---|---|
| `header_bar` | title, selected Barn, back/tabs, read-only status | confirmed external pattern; proposed reuse |
| `footer_bar` | scope/data-quality note | confirmed external pattern; proposed reuse |
| `kpi_stat_card` | confirmed latest values with units/freshness | confirmed external pattern; proposed reuse |
| `dashboard-theme.css` | SIBA panel shell and typography | confirmed external pattern; proposed reuse |
| System chart | read-only trends | confirmed external pattern; datasource uncertain |
| System alarm table | read-only alarm list | confirmed external pattern; schema/scope uncertain |

No component above currently exists in this repository. Packaging/import is deferred.

## Proposed new widget specifications

### `vent_barn_grid`

- Farm-level read-only navigator.
- Inputs: confirmed controller list, connectivity, data freshness, highest alarm and PLC
  mode.
- Preserves `OFFLINE`, `STALE`, `UNKNOWN` distinctions.
- Navigation only; no device action.

### `vent_synoptic`

- One-Barn schematic: six fans, two pumps, roof and side louvers.
- PLC feedback only; each item validates missing/stale independently.
- Display-only mode and current-level summary.
- Local mobile pan if geometry requires it.

### `vent_equipment_strip` — optional

- Use only if equipment labels/states cannot remain legible inside the schematic.
- Same feedback and freshness contract as `vent_synoptic`; it must not duplicate or
  independently reinterpret values.

## Prohibited V1 widgets

- `vent_control`;
- `vent_param_form`;
- RPC widget;
- write-capable widget;
- alarm action widget.

## Builder/state plan

A future approved implementation may use a separate ventilation builder and `vent_*`
widget family. VENT-001 creates no builder, widget, bundle entry, entity or dashboard.
