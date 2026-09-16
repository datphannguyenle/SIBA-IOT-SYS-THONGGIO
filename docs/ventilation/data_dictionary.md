# Ventilation data dictionary

Canonical key names below are **design candidates**, not confirmed PLC mappings. The
machine-readable draft is `config/ventilation_data_contract.json`.

| Semantic key | Meaning | Unit | Classification | Evidence / gap |
|---|---|---:|---|---|
| `temperature_indoor` | Nhiệt độ trong nhà | °C | uncertain mapping | PDF pp. 12–15, 59–60; raw tag/type/scale absent |
| `temperature_outdoor` | Nhiệt độ ngoài trời | °C | uncertain mapping | PDF pp. 12–15, 21–25 |
| `temperature_feel` | Nhiệt độ cảm nhận | °C | uncertain mapping | PDF pp. 12, 15, 21–22, 32 |
| `humidity` | Độ ẩm trong nhà | %RH | uncertain mapping | PDF pp. 12–14, 21–26, 61 |
| `air_speed` | Tốc độ gió | TBD | uncertain | PDF p. 16 names display only; no source/formula |
| `air_flow` | Lưu lượng gió | TBD | uncertain | PDF p. 16 names display only; no source/formula |
| `water_consumption` | Nước tiêu thụ | TBD | uncertain | PDF pp. 9, 16; pulse scale/reset absent |
| `fan_01_status` … `fan_06_status` | Trạng thái 6 quạt | enum TBD | uncertain | equipment count confirmed; feedback provenance absent |
| `pump_01_status`, `pump_02_status` | Trạng thái 2 bơm | enum TBD | uncertain | equipment count confirmed; feedback provenance absent |
| `roof_louver_position` | Vị trí cửa chớp trần | TBD | uncertain | 0–10 V feedback confirmed; scale absent |
| `side_louver_position` | Vị trí cửa chớp hông | TBD | uncertain | 0–10 V feedback confirmed; scale absent |
| `operation_mode` | Manual/Automatic display | enum TBD | uncertain mapping | modes confirmed; tag/enum absent |
| `fan_control_mode` | Step/VFD display | enum TBD | uncertain mapping | modes confirmed; tag/enum absent |
| `ventilation_stage` | Cấp hiện tại | level | uncertain mapping | 6 step / 9 VFD documented; runtime source absent |
| `controller_online` | Kết nối controller | boolean TBD | derived | ThingsBoard/Gateway source and timeout unconfirmed |

## Required semantics

- UI consumes semantic keys only; raw register binding belongs in gateway/config mapping.
- `null` and missing render `--`; neither means zero.
- `STALE` means data age exceeded a confirmed threshold; threshold is currently unknown.
- `OFFLINE` means confirmed connectivity loss; it does not mean equipment stopped.
- `UNKNOWN` is used when evidence is insufficient; it does not mean `STOPPED`.
- Fan/pump/louver state must be PLC feedback. Last command is never accepted as feedback.

## Stage model

- **confirmed document fact** — step mode supports 6 levels; VFD mode supports 9 levels
  (PDF p. 52).
- **uncertain runtime fact** — current mode, current level, per-level fan/frequency/louver
  map and stage-count telemetry are not available.
- UI must not render `3/6` or `3/9` until mode and stage-count sources are confirmed.

## Evidence required to promote a field

Provide raw tag/register, encoding, engineering conversion, valid range, unit, sampling
cadence, timestamp semantics, stale threshold and at least one read-only runtime sample.
