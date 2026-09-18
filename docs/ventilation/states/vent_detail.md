# State `vent_detail` — Giám sát một Barn (Data Contract v0.3)

## Purpose

Read-only monitoring view of an individual barn's environmental metrics, controller status,
and equipment feedback.

## Layout Plan

1. **Shared Header**: Barn selector, 5 navigation tabs, persistent demo badge, and connection indicators.
2. **KPI Rows**:
   - Primary: Indoor average temperature, feel temperature, outdoor temperature, relative humidity.
   - Secondary / Optional: Air speed (`airSpeed`), airflow (`airFlow`), total water consumption (`waterConsumptionTotal`).
3. **Read-Only Schematic**: Visualizes 6 fan positions, 2 cooling pumps, and roof/side louvers.
4. **Equipment Feedback Strip**: Displays current status for each equipment unit:
   - `RUNNING`: Green badge (`fanXXRun = 1` or `coolingPumpXXRun = 1`).
   - `STOPPED`: Neutral off badge (`fanXXRun = 0` or `coolingPumpXXRun = 0`).
   - `UNKNOWN`: Amber dashed badge (missing or invalid value).
   - `NOT_CONFIGURED`: Muted grey badge with "NOT CONFIGURED" label (for equipment absent from barn configuration).
5. **System Fault & Alarm Strip**: Displays system-level alarms:
   - `equipmentFaultActive`: Consolidated PLC hardware/process fault flag.
   - High/low temperature and sensor alarms with explicit `PLC` vs `PLATFORM` origin.
6. **Controller Summary**:
   - `operatingMode`: `MANUAL` / `AUTO` (PLC uint16 enum).
   - `controlBasis`: `ACTUAL_TEMPERATURE` / `PERCEIVED_TEMPERATURE`.
   - `fanControlMode`: `STEP` / `VFD`.
   - `fanStage`: Current ventilation level as an absolute integer (e.g. `4`). No synthetic ratio (`4 / 6` is forbidden).
   - `controllerOnline` & `dataQuality`: Explicitly marked `PLATFORM` tags.

## Explicit Exclusions

V1 contains no control inputs, setpoint writes, fan/pump toggle buttons, RPC triggers, or
attribute modifications.
