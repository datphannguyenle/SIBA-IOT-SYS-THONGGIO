# VENT-010 — Triển khai kiến trúc modular lên ThingsBoard Live

## Kết quả — 23/09/2026

Người dùng duyệt deploy VENT-010 lên ThingsBoard.
Hoàn tất triển khai lúc 11:13:09+07:00 trên tenant `http://100.86.144.207:8080`.

Bản live của demo thông gió đã được chuyển đổi hoàn toàn từ monolithic widget sang **kiến trúc modular 5 widget types độc lập**:
- `tenant.siba_vent_demo.modular_static` -> ID: `93516710-b6fe-11f1-a719-7da6129c6745` (Version 2)
- `tenant.siba_vent_demo.modular_latest` -> ID: `93544d40-b6fe-11f1-a719-7da6129c6745` (Version 2)
- `tenant.siba_vent_demo.modular_timeseries` -> ID: `93569730-b6fe-11f1-a719-7da6129c6745` (Version 2)
- `tenant.siba_vent_demo.modular_alarm` -> ID: `9358ba10-b6fe-11f1-a719-7da6129c6745` (Version 2)
- `tenant.siba_vent_demo.modular_overview` -> ID: `935adcf0-b6fe-11f1-a719-7da6129c6745` (Version 2)

Dashboard `DB-30-VEN-DETAIL-V1-DEMO` (`b9ff4d70-b26a-11f1-83ad-9912edc644d2`) được nâng cấp lên **Version 6**:
- Gồm 13 widget instances phân bổ trên 5 states chuẩn:
  - `default` (Tổng quan): 2 widgets (`header`, `overview`)
  - `vent_detail` (Giám sát): 5 widgets (`header`, `kpis`, `synoptic`, `controller`, `metrics`)
  - `vent_history` (Lịch sử): 2 widgets (`header`, `history`)
  - `vent_alarms` (Cảnh báo): 2 widgets (`header`, `alarms`)
  - `vent_settings` (Cài đặt): 2 widgets (`header`, `settings`)

## Bằng chứng kiểm tra và an toàn

- **Preflight baseline:** `evidence/vent010_preflight.json` ghi nhận snapshot hệ thống trước khi triển khai.
- **Backup live dashboard:** `evidence/vent010_pre_deploy_dashboard_backup.json` lưu lại toàn bộ cấu hình dashboard trước khi thực hiện mutation.
- **Manifest triển khai:** `deploy/thingsboard/vent010_manifest.json` và `evidence/vent010_execution.json` ghi nhận nhật ký 6 thao tác POST (5 widget types + 1 dashboard).
- **Snapshot bảo vệ nguyên vẹn:**
  - Không có bất kỳ thay đổi nào đối với các dashboard được bảo vệ (`SIBA · Khử mùi`, `SIBA · Khử mùi · SIMULATION`, `MUGE · Tổng quan trại`).
  - Bundle dùng chung `siba_custom_ui` 100% không đổi.
  - Số lượng Asset và Device của tenant không đổi.
  - Không ghi dữ liệu vào PLC, Gateway, thiết bị thật, telemetry, attribute, rule chain hay RPC.
- **REST API Verification:** `deploy_vent_modular.py verify` -> `VERIFICATION COMPLETE: PASS`.

## Hướng dẫn truy cập và kiểm thử

- **URL Dashboard Live:**
  `http://100.86.144.207:8080/dashboards/b9ff4d70-b26a-11f1-83ad-9912edc644d2`
- **Cách vào từ giao diện ThingsBoard:**
  1. Đăng nhập tài khoản `tenant@siba.com.vn`.
  2. Chọn menu **Dashboards** ở thanh điều hướng bên trái.
  3. Tìm dashboard `DB-30-VEN-DETAIL-V1-DEMO` (dòng đầu tiên).
  4. Bấm vào dòng dashboard hoặc mở chi tiết rồi bấm **Open dashboard**.
  5. Nếu trình duyệt còn cache UI cũ, bấm `Ctrl + Shift + R` (hoặc `Cmd + Shift + R`) để nạp lại toàn bộ bundle mới.

## Khôi phục (Rollback)

Nếu cần rollback về bản trước khi triển khai VENT-010:
```bash
python3 deploy/thingsboard/deploy_vent_modular.py rollback --confirm-rollback
```
Lệnh trên sẽ khôi phục lại dashboard `DB-30-VEN-DETAIL-V1-DEMO` từ file backup `vent010_pre_deploy_dashboard_backup.json`.
