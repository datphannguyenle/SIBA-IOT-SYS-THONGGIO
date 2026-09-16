# State `default` — Tổng quan trại

## Purpose

Giúp người vận hành nhận biết trong vài giây nhà nào cần chú ý trước khi mở chi tiết.
Đây là farm overview, không chứa schematic hoặc chi tiết của một Barn.

## Information hierarchy

1. Shared header: tên dashboard, Farm scope, data freshness summary.
2. Aggregate KPI row: chỉ hiện KPI có rollup và phạm vi đã **confirmed**.
3. Barn grid/list: connection, alarm severity, PLC mode và data-quality state.
4. Read-only active-alarm summary.
5. Shared footer: read-only scope and timestamp semantics.

## Data contract

- **uncertain** — Farm entity/alias and list of controllers.
- **uncertain** — Aggregate KPI keys/rollup source. No aggregate number may be computed in
  separate widgets or hard-coded.
- **uncertain** — Alarm scoping and propagation.
- **derived** — Grid can use exception-first ordering, based on the external Khử mùi
  pattern; ventilation precedence must be approved separately.

## Barn row/card states

Each row/card displays Barn/controller label plus independently sourced:

- connectivity: `ONLINE` / `OFFLINE` / `UNKNOWN`;
- data quality: `CURRENT` / `STALE` / `UNKNOWN`;
- alarm: highest confirmed severity or `NONE` / `UNKNOWN`;
- PLC mode: `AUTO` / `MANUAL` / `UNKNOWN`;
- current level only when mode/count/current-stage mapping is confirmed.

`OFFLINE`, `STALE` and `UNKNOWN` must never collapse into one generic error.

## Navigation

Selecting a Barn opens `vent_detail` with a selected-entity state parameter. Parameter
name and alias resolution are **uncertain** pending topology evidence. Navigation changes
dashboard state only; it performs no device mutation.

## Empty/error behavior

- No resolved controller: explain that topology/alias returned no entity; do not show zero.
- Missing value: `--` and `UNKNOWN`.
- Stale value: retain value only with timestamp/`STALE` label.
- Offline controller: show connectivity loss without marking every device `STOPPED`.

## Explicit exclusions

No one-Barn schematic, Auto/Manual button, fan/pump/louver control, alarm action, parameter
form or write-capable interaction.
