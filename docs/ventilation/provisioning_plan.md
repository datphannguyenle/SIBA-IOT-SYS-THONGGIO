# VENT-004 greenfield-with-legacy-compatibility provisioning plan

## Status and authorization

`PLANNING ONLY — NO THINGSBOARD MUTATION AUTHORIZED`

Rev A is the target schema. VENT-002 runtime evidence remains the source for deployed
state: there is currently no ventilation controller, profile, dashboard, alias or live
binding in the inspected tenant. This plan does not change that state.

## Target topology

```text
Farm
  -> FarmToArea -> Area                    LEGACY EXCEPTION
    -> AreaToBarn -> existing Barn         LEGACY EXCEPTION
      -> Contains -> <SITE>-<AREA>-<BUILDING>-VEN-SYS-01
        -> Contains -> <SITE>-<AREA>-<BUILDING>-VEN-PLC-01

Existing Gateway
  -> ConnectedTo -> <SITE>-<AREA>-<BUILDING>-VEN-PLC-01  optional
```

| Target | Entity type | Profile | State now |
|---|---|---|---|
| Ventilation System | Asset | `AP-SYSTEM-V1` | proposed; absent at runtime |
| VentilationController | Device | `DP-VEN-CTRL-V1` | proposed; absent at runtime |
| Barn → System | `Contains` relation | exact case/direction shown | proposed |
| System → Controller | `Contains` relation | exact case/direction shown | proposed |
| Gateway → Controller | `ConnectedTo` relation | optional after endpoint proof | proposed |

## Preconditions for a future provisioning task

- Reviewer grants `APPROVED — VENTILATION PROVISIONING PLAN`.
- A separate mutation authorization names the exact tenant, Barns and execution window.
- Approved `<SITE>`, `<AREA>` and `<BUILDING>` codes exist for each selected legacy Barn.
- Controller cardinality per Barn and numbering rules are approved.
- `AP-SYSTEM-V1` and `DP-VEN-CTRL-V1` definitions are approved or an exact creation
  manifest is reviewed.
- PLC/Gateway register map, device endpoint identity and credential owner are available.
- Customer/tenant isolation, rollback and secret handling are reviewed.

## Proposed execution sequence — not executed

1. **Read-only preflight:** inventory exact target Barn, ownership, relations, candidate
   Gateway and any name/profile collisions.
2. **Freeze manifest:** resolve placeholders and publish create/reuse/no-op actions,
   expected IDs after creation, and rollback order.
3. **Profiles:** create or reuse exact approved Asset/Device Profiles without changing
   unrelated profiles.
4. **Entities:** create one System Asset and the approved number of controller Devices.
5. **Relations:** add the two `Contains` edges; add `ConnectedTo` only when the Gateway
   is the proven communication owner.
6. **Gateway onboarding:** bind approved raw sources to canonical semantic keys; do not
   write PLC registers.
7. **Read-only soak:** collect timestamped samples, cadence, data types, ranges, scaling,
   heartbeat/connectivity and alarm behavior.
8. **VENT-002 re-verification:** promote only fields supported by direct evidence and
   return the task for `APPROVED — IMPLEMENTATION READY` review.
9. **Dashboard:** remains a later task and cannot start from provisioning approval alone.

## Data-contract migration map

`Evidence status` reflects VENT-002, not Rev A. `Source mapping` remains unresolved until
an approved register map/Gateway mapping and a runtime sample exist.

| Old design key | Proposed Rev A key | Evidence status | Source mapping status | Migration impact |
|---|---|---|---|---|
| `temperature_indoor` | `indoorTemperatureAvg`; or `indoorTemperature01`/`02` plus a documented average | uncertain | absent | Choose based on actual sensor count and averaging owner. |
| `temperature_outdoor` | `outdoorTemperature` | uncertain | absent | Rename only at the new Gateway normalization boundary. |
| `temperature_feel` | `perceivedTemperature` | uncertain | absent | Formula/source must be approved. |
| `humidity` | `relativeHumidity` | uncertain | absent | Confirm location, `%RH`, scale and range. |
| `air_speed` | `airSpeed` | uncertain | absent | Sensor, unit and scale unresolved; may be excluded after review. |
| `air_flow` | `airFlow` proposed extension | uncertain | absent | Not in Rev A ventilation catalog; needs schema decision, formula and unit. |
| `water_consumption` | `waterConsumptionTotal` or `waterVolumeTotal` | uncertain | absent | Select only after counter meaning, unit and reset behavior are known. |
| `fan_01_status` | `fan01Run` | uncertain | absent | Allowed only for physical run feedback, never command state. |
| `fan_02_status` | `fan02Run` | uncertain | absent | Pattern-derived; physical feedback required. |
| `fan_03_status` | `fan03Run` | uncertain | absent | Pattern-derived; physical feedback required. |
| `fan_04_status` | `fan04Run` | uncertain | absent | Pattern-derived; physical feedback required. |
| `fan_05_status` | `fan05Run` | uncertain | absent | Pattern-derived; physical feedback required. |
| `fan_06_status` | `fan06Run` | uncertain | absent | Pattern-derived; physical feedback required. |
| `pump_01_status` | `coolingPump01Run` if it is a cooling pump | uncertain | absent | Equipment role and physical feedback must be confirmed. |
| `pump_02_status` | `coolingPump02Run` proposed by sequence | uncertain | absent | Second-key extension needs approval and feedback proof. |
| `roof_louver_position` | `roofInletPosition` | uncertain | absent | Confirm 0–10 V conversion, engineering unit and valid range. |
| `side_louver_position` | `sideInletPosition` | uncertain | absent | Confirm 0–10 V conversion, engineering unit and valid range. |
| `operation_mode` | `operatingMode` | uncertain | absent | Confirm source enum; do not infer from commands. |
| `fan_control_mode` | `fanControlMode` proposed extension | uncertain | absent | Step/VFD key is not canonicalized in Rev A; needs enum decision. |
| `ventilation_stage` | `fanStage` | uncertain | absent | Confirm current stage and independent valid-stage-count source. |
| `controller_online` | platform connectivity plus `plcHeartbeat`; no direct rename yet | derived | absent | Define ONLINE/OFFLINE/STALE/UNKNOWN from evidence, not missing telemetry alone. |

The existing snake_case contract remains an audit trail until a reviewed migration is
approved. This plan intentionally does not edit `config/ventilation_data_contract.json`
or reclassify any field.

## Read-only safety

For ventilation V1, `RPC-01` is:

`N/A — prohibited by current V1 safety gate`

No RPC, command widget, parameter write, telemetry write, attribute write, alarm
acknowledge/clear/shelve or PLC write is part of this plan. Rev A command/control
sections are future architecture only.

## Rollback design for a later authorized execution

Rollback must operate in reverse dependency order and only on objects created by the
approved manifest: disable new data ingress, remove new optional cross-links, remove new
`Contains` relations, then retire/delete new entities and profiles if they have no other
references or history-retention obligation. Legacy relations and unrelated production
objects are never rollback targets.

The exact API calls and deletion policy remain unresolved until an execution task is
authorized; this planning task must not test them by mutation.

## Unresolved decisions

- Exact Barn set and canonical site/area/building codes.
- Controller cardinality and sequence for each Barn.
- Whether an existing Gateway or a new endpoint owns each controller connection.
- Full Asset/Device Profile definitions and alarms.
- All raw registers, types, byte/word order, scale, cadence and timestamps.
- Physical fan/pump feedback and louver calibration.
- `airFlow`, `fanControlMode`, pump naming and cumulative-water canonical choices.
- Connectivity/freshness thresholds and alarm/history retention.
- Exact rollback behavior for retained telemetry/history.

## Gate

ChatGPT Web must review this package and decide:

`APPROVED — VENTILATION PROVISIONING PLAN`

That decision approves a plan only. A separate explicit mutation authorization is still
required before any ThingsBoard write.
