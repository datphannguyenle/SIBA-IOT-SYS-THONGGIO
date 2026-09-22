# VENT-009 — sửa fit desktop và phạm vi menu

## Kết quả — 21/09/2026

Đã xử lý hai phản hồi sau khi triển khai VENT-009: các trang desktop còn phải cuộn
toàn widget và trang Tổng quan hiển thị menu dành cho từng nhà. Bản sửa dùng commit
nguồn `3ff7d57eb872e26cdf29c8b227ef4ec6bf0e2022`.

- Tổng quan chỉ giữ tiêu đề, phạm vi và nhãn DEMO DATA; không còn `.state-tabs`.
- Bốn màn của nhà vẫn có menu Giám sát / Lịch sử / Cảnh báo / Cài đặt.
- Ở desktop rộng hơn 1100px, root của cả năm state không cuộn dọc.
- Lịch sử và Cài đặt giữ đủ nội dung bằng vùng cuộn nội bộ trong panel/bảng.
- Tablet và mobile tiếp tục cuộn dọc tự nhiên để không ép nội dung quá nhỏ.

## Đo trước và sau

Trước sửa tại 1920×1080, root có client height 1016px: Tổng quan scroll 1074px,
Lịch sử 1710px, Cài đặt 1592px; Giám sát và Cảnh báo 1016px.

Sau sửa, kiểm live bằng Firefox phiên mới:

| Viewport | State | Root client/scroll | Kết quả |
|---|---|---:|---|
| 1920×1080 | 5/5 | 1016/1016px | PASS |
| 1366×768 | 5/5 | 704/704px | PASS |
| 820×1180 | 5/5 | cuộn tự nhiên | PASS |
| 390×844 | 5/5 | cuộn tự nhiên | PASS |

Tổng cộng 20/20 state/viewport không có lỗi. Ở Tổng quan `active=null`; bốn state
nhà nhận đúng tab active. Ảnh live đã được xem trực quan cho Tổng quan, Lịch sử và
Cài đặt ở 1920×1080; không thấy phần nội dung bị cắt khỏi khung.

## Triển khai và bằng chứng

- Local: 72/72 tests PASS; có test desktop fit cho cả năm state và kiểm menu Tổng quan.
- Preflight chỉ đọc: `evidence/vent009_fit_readonly_preflight.json`; live khớp bản trước.
- Backup: `evidence/vent008_before_update_vent009-fit.json`.
- Thực thi: `evidence/vent008_execution_vent009-fit.json`; đúng một POST widget,
  version 4→5; dashboard version2 là NO-OP.
- Hồi quy API: `evidence/vent008_regression_vent009-fit.json`; payload widget/dashboard
  đều khớp, protected objects không đổi, verification không mutation.
- Live UI: `evidence/vent009fit_ui_verification_20260921T142344+0700.json`, `ok=true`;
  ảnh `evidence/vent009fit-*.png`.

## An toàn và giới hạn

Không sửa PLC, Gateway, thiết bị, telemetry, attribute, RPC, alarm, dashboard khác,
bundle chung hay hệ khác. Đây vẫn là dashboard demo read-only dùng fixture; kết quả
không xác nhận mapping dữ liệu vật lý hoặc production readiness. Không push/merge.

## Sửa bổ sung theo viewport thực — 22/09/2026

Ảnh người dùng cho thấy Edge/browser zoom khoảng125% và thanh công cụ dashboard mở;
viewport CSS tương đương1536×734, phần widget chỉ còn620px chiều cao. Bản trước đã
ẩn overflow root nhưng chưa kiểm footer/panel cuối có nằm trong vùng nhìn thấy nên
detail bị clip. Tiêu chí cũ được đánh dấu chưa đủ.

Bản sửa cuối thêm chế độ `vent-compact-height`, giới hạn widget theo phần viewport
thực còn lại và refit sau animation đóng/mở toolbar. Header, KPI, sơ đồ, bảng thông số,
bộ điều khiển và dữ liệu bổ sung được nén có chủ đích; không ẩn dữ liệu semantic.
Trang cảnh báo có layout compact riêng; history/settings vẫn cuộn nội bộ.

- Local:73/73 tests PASS, gồm mô phỏng1536×734 + offset toolbar114px cho cả5state.
- Live widget: version5→10 qua các vòng sửa có backup/journal riêng; vòng cuối version10.
- Preflight phát hiện dashboard đã ở version3 thay vì version2. Không ghi đè: mọi vòng
  chỉ POST đúng widget demo và xác minh dashboard version3 giữ nguyên fingerprint.
- Live cuối:25/25 state/viewport PASS tại1920×1080,1536×734,1366×768,820×1180,
  390×844. Ba desktop mở toolbar; root, footer và critical detail panels đều visible.
- Bằng chứng cuối: `evidence/vent009_height5_*`,
  `evidence/vent009height5_ui_verification_20260922T100046+0700.json` và ảnh
  `evidence/vent009height5-*.png`.

Không có mutation dashboard, PLC, Gateway, telemetry, RPC, alarm hoặc hệ khác.
