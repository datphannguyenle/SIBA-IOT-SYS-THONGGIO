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

---

## Refinement 1 — kế hoạch (APPROVED — VENT-006 CONTROLLED VISUAL REFINEMENT UPDATE)

Phần trên giữ nguyên làm bằng chứng lần tạo. Refinement ghi nối tiếp tại đây.

### Chẩn đoán đầy đủ trước khi sửa (chỉ đọc)

So computed style MỌI phần tử của widget trên live với harness sạch (không CSS toàn cục),
4 state: 15 loại lệch, cùng một nguồn là typography Material toàn cục của TB:
`h2` 700/normal → 400/51.2px; `h3` 700 → 500; `p` line-height normal → 19.2/17.6px;
`strong` 700 → 500; `table/th/td` (và `b`, `span` bên trong) Arial 14px → Roboto 16px.

### Issue 1 — sửa trong phạm vi widget

`dashboard/thingsboard-reset.css` (nạp TRƯỚC `dashboard.css` trong `templateCss`, chỉ selector có
gốc `.vent-demo-root`): `h2,h3` 700/normal; `p` line-height normal; `:where(b,strong)` 700;
`:where(table,th,td)` kế thừa font. Class của bản đã duyệt (vd `.kpi__value` 600, `.data-table th`
12px) vẫn thắng nhờ thứ tự nguồn. Harness mới giả lập đúng các giá trị TB đo được: payload cũ
`7cb9621` tái hiện lệch; payload mới cho computed style giống hệt harness sạch.

### Issue 2 — quyết định

Thử CHỈ ĐỌC qua query `?hideToolbar=true` (frontend đọc tham số này vào cùng getter với setting):
toolbar FAB biến mất nhưng tenant admin nhận nút nổi `edit` (x 1872–1912, y 72–112) che CẢ hai góc
phải badge — tệ hơn. Vì vậy KHÔNG đổi dashboard; giữ toolbar và chừa 48px bên phải hàng tiêu đề
(`.vent-demo-root .vent-header__top{padding-right:64px}` trong `thingsboard-widget.css`).

### Phạm vi ghi dự kiến

Chỉ 1 UPDATE widget type `b9fa9280-…` (thay `templateCss`; `defaultConfig` giữ nguyên chuỗi live vì
TB nén JSON, nội dung giống hệt). Dashboard `b9ff4d70-…` không cần update (cấu hình live = build).
Standalone VENT-003 giống từng pixel (6/6).

### Refinement 1 — kết quả sau update

**Hồi quy** (`evidence/vent006_refinement_regression.json`) — ĐẠT: Khử mùi v27, SIMULATION v9, MUGE
v107 không đổi (sha256 đầy đủ); bundle `siba_custom_ui` 15 không đổi; asset 8412, device 8186,
dashboard 10, widget type tenant 20, bundle tenant 1 — không đổi, không object mới.

**Computed style trên live** (`evidence/vent006_refinement_typography_diff.json`): so 380 phần tử
(4 state, 1920) với harness sạch → **0 loại lệch** (trước refinement: 15). Giá trị đo:
`h2` ['700', 'normal', 'Arial', '17px'], `h3` ['700', 'normal', 'Arial', '13px'], `p` ['400', 'normal', 'Arial', '12px'], tiêu đề `strong` ['700', 'normal', 'Arial', '18px'], `.kpi__value` ['600', 'normal', 'Arial', '26px'],
`th` ['700', 'normal', 'Arial', '12px'], `td` ['400', 'normal', 'Arial', '14px'], `td b` ['700', 'normal', 'Arial', '14px'] (định dạng: weight, line-height, font, size).

**UI** (`evidence/vent006_refinement_ui_verification.json`) — ĐẠT 4 state × 1920 (cửa sổ) và 390
(iframe, innerWidth 390): 4 góc badge `DEMO DATA` đều là phần tử badge (`elementFromPoint`), không
bị FAB che; typography như trên; điều hướng qua `stateController` (`?state=`, hash rỗng) và quay về
`default`; 1 side menu; không tràn ngang; giá trị fixture, màu quạt, khoảng trống lịch sử, cảnh
báo chỉ đọc giữ nguyên.

Ảnh mới (không ghi đè ảnh lần tạo): `evidence/vent006r-{default,vent-detail,vent-history,vent-alarms}-{1920,390}.png`.

Kết luận: `VISUAL PARITY: PASS` — hai lệch đã hết. Không khẳng định giống từng pixel.
