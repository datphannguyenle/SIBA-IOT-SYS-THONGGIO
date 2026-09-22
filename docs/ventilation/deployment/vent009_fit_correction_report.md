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
