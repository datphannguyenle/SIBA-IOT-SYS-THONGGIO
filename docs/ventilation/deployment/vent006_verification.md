# VENT-006 — Verification

## Hồi quy (evidence/vent006_regression.json) — ĐẠT

| Đối tượng | Trước | Sau |
|---|---|---|
| SIBA · Khử mùi | v27 `99c899a8188f05b4` | v27 `99c899a8188f05b4` |
| SIBA · Khử mùi · SIMULATION | v9 `faccbe9141863dd0` | v9 `faccbe9141863dd0` |
| MUGE · Tổng quan trại | v107 `ed99833e5fa97194` | v107 `ed99833e5fa97194` |
| Bundle `siba_custom_ui` | 15 · `af87a8ba7849ac09` | 15 · `af87a8ba7849ac09` |
| Số bundle tenant | 1 | 1 |
| Asset | 8412 | 8412 |
| Device | 8186 | 8186 |
| Dashboard | 9 | 10 (+1 dự kiến) |
| Widget type tenant | 19 | 20 (+1 dự kiến) |

So sánh dùng sha256 đầy đủ của cấu hình (không chỉ tiền tố 16 ký tự).

## UI thật (evidence/vent006_ui_verification.json) — ĐẠT kiểm tự động

Phương pháp: Firefox headless qua geckodriver, hồ sơ mới mỗi lần (không cache template = nạp lại
cứng), đăng nhập qua form UI. Desktop: cửa sổ 1920×1080. Mobile: TB nằm trong iframe 390×844
trên trang cục bộ, vì Firefox không thu cửa sổ dưới ~500px (lần chạy đầu đo được innerWidth
500 nên đã bỏ, chạy lại bằng iframe, innerWidth 390).

Kiểm ở cả 4 state × 2 khổ: badge `DEMO DATA`; tab active đúng; chuyển state qua
`stateController` (URL đổi `?state=…`, `location.hash` rỗng); quay về `default` được; không có
khung giả lập; đúng một side menu nền tảng; không tràn ngang trang lẫn widget; màu panel đúng.
Riêng từng state: tag `PILOT · DEMO` / `DEMO`×3 / `SYNTHETIC`×2; 6 quạt RUNNING×3/STOPPED/
UNKNOWN/FAULT với màu xanh/xám/đỏ; KPI 27.8/31.2/29.1/74; bảng điều khiển `4 / 6`, 3 chỉ số
phụ `--`; lịch sử có khoảng trống (2 lệnh `M`), có đường cảm nhận, ô `--`; cảnh báo không có
nút/ô nhập.

Ảnh: `evidence/vent006-{default,vent-detail,vent-history,vent-alarms}-{1920,390}.png`.

## Lệch hiển thị phát hiện khi xem ảnh (chưa sửa — cần duyệt cập nhật)

1. **Typography toàn cục của TB rò vào widget.** Đo computed style trên live: `.panel__head h2`
   `font-weight 400`, `line-height 51.2px` (bản đã duyệt: đậm, dòng thường); `b/strong` của tiêu đề
   `500`. Hệ quả: tiêu đề panel nhạt hơn và đầu panel cao hơn ~30px.
   Đề xuất: thêm vào `dashboard/thingsboard-widget.css` reset có tiền tố gốc
   `.vent-demo-root h2,.vent-demo-root h3{font-weight:700;line-height:1.25}` và
   `.vent-demo-root b,.vent-demo-root strong{font-weight:700}`, rồi CẬP NHẬT widget type.
2. **Nút FAB bật/tắt toolbar dashboard** (`mat-fab-trigger`, 36×36 tại x 1866–1902, y 68–104)
   đè ~25px lên mép phải badge `DEMO DATA` (x 1802–1891). Đề xuất: đẩy badge/nội dung đầu widget
   vào trong ~48px ở cạnh phải, hoặc cập nhật dashboard `hideToolbar: true`.

Cả hai cần một lệnh UPDATE (widget type và/hoặc dashboard), nằm ngoài phê duyệt hiện tại (chỉ
CREATE). Không tự sửa. Kết luận parity: `VISUAL PARITY: PASS WITH MINOR REFINEMENT`, không khẳng
định giống từng pixel.
