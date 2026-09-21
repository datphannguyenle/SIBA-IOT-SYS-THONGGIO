# VENT-009 — checkpoint màn Giám sát

> **Đã hoàn tất triển khai demo:** người dùng duyệt5màn và xác nhận deploy.
> Xem `../deployment/vent009_execution_report.md`: widget4/dashboard2,20livechecksPASS.
> Nội dung “chưa deploy/chờ review” bên dưới là nhật ký lịch sử, không còn trạng thái hiện hành.

> **Checkpoint hiện hành: bước 2 — cả năm màn local.** Người dùng đã chấp nhận màn
> Giám sát và yêu cầu triển khai tiếp. Các ghi nhận bước1 bên dưới là lịch sử.

## Quyết định người dùng — 21/09/2026

Thiết kế lại toàn bộ lớp hiển thị của 5 màn theo bộ ảnh đính kèm.
Người dùng duyệt hướng thiết kế, yêu cầu triển khai từng bước; không phê duyệt deploy.
Màu/style cũ không còn là chuẩn cho module thông gió. Hệ khác và vỏ quản trị giữ nguyên.
Giá trị hiển thị là demo; tiêu chí nghiệp vụ là đúng ý nghĩa, đơn vị và trạng thái.

## Bước hiện tại

Chỉ màn Giám sát và header/tab của màn này. Tái dùng adapter/contract/fixture/navigation,
thay lớp hiển thị. Các màn còn lại chưa được gọi là hoàn thành hoặc đồng bộ.
Nguồn thiết kế là ảnh người dùng đã duyệt, không sinh thêm bản thay thế qua Stitch.
SVG/CSS nguyên gốc cho thiết bị giúp tách trạng thái động khỏi hình nền; không dùng ảnh
chứa số liệu cố định để giả làm dashboard.

## Căn cứ màu

Ảnh `ChatGPT Image Sep 21, 2026, 10_48_13 AM.png`, attachment
`1bab8c69-a820-49ff-9430-8009d952496a`, kích thước 1672×941.
Đọc pixel bằng Pillow ngày 21/09/2026: vùng mép nền (4,114)-(25,890) có màu trội
RGB (0,24,39); vùng controller (1190,320)-(1630,550) có màu trội (1,31,50).
Đây là mẫu màu ảnh raster/gradient, không phải tuyên bố có file thiết kế gốc.

## Kiểm chứng

- Trước chỉnh sửa: 67/67 unit/browser tests PASS, 12.170s.
- Trang local mới: `dashboard/design-preview.html#vent_detail`, bỏ vỏ preview nền tảng
  để so đúng canvas; không phải thay đổi ThingsBoard live/fullscreen.
- Bộ chụp mới: `tests/capture_vent009_checkpoint.py`; kết quả sau chỉnh sửa ghi ở cuối.

## Ranh giới

Không tự xác nhận nguồn PLC, không đổi fixture/adapter/contract, không RPC/write API.
Không bỏ thông số chỉ để giống số ô trong ảnh. UNKNOWN, NOT_CONFIGURED, STALE phải giữ.
Sơ đồ là minh họa, không phải chứng nhận cấu hình lắp đặt thực tế.

## Checkpoint kế tiếp

Người dùng review ảnh bản chạy local trước khi mở rộng các màn khác.
Local pass không đồng nghĩa live pass. Deployment cần phê duyệt riêng.

## Kết quả bước 1 — 21/09/2026

- Header/tab/KPI, nền và panel được thay bằng navy/petrol/cyan theo ảnh.
- Sơ đồ SVG mới có nhà, sáu quạt, hai bơm, hai cửa gió; trạng thái lấy từ VM.
- Hai panel controller/bổ sung riêng; giữ 8 thông số vận hành, chi tiết thiết bị
  nằm trong vùng có thể mở rộng. Fixture/adapter/contract không thay đổi.
- MAIN tự triển khai sau khi nhánh Terra medium bị ngắt mà chưa có bản sửa.
  Không có Stitch/imagegen mới; ảnh tham chiếu người dùng là nguồn thiết kế.
- Kiểm lại 69/69 tests PASS, 14.441s. git diff --check PASS.
- 1672×941,1366×768,390×844: không tràn ngang toàn trang; đủ 6 quạt,
  không có input ghi. Xem evidence/vent009-checkpoint.json và ảnh cùng tiền tố.
- Ảnh được chụp full-page desktop: chiều cao nội dung 944/982px, không giả là
  vừa hoàn toàn viewport. Mobile 390px thật qua iframe, sơ đồ pan cục bộ.
- Giới hạn hình thức: SVG nguyên gốc còn đơn giản hơn chất liệu thiết bị 3D trong
  ảnh mẫu; chưa kết luận đạt visual parity. Chưa có legend riêng như ảnh mẫu.
- Bốn màn khác vẫn giữ style cũ trong checkpoint này. Không ghi ThingsBoard,
  không deploy/commit/push, chưa kiểm bản redesign live.

## Bước 2 — đồng bộ bốn màn còn lại, 21/09/2026

- Tổng quan: KPIicon, viền/navy/cyan mới,3×2nhà desktop, cảnh báo ưu tiên và minh họa.
- Lịch sử: nền/bảng/biểu đồ và KPI mới; trung bình số học của các mẫu số hợp lệ,
  nhãn nêu rõ không là trung bình theo thời gian. Giữ khoảng6giờ hiện có, không
  giả chức năng24h/7ngày/datefilter/export hoặc dữ liệu cấp quạt lịch sử.
- Cảnh báo:3active từfixture;2MAJOR/1WARNING, donut đồng nhất; nhãn toàn trại.
  Tìm kiếm chỉ lọc bảng, không đổi thống kê; ghi rõ. Đã xử lý hôm nay thiếu nguồn → --.
- Cài đặt:6nhóm,224keys,10/10/9slot; bảng ngang/dọc cuộn nội bộ và headersticky.
- Màn Giám sát giữ bản được chấp nhận; bốn màn mới chưa được tự coi là user-approved.
- Main làm trực tiếp vì renderer/CSS dùng chung một owner và tận dụng chứng cứ đã có;
  không gọi lại nhánh Terra đã dừng. Không external design mới hoặc effort escalation.

### Kiểm chứng

71/71tests PASS13.369s, bao gồm adapter,read-only,navigation,missingdata,motion,
CSS ThingsBoard hostile harness,buildidentity và tests2thống kê mới. Diff whitespacePASS.
20captures:5state×4viewport1672×941,1366×768,820×1180,390×844 (iframe thực).
Không tràn ngang toàn trang; settings224keys tại mọi viewport; không inputghi.
Đã xem ảnh desktop của bốn màn mới. Không tuyên bố kiểmthử trìnhđọc màn hình/tất cảbrowser.
Ảnh fullpage, không giả fit một màn: lịch sử/cài đặt dài nên có cuộn dọc.
Xem evidence/vent009-step2-checkpoint.json. Nguồn fixture/adapter/contract không thay đổi.

### Bàn giao

URLlocal: http://127.0.0.1:8765/dashboard/design-preview.html#default (chỉ cùng máy).
Đã kiểmHTTP200 trong lượt này; server tạm có thể cần khởi động lại khi đổi phiên.
Chưa deploy, không ghi ThingsBoard/PLC/Gateway/telemetry, không commit/push.
Chờ review bốn màn; deployment là gate riêng. Khóa thông gió nhả tại checkpoint.
