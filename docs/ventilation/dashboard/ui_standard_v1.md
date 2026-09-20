# Chuẩn tham chiếu UI giám sát SIBA — VENT-008

Ngày 20/09/2026. Chuẩn tham chiếu từ dashboard thông gió demo, kế thừa `.stitch/DESIGN.md`;
không phải thiết kế lại nền tảng và không phải phê duyệt dữ liệu/điều khiển production.

## Bề mặt dùng chung

- Giữ shell ThingsBoard hiện hữu: thanh SIBA teal, sidebar trắng; module không dựng sidebar thứ hai.
- Canvas navy, panel phẳng viền mảnh, góc 6 px; màu lấy từ `.stitch/DESIGN.md` và CSS nguồn.
- Cấu trúc: tiêu đề/phạm vi → tab → KPI → sơ đồ/bảng → thông tin nguồn và thời điểm.
- KPI hiển thị giá trị, đơn vị, chất lượng và thời điểm riêng; không tô mọi thứ thành cảnh báo.
- Cỡ chữ/line-height cần reset trong widget để không phụ thuộc CSS toàn cục của ThingsBoard.
- Nhãn người vận hành bằng tiếng Việt; mã semantic vẫn giữ trong model và thuộc tính DOM.

## Ngữ nghĩa bắt buộc

- Tách trạng thái thiết bị, kết nối bộ điều khiển và độ mới dữ liệu. STALE không đồng nghĩa OFFLINE.
- `null`/thiếu → `--`; số 0 vẫn là 0; STOPPED khác UNKNOWN, NOT_CONFIGURED khác thiếu mẫu.
- Không gắn số liệu nhà A lên nhà B. Nhà không có chi tiết phải có thông báo và đường quay lại.
- Ghi rõ phạm vi lịch sử/cảnh báo. Danh sách cảnh báo toàn trại không được giả làm truy vấn một nhà.
- Không suy ra lỗi từng quạt từ cờ lỗi cấp hệ thống. Không tạo mẫu số cấp thông gió chưa xác minh.
- Chuyển động quạt chỉ dành cho RUNNING + CURRENT + ONLINE; tắt khi giảm chuyển động được bật.
  Animation minh họa trạng thái, không mô phỏng tốc độ thật hay chứng minh phản hồi cơ khí.
- Demo có badge bền vững, dữ liệu cố định và nguồn cô lập. Không lấy fixture làm bằng chứng runtime.

## Tương tác và biểu đồ

- V1 chỉ điều hướng, tìm kiếm/lọc tại chỗ và đọc dữ liệu; không nút lệnh, editor, RPC hoặc ghi tham số.
- Tab hiện hành có `aria-current`; focus bàn phím dễ nhìn. Bộ lọc có nhãn, trạng thái không kết quả,
  và có thể phục hồi khi xóa nội dung tìm kiếm.
- Cùng đại lượng dùng chung thang đo: ba chuỗi nhiệt độ dùng trục °C trái; độ ẩm trục %RH phải.
- Mẫu thiếu tạo khoảng trống, không nối bắc cầu và không đổi thành 0. Điểm biểu đồ có nhãn thời gian/đơn vị.
- Bảng số liệu là đường đọc thay thế cho biểu đồ. Chưa tuyên bố đạt chuẩn accessibility đầy đủ;
  chưa kiểm bằng trình đọc màn hình thực tế hoặc mọi thiết bị cảm ứng.
- Lịch sử demo hiện là khoảng cố định; không trình bày như bộ chọn thời gian hay export production đã hoạt động.

## Kiểm chứng trước khi tái sử dụng cho hệ khác

1. Giữ tokens/component/layout, nhưng dùng contract của hệ đó; không chép enum, ngưỡng hay mapping thông gió.
2. Chụp và kiểm cả năm state ở desktop, laptop, tablet và viewport mobile **thật** 390×844.
3. Chỉ chart/sơ đồ/bảng/tab được cuộn ngang cục bộ; trang không tràn ngang. Nhãn tiếng Việt không bị cắt.
4. Kiểm chuỗi tổng quan → chọn nhà → lịch sử/cài đặt → quay lại, cả nhà có/không có chi tiết.
5. Kiểm 0, null, enum không biết, stale, offline, unconfigured và reduced-motion; quét bề mặt ghi dữ liệu/bí mật.
6. Build từ repo, deploy đúng namespace đã duyệt, phiên trình duyệt mới, đối chiếu phiên bản/hash và hồi quy hệ khác.

Các report trong `docs/ventilation/deployment/` ghi rõ phiên bản đã deploy và bằng chứng live;
tài liệu này không thay thế report kiểm chứng từng lần triển khai.
