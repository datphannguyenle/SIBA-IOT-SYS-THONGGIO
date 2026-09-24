# SIBA Operations UI — baseline V1

## Quyết định

Người dùng chốt ngày 24/09/2026: giao diện đang chạy của hệ Thông gió là mẫu tham chiếu
cho các đợt làm mới giao diện của hệ khác. Tên baseline: **SIBA Operations UI V1**
(`SIBA-OPS-DARK-1.0`).

Mốc triển khai được duyệt:

- dashboard `DB-30-VEN-DETAIL-V1-GATEWAY-SIM`, runtime version 8;
- source commit `cddc523` trên nhánh `feat/VENT-008-live-demo-v03`;
- bằng chứng trình duyệt tại `deployment/evidence/vent012_ui_verify.json`;
- viewport đã kiểm: 1366×768, 1536×734 và 390×844.

“Mẫu tham chiếu” nghĩa là dùng lại ngôn ngữ hình ảnh, cấu trúc điều hướng và nguyên tắc
responsive. Không sao chép dữ liệu, alarm, ngưỡng, sơ đồ thiết bị hay logic thông gió sang
hệ khác. Mỗi hệ vẫn phải giữ hợp đồng dữ liệu và nghiệp vụ riêng.

## Ngôn ngữ hình ảnh

| Vai trò | Token hiện hành | Giá trị |
|---|---|---|
| Nền dashboard | `--vm-bg` | `#001827` |
| Panel chính | `--vm-panel` | `#01283d` |
| Panel phụ | `--vm-panel-2` | `#001d2f` |
| Viền/lưới | `--vm-line` | `#075677` |
| Chữ chính | `--vm-text` | `#f0f5ff` |
| Chữ phụ | `--vm-sub` | `#acc9e8` |
| Nhấn/điều hướng | `--vm-cyan` | `#00ecf6` |
| Bình thường | `--vm-ok` | `#00e7b5` |
| Cần chú ý | `--vm-warn` | `#ffbf19` |
| Sự cố | `--vm-danger` | `#ff484d` |

- Navy đậm là nền vận hành; cyan dùng cho nhận diện, tab đang chọn và hành động điều hướng.
- Xanh lá/vàng/đỏ chỉ biểu diễn ý nghĩa trạng thái tương ứng, không trang trí tùy ý.
- Panel viền mảnh, bo 6 px, nền chuyển sắc nhẹ; tránh bóng nổi hoặc gradient sáng quá mức.
- Font hiện hành là Arial/Helvetica; cỡ chữ nội dung tối thiểu 12 px ở laptop.
- Trạng thái không chỉ dựa vào màu: luôn có nhãn chữ hoặc giá trị đi kèm.

## Cấu trúc màn hình chuẩn

### Tổng quan

- Không có menu tab cấp nhà.
- Header nêu hệ, phạm vi và provenance; tiếp theo là KPI toàn phạm vi và danh sách nhà.
- Thẻ nhà ưu tiên kết nối, độ tươi, chế độ/cấp và cảnh báo; chọn nhà mới mở màn chi tiết.

### Màn theo nhà

- Header gọn một hàng trên laptop: quay lại, tên nhà, các tab, phạm vi/nhãn nguồn.
- Tab chuẩn: Giám sát, Lịch sử, Cảnh báo, Cài đặt. Hệ khác có thể đổi tên/số tab theo nghiệp
  vụ nhưng giữ cùng kiểu điều hướng và phải giữ entity đã chọn.
- Giám sát: KPI → vùng trực quan chính + cột trạng thái → thông tin bổ sung.
- Nội dung dày được gộp có chủ đích; không tạo nhiều widget nhỏ để lại khoảng trống lớn.
- Một trang chỉ dùng một cuộn dọc tự nhiên. Cuộn nội bộ chỉ dành cho bảng rộng hoặc sơ đồ
  thật sự cần pan ngang.

## Responsive và độ vừa màn hình

- Laptop tối thiểu bắt buộc kiểm cả 1366×768 và 1536×734 khi sidebar/toolbar ThingsBoard mở.
- Không thu nhỏ toàn dashboard để “vừa”; ưu tiên nén khoảng cách, gộp nội dung và sắp xếp lại.
- Desktop: bốn màn thông tin phụ lấp viewport; Giám sát được phép cuộn dọc ngắn do sơ đồ.
- Mobile: xếp một cột, menu/tab được wrap hoặc cuộn ngang cục bộ, không tràn ngang trang.
- Không dùng chiều cao cố định khiến nội dung bị cắt; không coi `autoFillHeight` là đủ nếu nội
  dung bên trong widget không lấp ô.

## Kiến trúc widget

- Duy trì widget tách theo trách nhiệm: header, KPI, trực quan, trạng thái, lịch sử, alarm,
  cài đặt. Không biến toàn màn thành một widget nguyên khối.
- Theme/token ở lớp trình bày; semantic key, kiểu, scale và enum ở adapter/converter.
- Giá trị thiếu, `UNKNOWN`, `STALE` và `OFFLINE` phải khác nhau; số 0 hợp lệ không thành `--`.
- Nguồn demo/SIM phải hiện rõ. Giao diện không được làm dữ liệu mô phỏng trông như production.
- V1 Thông gió vẫn chỉ đọc; baseline hình ảnh không cấp quyền ghi cho bất kỳ hệ nào.

## Cách áp dụng cho hệ khác

1. Chụp baseline hiện tại của hệ đích và khóa các hành vi/dữ liệu phải giữ.
2. Lập mapping component của hệ đích sang shell, KPI, panel, tab, bảng và trạng thái V1.
3. Dùng token và spacing ở tài liệu này; chỉ thêm màu khi có ý nghĩa nghiệp vụ chưa được phủ.
4. Giữ nguyên datasource/alias/command contract; redesign không phải quyền sửa nghiệp vụ.
5. Duyệt thiết kế riêng cho hệ đích, rồi kiểm trình duyệt ở hai kích thước laptop và mobile.
6. Triển khai theo từng hệ, có rollback; không sửa theme/widget chung để ép mọi hệ đổi cùng lúc.

Các cải tiến sau này của Thông gió không tự động thay baseline. Muốn thay V1 phải tạo phiên bản
mới, ghi khác biệt và kiểm hồi quy các hệ đã tham chiếu.
