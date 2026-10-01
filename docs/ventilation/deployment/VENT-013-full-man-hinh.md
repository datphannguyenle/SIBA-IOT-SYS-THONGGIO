# VENT-013 · Dashboard thông gió full màn hình (01/10/2026)

Thay baseline v1 ở điểm "trang Giám sát được cuộn dọc ngắn". Áp dụng cho 3 dashboard đang chạy:
`DB-30-VEN-DETAIL-V1-DEMO` (v17), `…-SIM` (v5), `…-GATEWAY-SIM` (v10).

## Quy tắc bố cục (nguồn chân lý: `build_vent_modular.LAYOUTS`)

- Mọi trang cùng **tổng 21 hàng**, header **3 hàng**, `autoFillHeight` bật ở mọi trang. Nếu một trang có tổng
  hàng khác, hàng của trang đó cao khác và header nhảy khi đổi tab (bẫy #36 trong kit).
- Giám sát: header 3 · KPI 3 · sơ đồ 9 + thông số 6 (cột trái 16/24) · bộ điều khiển 15 (cột phải 8/24).
- `mobileHeight` là **số hàng** của lưới, nằm trong `layouts.main.widgets[id]` (px = hàng×30−6); `config.mobileHeight` không có tác dụng.
- Widget luôn vừa khung được cấp (`dashboard/modular-fit.css`); vùng dài tự cuộn trong panel. Widget vẽ lại mỗi 5 giây
  nên `modular.js` giữ vị trí cuộn và ô tìm kiếm (`capture`/`restore`).
- Biểu đồ lịch sử vẽ theo kích thước THẬT của khung (viewBox = pixel), đo rồi vẽ lại một lần; trước đây viewBox cố định 720×280.
- Sửa kèm: đường "Độ ẩm" của biểu đồ chưa có kiểu vẽ nên bị tô đen (lỗi có sẵn); nay màu xanh lá nét đứt.

## Triển khai và xác minh

- `deploy/thingsboard/vent013_fit_deploy.py` (`--widgets`, `--dashboards DEMO,SIM,GATEWAY`, `--dry-run`): sao lưu bản cũ vào
  `~/siba-data/vent013-backup/` (ngoài repo), chỉ thay phần bố cục + 5 widget type, chứng minh không đổi gì khác, đọc lại sau khi ghi.
  5 widget type `siba_vent_demo.modular_*` DÙNG CHUNG cho cả 3 dashboard nên CSS đổi cùng lúc.
- `deploy/thingsboard/verify_vent013_fit.py [DEMO|SIM|GATEWAY]`: Firefox thật, 1366×768 / 1536×734 / 1920×1080 / 900 px / di động 390 px
  (iframe). Đo cuộn cấp dashboard, header nhảy giữa tab, panel bị cắt/để trống, chiều cao di động đúng số hàng. Kết quả: **0 vấn đề** cả 3 bản.
- Lưu ý khi kiểm: bản DEMO chỉ nhà **ND2-1** có dữ liệu chi tiết; chọn nhà khác chỉ ra thông báo ngắn và phép đo "đạt" vô nghĩa.
  Bộ kiểm báo lỗi nếu trang chi tiết chỉ hiện thông báo.

## Giới hạn đã biết

- Laptop 1366×768: trang Giám sát vẫn có 3 panel tự cuộn bên trong (sơ đồ + thẻ cửa chớp, thông số, cột bộ điều khiển) vì nội dung
  nhiều hơn chiều cao màn hình; từ 1920×1080 hiện đủ.
- Trang Lịch sử của SIM/GATEWAY hiện "chưa có mẫu lịch sử" khi bộ nạp mô phỏng đã dừng (dữ liệu "cũ"); không phải lỗi bố cục.
- Chỉ đổi giao diện: không đổi dữ liệu, alarm, rule, RPC. PR #3 chưa merge.
