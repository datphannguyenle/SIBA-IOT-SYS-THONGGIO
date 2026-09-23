# VENT-010 — Cấu hình widget modular khi có dữ liệu thật

Tài liệu này mô tả **việc cấu hình**, không phải sửa code. Chỉ đọc; không RPC, không ghi
attribute/telemetry, không lệnh thiết bị. Contract: v0.3 (mẫu giao diện, chưa phải mapping
PLC đã xác minh runtime).

## 1. Hai loại widget

| Loại | Widget type | Phạm vi entity | Dùng cho |
|---|---|---|---|
| `overview` | `tenant.siba_vent_demo.modular_overview` (chạy trên TB `latest`) | **Nhiều entity** | Lưới chọn nhà ở màn Tổng quan |
| `static`, `latest`, `timeseries`, `alarm` | `tenant.siba_vent_demo.modular_*` | **Một entity** | Header, KPI, sơ đồ, bộ điều khiển, lịch sử, cảnh báo, cài đặt |

Widget chi tiết cố ý **từ chối** khi datasource trả về nhiều entity
(`mapping.scope = MULTIPLE_ENTITIES_REJECTED`) để không trộn số liệu của hai nhà.
Chỉ `overview` mới đọc nhiều entity.

## 2. Thêm một nhà mới — chỉ cấu hình

1. Tạo device bộ điều khiển của nhà mới (VENT-005, hiện đang PAUSED).
2. Dùng Entity Alias lọc **theo loại thiết bị**, không gán ID cứng. Alias đó tự nhận nhà mới.
3. Widget `overview`: gán alias nhiều entity. Mỗi entity thành một thẻ nhà.
4. Widget chi tiết: dùng alias kiểu `stateEntity` theo tham số state `selectedBarnId`/`barnId`.

Không phải sửa script widget cho mỗi nhà thêm vào.

## 3. Settings của từng widget

| Khóa | Ý nghĩa |
|---|---|
| `component` | Thành phần hiển thị: `overview`, `header`, `kpis`, `synoptic`, `controller`, `metrics`, `history`, `alarms`, `settings` |
| `sourceMode` | `demo` dùng fixture nhúng; `live` đọc subscription. Live **không bao giờ** rơi về fixture |
| `keyMap` | Ánh xạ khóa semantic của contract → tên telemetry thật, ví dụ `{"indoorTemperatureAvg": "temp_avg"}` |
| `freshnessMs` | Ngưỡng dữ liệu cũ cho từng khóa. **Chưa khai thì quality là `UNKNOWN`**, không tự nhận `CURRENT` |
| `sourceIdentity` | Ép widget chi tiết bám đúng một entity id |
| `context` | Nhãn trại/khu/nhà khi không lấy từ state params |
| `alarmScope` | Ghi chú phạm vi alarm đã xác minh |

Widget `overview` cần tối thiểu các khóa: `fanStage`, `operatingMode`, `controllerOnline`,
`equipmentFaultActive`, `externalHighTemperatureAlarm`.

## 4. Quy tắc dữ liệu đã cài trong adapter

- Chưa khai `keyMap` → `UNKNOWN`, không phải `0` và không phải `N/A`.
- Chuỗi rỗng không thành `0`; số `0` thật giữ nguyên là `0`.
- Chỉ khóa có trong `mapping.notConfigured` mới thành `NOT_CONFIGURED`; thiếu telemetry vẫn là `UNKNOWN`.
- Mã enum hoặc mã run sai → `UNKNOWN`, và quality cũng hạ xuống `UNKNOWN`.
- `STALE` khác `OFFLINE`; timestamp tương lai → `UNKNOWN`.
- Thẻ nhà: chỉ xét cờ cảnh báo **đã khai trong `keyMap`**. Cờ chưa khai là không áp dụng,
  không mặc định là "bình thường". Không cờ nào được khai → `UNKNOWN`.
- "Cảnh báo đang mở" ở màn Tổng quan để `--`: con số này thuộc alarm của nền tảng, không suy
  từ danh sách nhà.

## 5. Chuyển sang dữ liệu thật

1. Kỹ sư PLC điền `plc_source` và bố trí dữ liệu vào vùng mirror `D550–D959`.
2. Gán datasource/alias cho từng widget.
3. Điền `keyMap` và `freshnessMs`.
4. Đổi `sourceMode` thành `live`.
5. Kiểm: không widget nào hiện `MULTIPLE_ENTITIES_REJECTED`, và `mapping.status` là `MAPPED`.

Deploy lên dashboard live cần một task được duyệt riêng; VENT-010 chỉ dựng payload cục bộ.

## 6. Bằng chứng

`docs/ventilation/dashboard/evidence/vent010-*.png`, chụp bằng
`tests/capture_vent010_evidence.py` trên harness cục bộ:
demo 1366 và 390, live chưa gán datasource (hiện thông báo hướng dẫn), và chế độ subscription.
