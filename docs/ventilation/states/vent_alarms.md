# State `vent_alarms` — Cảnh báo read-only

## Purpose

Display active alarms and history for the selected Farm/Barn/controller without changing
alarm lifecycle state.

## Planned columns

- severity;
- alarm type/message;
- occurrence time;
- device/controller and Barn scope;
- active/cleared status as reported by ThingsBoard;
- latest update/resolution time when present.

## Evidence classification

- **confirmed document capability** — HMI exposes current alarms, date-filtered history and
  equipment/temperature alarm information (PDF pp. 18–20).
- **uncertain target schema** — alarm type IDs, severity mapping, details, originator,
  propagation, retention, timezone and farm scoping.
- **confirmed external pattern** — Khử mùi builder configures a system alarm table in
  read-only form; applicability to ventilation datasource remains proposed.

## Interaction

- Read filters, sorting, paging, date/time window and row inspection are allowed.
- Navigation to read-only device detail is allowed if alias resolution is confirmed.

## Prohibited

- acknowledge;
- clear;
- shelve;
- assign;
- action button or event that changes alarm/device/PLC state.
