# State `vent_detail` — Giám sát một Barn

## Purpose

Read-only view of one Barn’s environment, controller mode and equipment feedback.

## Layout plan

1. Shared header: back to overview, selected Barn/controller, tabs, connectivity/freshness.
2. KPI row: indoor/outdoor/feel temperature and humidity.
3. Conditional KPI row: air speed, airflow, water consumption only after mapping is
   confirmed; otherwise omitted, not filled with demo values.
4. Read-only schematic: six fans, two pumps, roof louver and side louver.
5. Display-only controller summary: Auto/Manual, step/VFD, current level.
6. Short read-only trend preview with navigation to `vent_history`.

## Eligibility and classification

- Environmental field existence is **confirmed from PDF**; semantic/raw mappings remain
  **uncertain**.
- Six fans, two pumps and two louvers are **confirmed document equipment counts**.
- Louver feedback signal existence is **confirmed**; engineering conversion is uncertain.
- Fan/pump running status provenance is **uncertain** and cannot be treated as feedback
  until the PLC contract confirms it.
- Current mode/level keys and enum encodings are **uncertain**.

## Schematic state contract

Each element resolves independently to:

- `NORMAL`: confirmed healthy/running feedback under an approved interpretation;
- `WARNING`: confirmed warning condition;
- `FAULT`: confirmed fault feedback/alarm;
- `OFFLINE`: controller/device connectivity confirmed lost;
- `STALE`: value timestamp exceeds a confirmed freshness threshold;
- `UNKNOWN`: missing, invalid or unmapped feedback.

`STOPPED` may be displayed only from an explicit confirmed feedback value. `UNKNOWN` is
never converted to `STOPPED`. Last command is never accepted as actual feedback.

## Stage display

- Step mode document maximum: 6 levels.
- VFD mode document maximum: 9 levels.
- Runtime label uses current mode + confirmed stage-count source. Until both exist, display
  mode/level as `-- / UNKNOWN`; do not hard-code `x/6` or `x/9`.

## Responsive behavior

- Desktop: KPI then schematic and controller summary in the primary viewport.
- Tablet: stack summary beneath schematic.
- Mobile: one column; allow local horizontal pan for schematic if necessary, never root
  page horizontal overflow.

## Explicit exclusions

No toggle, slider, momentary button, mode switch, setpoint, fan/pump/louver command, RPC,
attribute write or control event.
