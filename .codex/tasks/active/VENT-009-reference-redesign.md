# VENT-009 — Thiết kế lại theo ảnh đã duyệt

Status: done — phạm vi giao diện DEMO đã duyệt và triển khai, không phải production.
21/09/2026: widget4/dashboard2, nguồn087411e,APIregressionPASS,
20live state/viewport+4BarnnavigationPASS. Xem vent009_execution_report.md.
Các ghi nhận checkpoint bên dưới giữ làm lịch sử. Không tự cấp gate PLC/implementation-ready.

## Correction active — 21/09/2026

User phản hồi dashboard desktop còn cuộn toàn trang và menu nhà xuất hiện ở Tổng quan.
Đo live trước sửa: root client1016; default scroll1074, history1710, settings1592;
detail/alarms1016. Yêu cầu: desktop root không cuộn; history/settings cuộn nội bộ;
overview không có `.state-tabs`, menu chỉ có ở state nhà.
Nguồn/tests sửa local,72/72PASS; chờ deploy+live verification rồi mới done lại.

## Objective / approval

Ngày 21/09/2026, người dùng duyệt 5 ảnh tham chiếu và yêu cầu triển khai từng bước.
Thay toàn bộ style thông gió, không giữ màu cũ. Phê duyệt thiết kế và code local;
không suy thành quyền deploy ThingsBoard hoặc triển khai production.

## Scope / ownership

Bước 1: màn Giám sát, header/tab/KPI, sơ đồ nhà và thiết bị, bộ điều khiển,
dữ liệu bổ sung, thông số vận hành; local preview và kiểm thử.
MAIN tích hợp/kiểm chứng/docs và triển khai. Đã yêu cầu Terra medium nhưng chưa có
bản sửa để tích hợp; nhánh được ngắt trước khi MAIN nhận lại app.js/dashboard.css.
Một file một owner. Các màn còn lại chờ checkpoint màn mẫu.

## Inputs / design decision

Ảnh Giám sát người dùng: attachment 1bab8c69-a820-49ff-9430-8009d952496a,
`ChatGPT Image Sep 21, 2026, 10_48_13 AM.png`; bộ 5 ảnh cùng yêu cầu.
Artifact do người dùng cung cấp, không phải thiết kế Stitch mới.
Phê duyệt mới thay hướng dẫn giữ style cũ trong phạm vi module thông gió;
không sửa theme chung hoặc các hệ khác. Giá trị demo không là bằng chứng PLC.

## Forbidden scope / dependencies

Không ghi ThingsBoard, PLC, Gateway, telemetry, RPC, alarm mutation, deploy, merge.
Không thay fixture, semantic adapter, contract v0.3 hoặc tự xác nhận mapping.
Giữ null/UNKNOWN/NOT_CONFIGURED/STALE, ngữ cảnh nhà và chỉ đọc.

## Expected outputs / acceptance / evidence

Màn Giám sát chạy local, ảnh desktop đúng canvas 1672x941 và mobile thật 390px,
không tràn ngang trang; quạt/bơm/cửa gió và toàn bộ thông số vẫn có mặt.
Kiểm thử hồi quy và build local; ghi kết quả thực tế, không gọi planned là passed.
Ảnh đối chiếu là checkpoint thẩm mỹ, không tự công bố pixel-perfect.

## Gate / checkpoint

Người dùng review bản chạy màn Giám sát trước khi nhân sang 4 màn còn lại.
Deploy là gate riêng. Dừng và ghi bàn giao tại checkpoint.

### Gate bước 1 đã qua

Người dùng phản hồi “Tôi thấy đẹp”, sau đó yêu cầu “Triển khai tiếp tục”.
Cho phép mở rộng style local sang bốn màn còn lại, không cho phép deploy.

### Checkpoint bước 2 — hiện hành

Đã đồng bộ cả5state, thống kê history/alarm có nguồn từ fixture và nhãn phạm vi rõ.
71/71tests PASS13.369s,20state/viewport zero horizontal overflow;224settingkeys.
Xem report reference_redesign_checkpoint.md, ảnh/evidence vent009-step2-*.
Chưa deploy/commit/push. Bốn màn mới chờ user review, không chuyển done.

### Gate triển khai — 21/09/2026

Người dùng “OKe tôi duyệt” cho cả5màn, sau đó xác nhận “oke” khi được hỏi cho phép
deploy bản demo. Phạm vi: đúng2object demo hiện có, backup/verify; không production,
PLC hoặc hệ khác. MAIN giữ khóa thong-gio và deploy trong lượt này.
Preflight xác nhận live widget3/dashboard2 và widget khớp bản commit trước.
Lưu commit nguồn để updater kiểm nguồn sạch, không push/merge.

## Checkpoint thực tế — 21/09/2026

Bước 1 có bản chạy local; 69/69 tests PASS (lượt kiểm lại 14.441s), build --check
được kiểm trong suite. Ba viewport không tràn ngang: 1672×941,1366×768,390×844.
Ảnh và số đo: docs/ventilation/dashboard/evidence/vent009-checkpoint.json.
Desktop 1672 có nội dung cao 944px (cuộn dọc 3px); laptop/mobile cuộn dọc và sơ đồ
cuộn ngang cục bộ. Không công bố fit/pixel-perfect. Chưa deploy, commit hoặc push.
Chờ review hình thức màn mẫu; bản vẽ SVG ít chi tiết hơn ảnh tham chiếu, chưa phải
bản tái tạo chất liệu 3D. Cần xác nhận mức chi tiết trước khi nhân sang 4 màn khác.
