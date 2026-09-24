# VENT-010 — Modular laptop UI and source-compatible simulation

Status: active — danh sách nhà nhiều entity đã xong, 97/97 test PASS (23/09/2026). Owner: MAIN.
User authorized implementation 2026-09-22; mở rộng phạm vi danh sách nhà live 23/09/2026.

## Objective
Replace whole-screen layout with independently configurable functional widgets, retaining
approved navy/cyan style. Readable laptop view, natural bounded scrolling, no clipped data.
Simulation and real subscription input share a semantic adapter; live mode must never fall
back to fixture. Mapping and runtime freshness remain unconfirmed until direct evidence.

## Scope / outputs
Modular renderer/style, source adapter, deterministic demo/widget/dashboard payloads,
browser and data-boundary tests, configuration instructions and evidence.
Preserve five dashboard states, home without house menu, read-only 224 settings accessible.

## Forbidden
No RPC, device/attribute/telemetry/alarm mutation, production binding, shared bundle change,
PR merge, or self-granted implementation-readiness gate.

## Acceptance / evidence
Laptop 1366x768 and constrained canvas with sidebar/header; also desktop/mobile.
No horizontal page overflow or forced hidden content. Readable chart, settings group navigation.
Independent datasource/settings per functional widget. Null/zero/unknown/stale tested.
Fixture updates and subscription updates use same rendering path. Live empty input stays unknown.
Record local vs deployed vs browser-verified separately.

## Routing / dependencies / gate
MAIN integration/review; Terra medium bounded UI/data implementation; runtime verification separate.
Depends on approved VENT-009 style and v0.3 semantic contract, not verified PLC mapping.
Gate: user review demo; real bindings require separately verified mapping and authority.


## Bổ sung 23/09/2026 — danh sách nhà đọc nhiều entity

**Giới hạn đã phát hiện:** trước đợt này, `vm.barns` chỉ đến từ fixture (`base.barns`), nên ở
`sourceMode: live` màn Tổng quan **không có đường dữ liệu thật** và lưới nhà rỗng. Thêm nhà mới
khi đó sẽ phải sửa script, không phải cấu hình.

**Đã làm:**
- `widgets/ventilation-source.js`: `barnsFromEntities()` dựng danh sách nhà từ NHIỀU entity cho
  `component: overview`; `barnSummary()` đếm nhà/trực tuyến/cần chú ý, để `activeAlarms = null`
  vì số cảnh báo thuộc alarm nền tảng. Widget chi tiết giữ nguyên ràng buộc một entity.
- Cờ cảnh báo trên thẻ nhà chỉ xét khóa ĐÃ khai trong `keyMap`; khóa chưa khai là không áp dụng.
- **Sửa lỗi thật:** `rowIdentity()` trả về object `entityId` của ThingsBoard, khiến mọi entity
  quy về cùng một chuỗi `[object Object]` và bị gom làm một. Nay lấy `entityId.id` dạng chuỗi.
  Trước khi sửa, nhiều nhà có thể bị trộn số liệu mà vẫn báo `SINGLE_ENTITY`.
- `widgets/ventilation-adapter.js`: thêm danh tính `LIVE_ENTITY` (không phải SYNTHETIC).
- `dashboard/modular.js`: màn Tổng quan rỗng hiện hướng dẫn gán datasource thay vì để trống.
- `deploy/thingsboard/build_vent_modular.py`: thêm widget type `modular_overview`
  (chạy trên TB `latest`, `singleEntity: false`, `maxDatasources: -1`); các widget khác giữ
  `singleEntity: true`. Payload build lại khớp nguồn.
- Test: 5 test nguồn cho luồng nhiều entity + 1 test build; tổng 97/97 PASS.
- Tài liệu cấu hình: `docs/ventilation/deployment/vent010_configuration.md`.
- Bằng chứng: `docs/ventilation/dashboard/evidence/vent010-*.png` qua `tests/capture_vent010_evidence.py`.

**Sai lệch so với test cũ:** `test_deterministic_build_and_native_widget_distribution` kỳ vọng
màn Giám sát có 6 widget, trong khi `LAYOUTS` khai 5. Đã lấy `LAYOUTS` làm chuẩn và đổi test sang
kiểm đúng tập thành phần. Nếu chủ ý ban đầu là 6 widget thì cần bổ sung vào `LAYOUTS`.

**Triển khai live ThingsBoard (23/09/2026):**
- Người dùng duyệt deploy VENT-010 lên ThingsBoard live.
- 5 modular widget types (`tenant.siba_vent_demo.modular_*`) đã triển khai và cập nhật lên Version 2.
- Dashboard `DB-30-VEN-DETAIL-V1-DEMO` (`b9ff4d70-b26a-11f1-83ad-9912edc644d2`) nâng cấp lên Version 6 gồm 13 widget instances trên 5 states chuẩn.
- Bằng chứng triển khai & verification: `docs/ventilation/deployment/vent010_execution_report.md` và `deploy/thingsboard/vent010_manifest.json`.
- Backup cấu hình trước deploy: `docs/ventilation/deployment/evidence/vent010_pre_deploy_dashboard_backup.json`.
- Zero mutation tới các dashboard bảo vệ và bundle chung `siba_custom_ui`.

**Chưa làm:** Chưa có dữ liệu PLC thật nên chưa kiểm được đường live end-to-end (thuộc phạm vi tích hợp vật lý).

## Sự cố 23/09/2026 — dashboard live trắng trang sau khi deploy

Bản deploy 11:16 (dashboard version 6) làm dashboard không mở được. Console:
`TypeError: Cannot read properties of undefined (reading 'entityAliasId')` trong
`validateAndUpdateDashboard`.

Nguyên nhân: TB duyệt widget kiểu `alarm` bằng `[config.alarmSource]` chứ không phải
`config.datasources`. Widget `modular_alarm` không có `alarmSource` nên mảng là `[undefined]`.
Lỗi nằm ở bước validate trước khi vẽ, nên một widget hỏng làm chết cả dashboard, mọi state.

Đã sửa trong repo (`build_vent_modular.py` sinh `alarmSource` cho instance và `defaultConfig`),
thêm `validate()` và 2 test lặp lại đúng vòng quét alias của TB. Ghi bẫy #33 vào kit.

**Đã thay thế trong cùng ngày:** người dùng đã chạy lượt sửa; dashboard live và kết quả cuối
được ghi tại VENT-011. Đoạn “chưa đẩy” chỉ mô tả checkpoint giữa sự cố. Bản sao dashboard version 5 giữ ở
`docs/ventilation/deployment/evidence/vent010_pre_deploy_dashboard_backup_v5.json`.
