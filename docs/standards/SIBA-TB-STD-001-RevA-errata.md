# SIBA-TB-STD-001 Rev A — adoption decision and errata

## Decision

Recorded: 2026-09-17

`SIBA_ThingsBoard_Entity_Data_Standard_RevA.docx` is accepted as:

- a draft architecture baseline;
- a greenfield design baseline; and
- an acceptance, FAT and SAT baseline.

It is not approved for retroactive enforcement across the existing tenant. This
decision does not authorize a ThingsBoard mutation, production migration, dashboard
implementation or deployment.

## Canonical syntax clarification

The prose rules in section 5.1 of the DOCX control where table rendering is ambiguous.
The following forms are canonical:

| Object | Canonical syntax | Example |
|---|---|---|
| Entity/artifact technical name | uppercase ASCII segments separated by hyphens | `GH01-F01-1F1-VEN-PLC-01` |
| Device Profile | `DP-<DOMAIN>-<ROLE>-V<MAJOR>` | `DP-VEN-CTRL-V1` |
| Asset Profile | `AP-<ROLE>-V<MAJOR>` | `AP-SYSTEM-V1` |
| Dashboard | `DB-<NN>-<SCOPE>-<PURPOSE>-V<MAJOR>` | `DB-30-VEN-DETAIL-V1` |
| Alarm type | `UPPER_SNAKE_CASE` | `VEN_HIGH_TEMPERATURE` |
| Telemetry/attribute key | ASCII `lowerCamelCase` | `indoorTemperatureAvg` |

Examples rendered with spaces, such as `DP VEN CTRL V1`, `GH01 F01 1F1 VEN PLC 01`
and `VEN HIGH TEMPERATURE`, are presentation ambiguity, not alternate naming syntax.
This clarification applies to new artifacts. It does not rename existing production
objects.

## Scope clarification

- Existing live entities, technical names, profiles and relations are grandfathered.
- Existing `FarmToArea` and `AreaToBarn` relations remain valid legacy topology.
- New ventilation entities use the Rev A target model from the existing Barn downward.
- Rev A RPC/control sections describe future architecture only for this project.
- Ventilation V1 remains read-only; `RPC-01` is `N/A — prohibited by current V1 safety
  gate`.
- A key appearing in Rev A is a target-schema candidate, not proof that a PLC/Gateway
  source or live ThingsBoard binding exists.

## Evidence boundary

The following sources have distinct authority:

1. Rev A defines the proposed canonical target schema.
2. An approved register map and Gateway configuration define the source mapping.
3. A timestamped read-only runtime sample confirms that the binding operates.

No field may move from `uncertain` to `confirmed` solely because it is listed in Rev A.

## Open revision items

- Incorporate this syntax clarification into the next human-readable DOCX revision so
  the prose and all table examples render identically.
- Add an explicit greenfield-versus-legacy applicability column to the acceptance
  checklist.
- Mark RPC/control acceptance items optional or `N/A` for monitoring-only projects.
- Publish project-approved register maps, alarm matrices and data dictionaries before
  commissioning.
