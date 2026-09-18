# State `vent_settings` — Cài đặt thông gió (Data Contract v0.3)

## Purpose

Read-only inspection interface for the 224 controller configuration parameters defined in
**Data Contract v0.3** (`SIBA_Ventilation_Agent_DataContract_v0.3.json`).

## Functional Organization

The 224 setting variables (179 PROPOSED, 45 OPTIONAL) are structured into functional matrices:

1. **Cài đặt nhiệt độ** (40 parameters):
   - 10 configuration slots × 4 variables: Ngày tuổi (`settingTemperatureProfileXXDayAge`),
     Nhiệt độ cài đặt (`settingTemperatureProfileXXTargetTemperature`),
     Cảnh báo thấp (`settingTemperatureProfileXXLowAlarm`),
     Cảnh báo cao (`settingTemperatureProfileXXHighAlarm`).
2. **Cài đặt nhiệt độ cảm nhận** (40 parameters):
   - 10 configuration slots × 4 variables: Ngày tuổi (`settingPerceivedProfileXXDayAge`),
     Cài đặt (`settingPerceivedProfileXXTarget`),
     Cảnh báo thấp (`settingPerceivedProfileXXLowAlarm`),
     Cảnh báo cao (`settingPerceivedProfileXXHighAlarm`).
3. **Cài đặt cấp thông gió** (108 parameters):
   - 9 configuration slots × 12 variables:
     Offset nhiệt độ (`settingStageXXTemperatureOffset`),
     Offset cảm nhận (`settingStageXXPerceivedOffset`),
     Quạt 1–6 chọn chạy (`settingStageXXFan01Select` .. `settingStageXXFan06Select`),
     Tần số VFD 1–2 (`settingStageXXVfd01Frequency`, `settingStageXXVfd02Frequency`),
     Độ mở cửa chớp trần/hông (`settingStageXXRoofLouverPosition`, `settingStageXXSideLouverPosition`).
   - *Note*: 9 slots represent the maximum engineering capability of the controller, not the active operating stage count.
4. **Cài đặt thời gian** (18 parameters):
   - Delay chuyển cấp và trễ tắt quạt.
   - Chu kỳ chạy/dừng định kỳ cho Quạt 1–6 và Bơm 1–2.
5. **Hiệu chỉnh** (4 parameters):
   - Bù nhiệt độ cảm biến trong nhà 1–2, nhiệt độ ngoài trời, độ ẩm.

## Display Rules

- **Default Value**: All 224 cells render `--` when no specific telemetry or attribute value is provided.
- **Unit & Formatting**: Rendered with proper units (°C, %, Hz, s, min, ngày) derived from contract metadata.
- **Index Jump Navigation**: Secondary anchor links at the top of the settings tab allow jumping directly to functional sections.
- **Responsive Layout**: Wrapped in a horizontally scrollable container on tablet and mobile viewports (`390px`) to prevent root horizontal overflow.

## Strict Safety Boundaries (V1 Policy)

- **READ-ONLY ONLY**: The surface contains zero `<input>`, `<select>`, `<textarea>`, `<form>`, or `<button>` write controls.
- **NO RPC**: No ThingsBoard RPC methods (`sendOneWayRpc`, `sendTwoWayRpc`, `controlApi`) are present in the controller script.
- **NO ATTRIBUTE WRITE**: No writes to server-side or shared attributes (`saveEntityAttributes`, `attributeService`).
- **NO PLC WRITE**: Modbus Function Code is strictly read (FC 03).
