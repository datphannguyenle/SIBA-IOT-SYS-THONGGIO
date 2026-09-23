# VENT-011 — Dữ liệu mô phỏng cho hệ thông gió

Mục tiêu: chạy được **đúng đường dữ liệu thật** (thiết bị → rule engine → subscription →
widget) mà không cần chờ PLC. Khi PLC vào, chỉ đổi `keyMap` ở cài đặt widget, không sửa code.

> Mọi số trong tài liệu này là **số mô phỏng** phục vụ kiểm giao diện. Không phải số của nhà
> cung cấp và không được dùng làm cơ sở cấu hình thiết bị thật.

## 1. Hai dashboard tách biệt

| Dashboard | Nguồn | Dùng để |
|---|---|---|
| `DB-30-VEN-DETAIL-V1-DEMO` | fixture nhúng trong widget (`sourceMode: demo`) | Duyệt giao diện, không phụ thuộc hạ tầng |
| `DB-30-VEN-DETAIL-V1-SIM` | subscription từ thiết bị `SIM-VentController` (`sourceMode: live`) | Kiểm đường dữ liệu, kiểm mapping |

Dashboard DEMO **không bị chạm tới**. Hai cái mở cạnh nhau để so sánh.

## 2. Bảy thiết bị, bảy kịch bản

Profile `SIM-VentController`, thiết bị tiền tố `SIM-VEN-` (cùng lối đã dùng cho `SIM-DEO-*`).

| Thiết bị | Kiểm điều gì |
|---|---|
| `SIM-VEN-NORMAL` | Chạy AUTO, dữ liệu đầy đủ và tươi |
| `SIM-VEN-BOUNDARY` | Cấp 0 và **số 0 THẬT** (đàn 0, lưu lượng 0) — 0 phải hiện là `0`, không phải `--` |
| `SIM-VEN-MANUAL` | Chế độ tay, quạt VFD vô cấp |
| `SIM-VEN-FAULT` | Lỗi thiết bị tổng + cảnh báo nhiệt độ cao, cấp 9 |
| `SIM-VEN-STALE` | Payload đầy đủ nhưng mốc thời gian lùi 3 giờ — phải ra `STALE`, **khác** `OFFLINE` |
| `SIM-VEN-UNKNOWN` | Chỉ gửi 3 khóa; phần còn lại **không gửi** — phải ra `--`, không được ra `0` |
| `SIM-VEN-OFFLINE` | Không gửi gì; TB tự đánh `active = false` |

Ba cặp dễ lẫn mà bộ kịch bản này phân định rạch ròi: `0` thật ≠ chưa có dữ liệu;
`STALE` ≠ `OFFLINE`; thiếu mapping ≠ thiết bị bình thường.

## 3. Quy tắc bắt buộc của đường ghi

Telemetry đi qua **access token của chính thiết bị**: `POST /api/v1/{token}/telemetry`.
Tuyệt đối không dùng `/api/plugins/telemetry/...` của phiên người dùng — đường đó ghi thẳng DB,
**không qua rule engine**, nên alarm rule sẽ không bao giờ tự sinh. Rào chắn trong
`vent011_deploy.py` chặn đường sai đó, và có test khẳng định việc chặn.

Access token lưu ở `~/.config/siba-vent011-tokens.json` (quyền 600), **không bao giờ vào repo**.

## 4. Trình tự chạy

```bash
cd ~/SIBA-IOT-SYS-THONGGIO/deploy/thingsboard
export TB_URL=http://100.86.144.207:8080 TB_USER=tenant@siba.com.vn
export TB_PASSWORD="$(cat ~/.config/siba-tb-pass)"

python3 vent011_deploy.py plan                      # chỉ đọc, kiểm trùng tên
python3 vent011_deploy.py provision --confirm-create # profile + 7 thiết bị
python3 vent011_deploy.py seed --confirm-write       # 3 giờ lịch sử + 224 cài đặt
python3 deploy_vent_modular.py execute --confirm-deploy  # cập nhật widget type
python3 vent011_deploy.py bind --confirm-create      # tạo dashboard SIM
python3 vent011_deploy.py feed --minutes 60          # bơm tiếp, mỗi phút một lượt
python3 vent011_deploy.py verify                     # chỉ đọc
python3 vent011_deploy.py teardown --confirm-delete   # xoá đúng những gì đã tạo
```

`teardown` chỉ xoá đối tượng có cờ `created_by_us` trong `vent011_manifest.json`.

## 5. Gắn dữ liệu vào widget

Hai entity alias:

| Alias | Bộ lọc | Cho widget |
|---|---|---|
| `Nhà gió mô phỏng` | `deviceType = SIM-VentController`, tên chứa `SIM-VEN-`, nhiều entity | `overview` |
| `Nhà gió đang xem` | `stateEntity` | mọi widget chi tiết và `alarmSource` |

Click một nhà ở màn Tổng quan sẽ đặt state param `entityId = {entityType, id}` — đây là thứ
alias `stateEntity` cần. Truyền id dạng chuỗi là không bind được; xem mục 7.

`keyMap` hiện là ánh xạ một-một vì bộ điều khiển mô phỏng phát đúng tên khóa semantic của
contract v0.3. PLC thật sẽ dùng tên khác: khi đó **chỉ sửa `keyMap`** trong cài đặt widget.

`controllerOnline` không phải khóa PLC — nó đọc attribute `active` do nền tảng tự quản.

`freshnessMs`: 5 phút cho khóa giám sát (chu kỳ bơm 60 giây), 7 ngày cho cài đặt (cài đặt là
hằng số cấu hình, `feed` ghi lại mỗi giờ để giữ `CURRENT`).

## 6. Thêm nhà mới

Tạo thêm thiết bị thuộc profile `SIM-VentController` với tên bắt đầu bằng `SIM-VEN-`. Alias lọc
theo loại thiết bị nên nhà mới **tự xuất hiện** ở màn Tổng quan, không phải sửa script widget.

## 7. Hai lỗi đã sửa trong đợt này

**Click nhà không bind được thiết bị.** Màn Tổng quan chỉ truyền `barnId` dạng chuỗi, còn alias
`stateEntity` của TB đọc `params.entityId` dạng `{entityType, id}`. Danh sách nhà giờ mang theo
`entityType`, và controller dựng `entityId` đúng dạng trước khi chuyển state.

**Thẻ nhà giải mã trên giá trị thô.** TB có thể giao telemetry số dưới dạng chuỗi (`"3"`). Mã
enum và cờ chỉ nhận số nguyên, nên mọi nhà sẽ ra `UNKNOWN`. Giờ giải mã trên giá trị đã chuẩn
hóa; giá trị không phải số (`"cap 3"`, `"2.5"`) vẫn ra `UNKNOWN` chứ không đoán.

## 8. Còn phải xác minh trên trình duyệt

Ba điều dưới đây **chưa** kiểm được bằng test cục bộ, phải mở dashboard SIM và soát mắt:

1. `SIM-VEN-BOUNDARY` hiện `0` ở cấp/lưu lượng, **không** hiện `--`.
2. `SIM-VEN-STALE` hiện `STALE` và vẫn `ONLINE`; `SIM-VEN-OFFLINE` hiện `OFFLINE`.
3. Click từng nhà ở Tổng quan → widget chi tiết đổi đúng thiết bị đó.
