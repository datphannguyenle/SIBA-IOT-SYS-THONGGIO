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

## 8. Đã xác minh trên trình duyệt thật (23/09/2026)

`verify_vent011_ui.py` chạy trên Firefox thật, chỉ đọc. Kết quả thẻ nhà ở màn Tổng quan:

| Nhà | Kết nối | Dữ liệu | Chế độ | Cấp |
|---|---|---|---|---|
| NORMAL | Trực tuyến | Hiện tại | Tự động | 3 |
| BOUNDARY | Trực tuyến | Hiện tại | Tự động | **0** |
| STALE | Trực tuyến | **Dữ liệu cũ** | Tự động | 3 |
| OFFLINE | **Ngoại tuyến** | Chưa rõ | Chưa rõ | -- |
| UNKNOWN | Trực tuyến | Chưa rõ | Chưa rõ | -- |

Ba cặp dễ lẫn đều phân định đúng: `0` thật hiện là `0`; `STALE` vẫn `Trực tuyến` còn `OFFLINE`
là `Ngoại tuyến`; thiếu mapping ra `--` chứ không ra `0`. Click nhà FAULT → widget chi tiết hiện
`32 °C` (số riêng của nhà đó), tức là bám đúng thiết bị.

KPI: 7 nhà · 6 trực tuyến · 4 cần chú ý · cảnh báo đang mở `--` (thuộc alarm nền tảng).

Bằng chứng: `evidence/vent011_ui_verify.json`, `vent011-live-overview-1600.png`,
`vent011-live-detail-1600.png`.

## 9. Bốn màn chi tiết (23/09/2026)

| Màn | Kết quả | Ô ghi được |
|---|---|---|
| Giám sát | KPI và sơ đồ đúng số của nhà đã chọn | 0 |
| Lịch sử | **380 dòng** từ 3 giờ dữ liệu thật, có mốc thời gian và giá trị | 0 |
| Cảnh báo | **4 dòng**, đúng 4 alarm của nhà đang xem, không lẫn nhà khác | 0 |
| Cài đặt | đọc được **224/224** khóa, 37 dòng bảng | 0 |

Không màn nào có ô nhập hay điều khiển ghi: đúng yêu cầu chỉ xem.

## 10. Ngưỡng không hoạt động của TB

TB tự đặt `active = false` sau ngưỡng không hoạt động (mặc định 600 giây). Nên khi `feed` dừng,
sau khoảng 10 phút **mọi nhà** chuyển sang `Ngoại tuyến` và dữ liệu thành `Dữ liệu cũ`. Đó là
hành vi đúng, không phải lỗi. Muốn xem trạng thái trực tuyến thì phải giữ `feed` chạy.

`verify_vent011_ui.py` vì thế **không giả định** `feed` đang chạy: nó đọc tuổi telemetry và cờ
`active` thật từ nền tảng rồi đối chiếu hai chiều với nhãn trên giao diện.

## 11. Alarm rule

`vent011_alarms.py` gắn 6 alarm rule vào **device profile** `SIM-VentController`, không sửa Root
Rule Chain (chain đó xử lý message của MỌI thiết bị trong tenant).

| Cờ trong contract | Tên alarm | Mức độ (ĐỀ XUẤT) |
|---|---|---|
| `equipmentFaultActive` | Lỗi thiết bị thông gió | CRITICAL |
| `externalHighTemperatureAlarm` | Nhiệt độ cao (thermostat ngoài) | MAJOR |
| `temperatureHighAlarmActive` | Nhiệt độ trong chuồng cao | MAJOR |
| `temperatureLowAlarmActive` | Nhiệt độ trong chuồng thấp | MINOR |
| `perceivedTemperatureHighAlarmActive` | Nhiệt độ cảm nhận cao | MINOR |
| `perceivedTemperatureLowAlarmActive` | Nhiệt độ cảm nhận thấp | MINOR |

> **Mức độ là đề xuất của dự án.** Contract v0.3 không quy định mức nào cho cờ nào. Phải được
> NCC/khách xác nhận trước khi áp cho thiết bị thật. Ghi chú này được nhúng vào `alarmDetails`
> của từng rule để người xem alarm trên TB cũng thấy.

Cờ trong contract là `uint16` 0/1, nên điều kiện so sánh **NUMERIC** (`= 1` tạo, `= 0` xoá).
So sánh BOOLEAN sẽ không bao giờ khớp. Thiết bị mô phỏng chưa có quan hệ nhà/khu/trại nên
`propagate = false`.

Alarm chỉ sinh khi có **bản tin mới** đi qua rule engine sau khi ghi rule — phải giữ `feed` chạy.

## 12. Bốn thứ widget kiểu alarm bắt buộc phải có

Mất nhiều vòng mới ra, vì thiếu thứ nào cũng **không sinh lỗi**. Ghi lại thành bẫy #34 trong kit.

| Thứ | Thiếu thì sao |
|---|---|
| `config.alarmSource` | **Vỡ cả dashboard** khi mở (bẫy #33) |
| `alarmSource.dataKeys` kiểu `alarm` | Bảng trống, không báo lỗi |
| `useDashboardTimewindow` + `timewindow` riêng | Bảng trống, không báo lỗi |
| `sortOrder.key` là EntityKey chứ không phải chuỗi | Bảng trống, không báo lỗi |

Cái cuối là lỗi của chính dự án này, trong `subscribeForAlarms` của controller. Đo trực tiếp
trên websocket TB 4.3.1.2, cùng socket, cùng thiết bị, hai lệnh chỉ khác chỗ đó:

| `sortOrder.key` | Máy chủ trả lời |
|---|---|
| `"createdTime"` | **không trả lời gì**, không báo lỗi |
| `{type: "ALARM_FIELD", key: "createdTime"}` | `totalElements = 4` |

Cách chẩn đoán đã dùng: vá `WebSocket.prototype.send` trong trang để bắt lệnh gửi đi và gắn
listener đọc phản hồi. Không thấy `cmdId` của mình trong phản hồi nghĩa là máy chủ đã bỏ lệnh,
tức sai định dạng chứ không phải sai bộ lọc. Chi tiết trong bẫy #34.

## 13. Kết quả cuối (23/09/2026)

`verify_vent011_ui.py` báo **ĐẠT** toàn bộ. Bảng Cảnh báo hiện đủ 4 alarm của nhà FAULT; chẩn
đoán xác nhận `alarmDataCount = 4`, `alarmTotal = 4`, `canSubscribe = true` — tức là chính lời
gọi `subscribeForAlarms` của dự án này là đường đang dùng, nên lỗi `sortOrder.key` đúng là của ta.

Chẩn đoán vẫn để bật trên widget cảnh báo. Nó chỉ ghi hình dạng, không ghi giá trị, và là công cụ
sẽ cần lại khi đấu PLC thật.

## 14. Việc còn treo

- "Cảnh báo đang mở" ở màn Tổng quan vẫn để `--`. Đây là **chủ ý**: con số đó thuộc phạm vi alarm
  của nền tảng, không suy được từ danh sách nhà. Muốn hiện số thật thì phải cho widget Tổng quan
  một alarm subscription riêng — việc của đợt sau.
- Mức độ nghiêm trọng của 6 alarm rule vẫn là **đề xuất**, chưa được NCC/khách xác nhận.
- Thiết bị mô phỏng chưa có quan hệ nhà/khu/trại nên alarm không lan truyền lên cấp trên.
