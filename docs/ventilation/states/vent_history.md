# State `vent_history` — Lịch sử read-only

## Purpose

Inspect historical trends and samples without changing controller or alarm state.

## Planned content

- Time-window selector owned by dashboard/UI state only.
- Trends for indoor/outdoor/feel temperature and humidity after mappings are confirmed.
- Conditional trends for air speed, airflow and water consumption after source/unit/scale
  confirmation.
- Historical table with timestamp, semantic label, value, unit and data-quality marker.
- Built-in ThingsBoard export only if the deployed edition/widget supports it and export is
  verified read-only.

## Evidence classification

- **confirmed document capability** — HMI has stored-data table, date query, Excel export,
  and charts for indoor/outdoor temperature and humidity (PDF pp. 18–26).
- **uncertain target capability** — target ThingsBoard retention, export setting, timezone,
  aggregation and permissions.
- **uncertain mapping** — all production semantic keys and history availability.

## Data-quality behavior

- Missing samples create gaps; never interpolate to zero.
- Stale/current applies to latest-value context; historical points retain their timestamp
  and quality when available.
- Timezone and aggregation label must be visible once confirmed.

## Explicit exclusions

No custom backend exporter, data correction, attribute write, parameter edit or device
command in V1.
