# Runtime assumptions and evidence gaps

## Confirmed

- V1 is read-only; PLC/Gateway controls fans, pumps, louvers and ventilation logic.
- Target repo currently contains no runtime artifact or production code.
- Technical document describes six fans, two pumps, two louvers and manual/automatic
  display behavior (PDF pp. 6, 8–18, 38–61).
- Step control has 6 levels; VFD mode has 9 levels (PDF p. 52).

## Derived

- `controller_online` will likely come from ThingsBoard connectivity/activity rather than
  a PLC register, but this must be confirmed against the selected entity/profile model.
- A selected-entity dashboard state is a suitable design candidate because the external
  Khử mùi dashboard uses that pattern successfully; it is not yet a ventilation runtime
  fact.

## Uncertain

- Runtime instance, device profile, entity IDs, aliases and relation names.
- Whether there is one controller per Barn.
- Raw PLC tags/registers, encoding, scale, valid ranges and timestamps.
- Telemetry sampling cadence, transport cadence, heartbeat and stale thresholds.
- Fan/pump status provenance and fault granularity.
- Air speed, airflow and water-consumption production sources/formulas.
- Alarm types, severities, propagation, retention and timezone.
- History retention and availability of built-in export in the target ThingsBoard build.

## Design handling

- Unknown values render `--` plus `UNKNOWN`, never numeric zero.
- Stale data retains last value only with explicit `STALE`; it must not appear current.
- `OFFLINE` describes connectivity; it is not a synonym for stopped equipment.
- No UI state is inferred from a last command.
- All runtime-dependent panels remain conditional until their evidence gap is closed.
