# VENT-009 — checkpoint bước 2

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
