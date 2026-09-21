# VENT-009 — triển khai demo đã duyệt

## Kết quả — 21/09/2026

Người dùng duyệt cả5màn và xác nhận deploy demo. Hoàn tất lúc14:03:45+07,
commit nguồn `087411efbaf99d6a1e868bb3c5aeeba8e5832349`.
Chỉ1POST `/api/widgetType`: widget `b9fa9280-b26a-11f1-83ad-9912edc644d2`
từ version3→4. Dashboard `b9ff4d70-b26a-11f1-83ad-9912edc644d2` version2
NO-OP vì cấu hình đã tương đương; không gửi update thừa.

## Bằng chứng

- GET preflight: `evidence/vent009_readonly_preflight.json`, live khớp commit trước.
- Backup đúng object/version trước ghi: `evidence/vent008_before_update_vent009.json`.
- Journal: `evidence/vent008_execution_vent009.json` (tên script VENT-008 được tái dùng
  với run-id mới vent009; không chạy lại run webp hoặc ghi đè backup cũ).
- API regression: `evidence/vent008_regression_vent009.json`, payloadmatch cả2object,
  protected dashboards/bundle/counts không đổi. Verification không mutation.
- Live Firefox phiên mới cho từng viewport,20state/viewport và4kiểm nhà/recoveryPASS:
  `evidence/vent009_ui_verification_20260921T140351+0700.json`, ok=true.
- Viewports1920×1080,1366×768,820×1180,390×844 iframe thực. Ảnh `vent009-*.png`.
- Kiểm thêm DOM live:4tab đúng nhãn, opacity1, màu trắng/cyan, panel gradient
  rgb1,40,61→rgb0,28,45. Đã xem ảnh live Giám sát/Cảnh báo.
- Local trướcdeploy71/71testsPASS18.012s. Không thay adapter/fixture/contract.

## An toàn / khôi phục

Không sửa PLC/Gateway,thiết bị,telemetry,attribute,RPC,alarm,rootchain,bundle chung.
Giữ backup và fingerprint để khôi phục đúng nội dung nếu cần. Chưa thực thi rollback;
phải kiểm concurrent changes trước, không retry write mù. Không push/merge PR.
Chỉ là demo fixture, không xác nhận nguồn dữ liệu vật lý hay implementation-ready.

## URL

http://100.86.144.207:8080/dashboards/b9ff4d70-b26a-11f1-83ad-9912edc644d2

URLmạngriêng; máy người dùng phải truy cập được địa chỉ này. Nếu còn cache UI cũ,
Ctrl+Shift+R. Vỏ quản trị ThingsBoard giữ nguyên theo phạm vi được duyệt.

## Điều phối

MAIN thực hiện tuần tự deploy và browserverification, giữ khóa thông-gió/deploy;
không giao thêm agent vì chỉ một phiên sở hữu tài nguyên mutation. Không tăng effort.
Checkpoint hoàn tất scope giao diện demo; physicalintegration vẫn là task/gate khác.
