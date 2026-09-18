# VENT-007 — Đối chiếu dashboard hiện tại ↔ Data Contract v0.2

Ngày 17/09/2026 · nhánh `feat/VENT-007-contract-v02-alignment` (tách từ `feat/VENT-006-tb-demo-deploy` @ `018d625`).
Chỉ repo. Không sửa ThingsBoard live, không PLC integration, không resume VENT-005.

## 1. Tóm tắt

| Hạng mục | Hiện tại (VENT-003/006) | Contract v0.2 + quyết định | Hành động |
|---|---|---|---|
| Nguồn raw của fixture | snake_case kế thừa VENT-002 (`temperature_indoor`, `fan_01_run`…), boolean/string | key camelCase của contract, kiểu PLC (`uint16` 0/1/enum, `float32`) | Đổi fixture `latest` sang key + mã hóa contract; adapter chuyển mã |
| Trạng thái quạt/bơm | `fanXXRun` + `fanXXFault` → RUNNING/STOPPED/FAULT/UNKNOWN | chỉ `fanXXRun` (0/1) | Bỏ 8 key Fault; trạng thái RUNNING/STOPPED/UNKNOWN/NOT_CONFIGURED |
| Lỗi thiết bị | theo từng quạt (Quạt 06 FAULT) | `equipmentFaultActive` cấp hệ thống | Chỉ báo mức hệ thống |
| Cấp thông gió | `fanStage` + `stageCount` → `4 / 6` | chỉ `fanStage` | Bỏ `stageCount`, hiển thị `4` |
| controllerOnline / dataQuality | đọc như biến telemetry | không có trong PLC contract | PLATFORM_DERIVED, khối riêng trong fixture |
| Biến giám sát mới | — | 19 key giám sát/cảnh báo chưa có | Thêm vào canonical model theo phân loại |
| Cài đặt | — | 224 biến (179 PROPOSED, 45 OPTIONAL) | State mới `vent_settings` READ-ONLY |
| Cảnh báo demo | `VEN_FAN_FAULT` (theo quạt), `VEN_ROOF_INLET_STALE`, `VEN_HIGH_HUMIDITY` | cờ PLC + alarm platform | Đổi sang nguồn PLC/PLATFORM rõ ràng |

Lưu ý sửa số: đợt hỏi trước ghi "238 setting"; đếm lại từ JSON là **224**.

## 2. Đối chiếu từng key

### Current canonical keys (adapter CANONICAL_MAP, 33)

| Key hiện tại | Trong contract v0.2 | Kiểu contract | Đề xuất |
|---|---|---|---|
| `airFlow` | có (D1020-D1021, PROPOSED) | float32 m3/h | GIỮ · PRIMARY_MONITORING |
| `airSpeed` | có (D1018-D1019, PROPOSED) | float32 m/s | GIỮ · PRIMARY_MONITORING |
| `controllerOnline` | không | — | GIỮ · PLATFORM_DERIVED (không D-register) |
| `coolingPump01Fault` | không | — | **BỎ** |
| `coolingPump01Run` | có (D1046, PROPOSED) | uint16  | GIỮ · PRIMARY_MONITORING |
| `coolingPump02Fault` | không | — | **BỎ** |
| `coolingPump02Run` | có (D1047, PROPOSED) | uint16  | GIỮ · PRIMARY_MONITORING |
| `dataQuality` | không | — | GIỮ · PLATFORM_DERIVED (không D-register) |
| `fan01Fault` | không | — | **BỎ** |
| `fan01Run` | có (D1040, PROPOSED) | uint16  | GIỮ · PRIMARY_MONITORING |
| `fan02Fault` | không | — | **BỎ** |
| `fan02Run` | có (D1041, PROPOSED) | uint16  | GIỮ · PRIMARY_MONITORING |
| `fan03Fault` | không | — | **BỎ** |
| `fan03Run` | có (D1042, PROPOSED) | uint16  | GIỮ · PRIMARY_MONITORING |
| `fan04Fault` | không | — | **BỎ** |
| `fan04Run` | có (D1043, PROPOSED) | uint16  | GIỮ · PRIMARY_MONITORING |
| `fan05Fault` | không | — | **BỎ** |
| `fan05Run` | có (D1044, PROPOSED) | uint16  | GIỮ · PRIMARY_MONITORING |
| `fan06Fault` | không | — | **BỎ** |
| `fan06Run` | có (D1045, PROPOSED) | uint16  | GIỮ · PRIMARY_MONITORING |
| `fanControlMode` | có (D1032, PROPOSED) | uint16  | GIỮ · PRIMARY_MONITORING |
| `fanStage` | có (D1033, PROPOSED) | uint16 stage | GIỮ · PRIMARY_MONITORING |
| `indoorTemperature01` | có (D1000-D1001, PROPOSED) | float32 °C | GIỮ · SECONDARY_MONITORING |
| `indoorTemperature02` | có (D1002-D1003, PROPOSED) | float32 °C | GIỮ · SECONDARY_MONITORING |
| `indoorTemperatureAvg` | có (D1004-D1005, PROPOSED) | float32 °C | GIỮ · PRIMARY_MONITORING |
| `operatingMode` | có (D1029, PROPOSED) | uint16  | GIỮ · PRIMARY_MONITORING |
| `outdoorTemperature` | có (D1006-D1007, PROPOSED) | float32 °C | GIỮ · PRIMARY_MONITORING |
| `perceivedTemperature` | có (D1008-D1009, PROPOSED) | float32 °C | GIỮ · PRIMARY_MONITORING |
| `relativeHumidity` | có (D1014-D1015, PROPOSED) | float32 %RH | GIỮ · PRIMARY_MONITORING |
| `roofInletPosition` | có (D1034-D1035, PROPOSED) | float32 % | GIỮ · PRIMARY_MONITORING |
| `sideInletPosition` | có (D1036-D1037, PROPOSED) | float32 % | GIỮ · PRIMARY_MONITORING |
| `stageCount` | không | — | **BỎ** |
| `waterConsumptionTotal` | có (D1022-D1023, PROPOSED) | float32 L | GIỮ · PRIMARY_MONITORING |

Số key hiện tại: 33; giữ: 22; platform: 2; bỏ: 9

### Monitoring/alarm keys của contract chưa có trong model hiện tại

| # | Key | Kiểu | Đơn vị | Mirror | Status | Phân loại đề xuất | Nhãn |
|---|---|---|---|---|---|---|---|
| 6 | `temperatureSetpointCurrent` | float32 | °C | D1010-D1011 | PROPOSED | SECONDARY_MONITORING | Nhiệt độ cài đặt hiện tại theo ngày tuổi |
| 7 | `perceivedTemperatureSetpointCurrent` | float32 | °C | D1012-D1013 | PROPOSED | SECONDARY_MONITORING | Nhiệt độ cảm nhận cài đặt hiện tại |
| 9 | `humiditySetpointCurrent` | float32 | %RH | D1016-D1017 | PROPOSED | SECONDARY_MONITORING | Độ ẩm cài đặt hiện tại |
| 13 | `waterFlow` | float32 | L/min | D1024-D1025 | OPTIONAL | OPTIONAL | Lưu lượng nước tức thời nếu PLC có tính |
| 14 | `pigCount` | uint16 | count | D1026 | PROPOSED | SECONDARY_MONITORING | Tổng đàn hiện tại / số heo nhập chuồng |
| 15 | `pigDeathCount` | uint16 | count | D1027 | PROPOSED | SECONDARY_MONITORING | Số heo chết tích lũy |
| 16 | `pigAgeDay` | uint16 | day | D1028 | PROPOSED | SECONDARY_MONITORING | Ngày tuổi hiện tại |
| 18 | `controlBasis` | uint16 |  | D1030 | PROPOSED | SECONDARY_MONITORING | Cơ sở điều khiển: nhiệt độ / nhiệt độ cảm nhận |
| 19 | `dehumidificationEnabled` | uint16 |  | D1031 | PROPOSED | SECONDARY_MONITORING | Chế độ khử ẩm đang bật/tắt |
| 24 | `equipmentFaultActive` | uint16 |  | D1038 | PROPOSED | PRIMARY_MONITORING | Tín hiệu lỗi thiết bị tổng từ DI |
| 25 | `externalHighTemperatureAlarm` | uint16 |  | D1039 | PROPOSED | PRIMARY_MONITORING | Cảnh báo nhiệt độ cao từ thermostat ngoài |
| 34 | `fan01SpeedSetpoint` | float32 | % | D1048-D1049 | OPTIONAL | OPTIONAL | AO tốc độ quạt/VFD kênh 1 - giá trị đặt |
| 35 | `fan02SpeedSetpoint` | float32 | % | D1050-D1051 | OPTIONAL | OPTIONAL | AO tốc độ quạt/VFD kênh 2 - giá trị đặt |
| 36 | `fan01SpeedFeedback` | float32 | Hz | D1052-D1053 | OPTIONAL | OPTIONAL | Phản hồi tốc độ/VFD kênh 1 |
| 37 | `fan02SpeedFeedback` | float32 | Hz | D1054-D1055 | OPTIONAL | OPTIONAL | Phản hồi tốc độ/VFD kênh 2 |
| 262 | `temperatureLowAlarmActive` | uint16 |  | D1406 | OPTIONAL | OPTIONAL | Cảnh báo nhiệt độ thấp trong chuồng |
| 263 | `temperatureHighAlarmActive` | uint16 |  | D1407 | OPTIONAL | OPTIONAL | Cảnh báo nhiệt độ cao trong chuồng |
| 264 | `perceivedTemperatureLowAlarmActive` | uint16 |  | D1408 | OPTIONAL | OPTIONAL | Cảnh báo nhiệt độ cảm nhận thấp |
| 265 | `perceivedTemperatureHighAlarmActive` | uint16 |  | D1409 | OPTIONAL | OPTIONAL | Cảnh báo nhiệt độ cảm nhận cao |

### Settings theo nhóm

| Nhóm | Tổng | PROPOSED | OPTIONAL | Mirror |
|---|---|---|---|---|
| CÀI ĐẶT - HỆ THỐNG | 14 | 14 | 0 | D1056–D1077 |
| CÀI ĐẶT - NHIỆT ĐỘ | 40 | 40 | 0 | D1078–D1147 |
| CÀI ĐẶT - NHIỆT ĐỘ CẢM NHẬN | 40 | 40 | 0 | D1148–D1217 |
| CÀI ĐẶT - CẤP THÔNG GIÓ | 108 | 63 | 45 | D1218–D1379 |
| CÀI ĐẶT - THỜI GIAN | 18 | 18 | 0 | D1380–D1397 |
| CÀI ĐẶT - HIỆU CHỈNH | 4 | 4 | 0 | D1398–D1405 |
| **Tổng** | **224** | 179 | 45 | |

Phân loại toàn bộ 265 biến: {'SECONDARY_MONITORING': 10, 'PRIMARY_MONITORING': 22, 'OPTIONAL': 9, 'SETTINGS': 224}


## 3. Chuyển mã adapter đề xuất (raw contract → canonical view model)

| Canonical | Raw contract | Quy tắc |
|---|---|---|
| float32 (nhiệt độ, độ ẩm, vị trí cửa chớp, gió, nước…) | số | giữ nguyên; `null`/thiếu → `null` (`--`); `0` giữ là `0` |
| `operatingMode`, `controlBasis`, `fanControlMode`, `dehumidificationEnabled` | uint16 | bảng enum B; giá trị ngoài bảng → `UNKNOWN` (không đoán) |
| `fanXXRun`, `coolingPumpXXRun` | uint16 | 0→`STOPPED`, 1→`RUNNING`, khác/null→`UNKNOWN`; key nằm trong danh sách N/A → `NOT_CONFIGURED` |
| `equipmentFaultActive`, `externalHighTemperatureAlarm`, 4 cờ alarm OPTIONAL | uint16 | 0→`NORMAL`, 1→`ACTIVE`, khác/null→`UNKNOWN`; N/A → `NOT_CONFIGURED` |
| `fanStage`, `pigCount`, `pigDeathCount`, `pigAgeDay` | uint16 | số nguyên; null giữ null |
| `controllerOnline` | platform | `true/false/null` → ONLINE/OFFLINE/UNKNOWN |
| `dataQuality` | platform | CURRENT/STALE/OFFLINE/UNKNOWN |

**Nguồn "N/A" (thiết bị/biến không cấu hình)** — đề xuất: fixture có `mapping.notConfigured: [keys]`
(sau này đến từ mapping kỹ sư PLC ghi N/A). Cần review xác nhận hình thức này.

## 4. Đề xuất theo state

- **default**: bỏ `stageCount` khỏi thẻ nhà; thẻ nhà hiện `Cấp: n`. Alarm ưu tiên hiện nguồn (`PLC`/`PLATFORM`).
- **vent_detail**:
  - KPI giữ 4: `indoorTemperatureAvg`, `outdoorTemperature`, `perceivedTemperature`, `relativeHumidity`.
  - Sơ đồ: 6 quạt RUNNING/STOPPED/UNKNOWN/NOT_CONFIGURED (NOT_CONFIGURED: ẩn khỏi sơ đồ hoặc vẽ mờ nét đứt có nhãn — đề xuất vẽ mờ để giữ bố cục); cửa chớp giữ.
  - Dải thiết bị: bỏ dòng "FAULT"; thêm băng trạng thái hệ thống `equipmentFaultActive` + `externalHighTemperatureAlarm`.
  - Panel bộ điều khiển: Kết nối (PLATFORM), Chế độ, Cơ sở điều khiển, Điều khiển quạt, **Cấp hiện tại = `fanStage`**, Khử ẩm, Chất lượng dữ liệu (PLATFORM).
  - "Dữ liệu bổ sung": `airSpeed`, `airFlow`, `waterConsumptionTotal` (+ `waterFlow` OPTIONAL).
  - Nhóm SECONDARY mới (gọn): setpoint hiện tại (nhiệt độ, cảm nhận, độ ẩm), `indoorTemperature01/02`, đàn heo (`pigCount`, `pigDeathCount`, `pigAgeDay`). VFD OPTIONAL (`fan01/02SpeedSetpoint/Feedback`) chỉ hiện khi `fanControlMode=VFD` và có giá trị.
- **vent_history**: giữ biểu đồ 4 chuỗi + bảng. Contract liệt kê thêm `airSpeed`, `airFlow`, `waterConsumptionTotal` là ứng viên lịch sử — đề xuất thêm một bảng/biểu đồ phụ "Gió & nước"; nước hiển thị delta từ total counter chỉ khi có dữ liệu (demo: `--`). Cần review chọn phương án.
- **vent_alarms**: thêm cột Nguồn loại (`PLC` / `PLATFORM`); demo đổi thành `EQUIPMENT_FAULT_ACTIVE` (PLC), `TELEMETRY_STALE` (PLATFORM), `TEMPERATURE_HIGH_ALARM_ACTIVE` (PLC, OPTIONAL — có thể N/A). Không có cờ độ ẩm trong v0.2 → bỏ `VEN_HIGH_HUMIDITY`.
- **vent_settings (mới, READ-ONLY)**: tab con theo 6 nhóm:
  - Hệ thống (14): danh sách nhãn/giá trị/đơn vị, enum hiển thị semantic.
  - Nhiệt độ (40) và Nhiệt độ cảm nhận (40): bảng 10 slot × (Ngày tuổi, Cài đặt, Cảnh báo thấp, Cảnh báo cao).
  - Cấp thông gió (108): bảng 9 slot × (Offset nhiệt độ, Offset cảm nhận*, Quạt 1–6 chọn, Tần số VFD 1–2*, Cửa chớp trần*, Cửa chớp hông*) — *OPTIONAL; ghi rõ "9 slot = năng lực cấu hình tối đa, không phải số cấp đang dùng".
  - Thời gian (18): delay chuyển cấp/tắt quạt + chu kỳ chạy/dừng quạt 1–6, bơm 1–2.
  - Hiệu chỉnh (4).
  - Không nút, không ô nhập, không hiển thị địa chỉ D-register trên UI.
  - Dữ liệu demo: đề xuất để `null` (`--`) cho gần như toàn bộ, tránh trông như tham số khuyến nghị thật; cần review.

## 5. File và key cần sửa (trước khi code)

| File | Thay đổi |
|---|---|
| `docs/ventilation/contract/` | ĐÃ thêm: JSON gốc, README, quyết định, báo cáo này. Excel: chờ bổ sung |
| `fixtures/ventilation/demo.json` | v2.0.0: `latest` dùng key contract + mã uint16/float32; khối `platform` (`controllerOnline`, `dataQuality`); `mapping.notConfigured`; bỏ `*_fault`, `ventilation_stage_count`, `stageCount` ở `barns`; bỏ Quạt 06 FAULT; thêm SECONDARY, cờ hệ thống, `settings` (null theo nhóm); `history` dùng key contract; alarm có `source`; `adapterTestVariants` mới (enum ngoài bảng, NOT_CONFIGURED, stage 0, fault hệ thống) |
| `widgets/ventilation-adapter.js` | Bỏ `CANONICAL_MAP` snake_case, 8 key Fault, `stageCount`, `stageDisplay` x/y; thêm bảng enum, chuyển mã run/cờ, `NOT_CONFIGURED`, platform block, SECONDARY/OPTIONAL, `settings` theo group; đọc danh sách key từ một nguồn (không gõ lại 265 key) |
| `dashboard/app.js` | Detail (bỏ FAULT từng quạt, thêm băng lỗi hệ thống, panel mới, `fanStage`), default (thẻ nhà), alarms (cột nguồn), history (theo quyết định review), state mới `vent_settings` + tab thứ 5 |
| `dashboard/dashboard.css` | Style NOT_CONFIGURED, băng lỗi hệ thống, bảng settings dạng slot; bỏ `.fan.FAULT` từng quạt |
| `tests/test_dashboard_demo.py` | Tập key chuẩn mới; không còn Fault/stageCount; enum; phân loại; fixture phủ NOT_CONFIGURED |
| `tests/test_dashboard_browser.py` | Suy diễn trạng thái mới; `fanStage` không mẫu số; 5 state; settings chỉ đọc; không ô nhập |
| `tests/test_contract_v02.py` (mới) | Mọi key PLC trong model có trong contract; `controllerOnline`/`dataQuality` không có; không key đã bỏ; enum khớp quyết định; không đánh số lại mirror (so sha256 file gốc) |
| `tests/test_thingsboard_widget_payload.py` | Cập nhật kỳ vọng (quạt, `4`, 5 state); test "refinement chỉ đổi CSS" gắn với VENT-006 → giới hạn lại/đổi mốc |
| `deploy/thingsboard/build_vent_demo.py`, `vent_demo_common.py` (`STATES`) | Thêm `vent_settings` vào build (chỉ build cục bộ; KHÔNG deploy) |
| `deploy/thingsboard/verify_vent_demo_ui.py` | Công cụ VENT-006 kiểm bản live hiện tại; giữ nguyên, ghi chú không dùng cho build VENT-007 cho tới task deploy mới |
| `docs/ventilation/dashboard/{canonical_view_model,fixture_schema,widget_inventory,state_navigation}.md`, `docs/ventilation/states/vent_detail.md` + mới `vent_settings.md` | Cập nhật theo model mới |
| `docs/ventilation/dashboard/evidence/` | Chụp lại standalone (thêm `vent-settings-1920/390`) |

**Không sửa**: `config/ventilation_data_contract.json`, `docs/ventilation/runtime/*` và handoff VENT-002 (bằng chứng),
`docs/ventilation/provisioning/*` (VENT-005), `deploy/thingsboard/vent006_manifest.json` và evidence VENT-006, live ThingsBoard.

## 6. Câu hỏi cần review trước khi code

1. Nguồn N/A: chấp nhận `mapping.notConfigured` trong fixture (sau này từ mapping PLC)?
2. Quạt NOT_CONFIGURED trên sơ đồ: vẽ mờ có nhãn (giữ bố cục) hay ẩn hẳn?
3. `vent_history`: thêm phần "Gió & nước" hay giữ 4 chuỗi môi trường?
4. `vent_settings` demo: toàn `--` hay có vài giá trị DEMO minh họa?
5. Vị trí tab `vent_settings`: tab thứ 5 sau "Cảnh báo"?

---

## 7. Quyết định bổ sung từ chủ dự án (18/09/2026) — Data Contract v0.3

Vào ngày 18/09/2026, chủ dự án (ChatGPT Web / Project Owner) đã đưa ra quyết định chính thức:
**Data Contract v0.3 thay thế v0.2 làm GIAO DIỆN HIỆN HÀNH (CURRENT ventilation interface).**

### Chi tiết thay đổi:
1. **Kiến trúc PLC**: Hệ thống thông gió sử dụng PLC riêng, độc lập với hệ khử mùi.
2. **Dải địa chỉ mirror**:
   - Vùng mirror PLC dịch chuyển `-450`: từ `D1000–D1409` về `D550–D959`.
   - Modbus Holding Register giữ nguyên: `4x-1 .. 4x-410` (410 registers).
3. **Tính tương thích**:
   - Toàn bộ 265 keys giữ nguyên không đổi.
   - Thứ tự, kiểu dữ liệu, độ rộng word, các enum và ngữ nghĩa dashboard hoàn toàn không đổi.
4. **Hiện vật nguồn (Source Artifacts)**:
   - `docs/ventilation/contract/SIBA_Ventilation_Agent_DataContract_v0.3.json` (sha256 `6cce2e264f5a698cbdd7ab157a21101c968671c55836dcde3ecdf6170f987244`).
   - `docs/ventilation/contract/SIBA_Ventilation_PLC_HMI_TB_Mapping_TEMPLATE_v0.3.xlsx`.
5. **Bảo lưu v0.2**: Bản v0.2 được giữ nguyên làm bằng chứng lịch sử, không xóa.
