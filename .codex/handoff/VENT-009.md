# VENT-009 — hoàn tất demo và sửa fit desktop

> **Cập nhật hiện hành 22/09/2026:** đã sửa trường hợp browser zoom khoảng125% và
> toolbar ThingsBoard mở như ảnh người dùng. Widget10; dashboard live3 được giữ nguyên
> tuyệt đối vì preflight phát hiện version ngoài dự kiến. 73/73 local PASS;25/25 live
> state/viewport PASS, gồm1536×734 CSS với toolbar mở. Verify đo root, footer và panel
> detail thật sự nằm trong viewport. Ảnh `vent009height5-1536x734-vent-detail.png`.
> Không push/merge, không tác động PLC.

> **Mốc 21/09/2026 (đã thay thế bởi sửa 22/09):** phản hồi cuối đã xử lý và triển khai.
> Widget5/dashboard2(NO-OP), commit nguồn `3ff7d57`. Tổng quan không còn menu nhà;
> menu chỉ có trong4state nhà. Ở desktop1920/1366, cả5state vừa khung widget,
> không cuộn root; history/settings dùng vùng cuộn nội bộ. 72/72 local PASS và
> 20/20 live state/viewport PASS. Xem
> `docs/ventilation/deployment/vent009_fit_correction_report.md`.
> Tablet/mobile giữ cuộn dọc tự nhiên. Không push/merge; không tác động PLC.

> **Mốc trước (đã thay thế): đã deploy demo và verify live 21/09/2026.** User duyệt cả5màn
> và xác nhận deploy. Widget4/dashboard2(NO-OP),commitnguồn087411e.
> 20state/viewport+4navigationPASS; report `docs/ventilation/deployment/vent009_execution_report.md`.
> Những ghi nhận “chưa deploy/chờ review” bên dưới là lịch sử bước2, đã thay thế.
> Không chạy lại execute run-id vent009. Không push/merge. Nguồn PLC vẫn chưa xác minh.

## STATUS
Người dùng đã chấp nhận hình thức màn Giám sát (“Tôi thấy đẹp”) và yêu cầu tiếp tục.
Cả 5 màn đã đồng bộ style local; chờ review bốn màn mới, không self-approve.
Branch giữ feat/VENT-008-live-demo-v03; thay đổi chưa commit. Không deploy.

## MODELS USED
MAIN triển khai/tích hợp/kiểm chứng. Terra medium được yêu cầu, bị ngắt trước khi có
bản sửa để tích hợp. Không external design generation; dùng ảnh người dùng đã duyệt.

## FINDINGS / EVIDENCE
docs/ventilation/dashboard/reference_redesign_checkpoint.md và evidence/vent009-*.
Màu nền mẫu đo được RGB0,24,39; bản mới dùng navy/petrol/cyan.

## CHANGES
app.js/dashboard.css scope .vent-reference cả 5 state; design-preview.html;
payload local rebuild; capture_vent009_checkpoint.py và tests. Semantic sources giữ nguyên.

## TESTS
71/71 PASS,13.369s; diff --check PASS. 20 state/viewport zero horizontal overflow.
Viewport1672×941,1366×768,820×1180,390×844 thực qua iframe.
evidence/vent009-step2-checkpoint.json và ảnh vent009-step2-*.
Cài đặt224keys vẫn tồn tại; semantic source/fixture không đổi. Trang dài có cuộn dọc.

## UNCERTAIN / RISKS
Màn Giám sát đã được user chấp nhận; bốn màn mới chờ review hình thức.
Không thêm bộ chọn thời gian24h/7ngày hoặc stagehistory chưa có nguồn.
History KPI là TB số học mẫu hợp lệ, không TB theo thời gian; xử lý hôm nay chưa có nguồn → --.
Không suy local pass thành ThingsBoard live pass. Không tự deploy.
Local preview server có thể ngừng giữa phiên; kiểm trước khi gửi URL.

## NEXT RECOMMENDED ACTION
Người dùng review bốn màn mới. Deploy cần phê duyệt riêng.
Không lặp lại VENT-008 deployment. Khóa thông gió nhả khi bàn giao.
