# Contract v0.2 — quyết định dự án (chốt 17/09/2026)

Nguồn: phê duyệt người dùng/ChatGPT Web khi mở VENT-007. Bổ sung cho JSON gốc, không sửa JSON.

## A. Giao tiếp PLC

| Mục | Quyết định |
|---|---|
| Hãng/model PLC, IP, port, unit ID | `PLC_ENGINEER_TBD` — không chặn VENT-007 |
| `D1000–D1409` ↔ `4x-1..4x-410` | Mapping DO DỰ ÁN QUY ĐỊNH cho interface PLC → Gateway, không phải mapping đọc từ PLC hiện hữu. Kỹ sư PLC bố trí dữ liệu thật vào block này; vùng D không dùng được/trùng → báo lại, không tự đổi |
| Thứ tự word float32 | `PLC_ENGINEER_TBD` — không giả định ABCD/CDAB |
| Gateway | Gateway riêng cho hệ thông gió; không dùng gateway hệ khác làm communication owner. Chu kỳ đọc/topology chốt khi có PLC |

## B. Enum (PLC uint16 → semantic string ở Adapter/Gateway)

| Key | 0 | 1 | Giá trị khác / null |
|---|---|---|---|
| `operatingMode` | `MANUAL` | `AUTO` | `UNKNOWN` |
| `controlBasis` | `ACTUAL_TEMPERATURE` | `PERCEIVED_TEMPERATURE` | `UNKNOWN` |
| `fanControlMode` | `STEP` | `VFD` | `UNKNOWN` |
| `dehumidificationEnabled` | `DISABLED` | `ENABLED` | `UNKNOWN` |
| `fanXXRun`, `coolingPumpXXRun` (theo contract) | `STOPPED` | `RUNNING` | `UNKNOWN`; thiết bị N/A → `NOT_CONFIGURED` |

PLC không dùng string. Muốn đổi enum phải báo trước để đổi contract.

## C. Nghiệp vụ

- **stageCount**: không có trong contract. Dashboard chỉ hiện `fanStage` (vd `4`), không `x / y`, không suy từ 9 slot cấu hình (9 slot = năng lực cấu hình tối đa).
- **indoorTemperatureAvg / perceivedTemperature / airFlow**: ưu tiên PLC tính sẵn. Không viết công thức trong TB giai đoạn này. PLC không có → null/unavailable, kỹ sư ghi N/A. (Tính avg ở Gateway: để sau, không thuộc VENT-007.)
- **waterConsumptionTotal**: TOTAL COUNTER tích lũy, không reset theo ngày cho dashboard. Hệ số xung `PLC_ENGINEER_TBD`. Nước theo ngày/lứa/ca = delta tính ở platform.
- **Thiết bị**: contract hỗ trợ tối đa 6 quạt + 2 bơm (capability). Thiết bị không tồn tại = N/A → UI ẩn hoặc `NOT CONFIGURED`, không bao giờ `STOPPED`/`FAULT`.
- **Alarm**: alarm process/hardware lấy từ cờ PLC nếu có (nhiệt độ cao/thấp, độ ẩm, lỗi thiết bị, thermostat). TB chỉ tự sinh alarm platform (OFFLINE, telemetry stale, liên lạc gateway/device). Không tạo trùng alarm PLC đã có. Cờ OPTIONAL không có → N/A.

## D. Phạm vi

- Pilot tham chiếu `ND2-1`; mã `ABCDA01-B-ND2-01` CHƯA duyệt production. VENT-005 PAUSED.
- `vent_settings`: READ-ONLY. Không write attribute, RPC, PLC write, parameter write.
- Không map D-register cho `controllerOnline`, `dataQuality` (PLATFORM_DERIVED).
