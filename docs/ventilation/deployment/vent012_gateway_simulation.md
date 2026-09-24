# VENT-012 — Mô phỏng qua ThingsBoard IoT Gateway

## Trạng thái

Đã triển khai end-to-end lên runtime ngày 24/09/2026. Simulator và Gateway riêng đều healthy;
bốn controller ND2-1..4 đang gửi dữ liệu 3 giây/lần. Đây là **SIMULATION**, không xác nhận
mapping PLC production. Kiểm live và 183 test đã đạt. Sau các yêu cầu chỉnh layout của người
dùng, hai lượt soak cũ được dừng đúng quy trình ở 328 và 18 mẫu, lưu ngoài Git và không dùng
làm kết quả. Baseline giao diện cuối bắt đầu soak lại lúc 16:01:37 24/09/2026 (UTC+7), vì vậy
task vẫn `active`.

## Đường dữ liệu

`PLC Modbus TCP giả lập` → `tb-gateway-ventilation` → MQTT Gateway API → ThingsBoard →
semantic adapter → dashboard. Bốn unit ID 1..4 tương ứng ND2-1..4. Cổng 1502 chỉ nằm trên
Docker network `internal`; không publish lên host.

Simulator có 265 khóa contract: 41 giám sát và 224 cài đặt. Mỗi giá trị dùng FLOAT32 kèm cờ
validity; số 0 khác dữ liệu thiếu. Bảy block lặp sequence/timestamp để converter bỏ snapshot
bị xé giữa hai chu kỳ. Bảng này là **SIM ONLY**, không dùng commissioning PLC thật.

## Ranh giới an toàn

- Gateway dùng image digest cố định tương đương runtime khử mùi 3.8.0 nhưng là container riêng.
- Connector subclass chặn toàn bộ server-side RPC và attribute update. Việc `rpc: []` một mình
  không chặn reserved/connector RPC của Gateway 3.8.
- Modbus simulator chỉ nhận FC03; FC05/06/15/16 và mọi function khác bị từ chối.
- Root Rule Chain, gateway khử mùi, shared bundle, MUGE và dashboard DEMO không bị sửa.
- Alarm mặc định bị suppress tại nguồn. Chỉ đặt `allow_alarms: true` sau khi chạy lại audit
  notification và xác minh không có kênh ngoài ý muốn.

## Vận hành

Credential Gateway nằm ở `~/.config/siba-vent012-gateway-token`, mode 600, ngoài Git.

```bash
cd ~/SIBA-IOT-SYS-THONGGIO
python3 deploy/thingsboard/vent012_audit.py
python3 deploy/thingsboard/vent012_deploy.py plan
python3 deploy/thingsboard/vent012_deploy.py provision --confirm-create
export VENT_GATEWAY_TOKEN_FILE="$HOME/.config/siba-vent012-gateway-token"
docker compose -f gateway/ventilation/compose.yaml up -d
python3 deploy/thingsboard/deploy_vent012_widgets.py execute --confirm-deploy
python3 deploy/thingsboard/vent012_deploy.py dashboard --confirm-dashboard
python3 deploy/thingsboard/vent012_deploy.py verify
```

Kịch bản ở `gateway/ventilation/control/scenarios.json`. Mặc định NORMAL/BOUNDARY/MANUAL/FAULT,
alarm đều khóa. Đổi file chỉ là điều khiển simulator cục bộ; không có HTTP control API.

Theo dõi soak được ghi ngoài Git để tiến trình nền không làm bẩn worktree:

```bash
python3 deploy/thingsboard/vent012_soak.py status
# Chỉ sau khi completed=true:
python3 deploy/thingsboard/vent012_soak.py export
```

## Bằng chứng live ngày 24/09/2026

- 41/41 khóa giám sát và 224/224 khóa cài đặt có trên mỗi snapshot đầy đủ; zero và missing
  được phân biệt bằng validity map, không thay missing bằng 0.
- Kịch bản UNKNOWN, INVALID_ENUM, OFFLINE-controller và STALE đã chạy qua Modbus/Gateway.
  Tổng quan hiện `Chưa rõ` cho khóa thiếu/enum 99 và `Dữ liệu cũ` cho mất mẫu/stale; trạng thái
  `active=true` của nền tảng không bị dùng để đoán controller còn phát dữ liệu.
- Một chu kỳ FAULT có kiểm soát sinh 4 alarm `[SIM]` từ rule engine. Cùng bốn alarm ID xuất
  hiện ở controller, system, Barn, Area và Farm; sau khi tắt cờ tại nguồn, cả năm cấp về 0
  alarm SIM active. Không gọi API tạo/xóa/ack alarm.
- Dừng riêng `tb-gateway-ventilation` làm tuổi dữ liệu bốn nhà vượt 36 giây; start lại đưa cả
  bốn về dưới 1 giây. Container `tb-gateway` khử mùi giữ nguyên ID, image, startedAt và
  restartCount.
- Firefox live PASS ở 1366×768, 1536×734 và 390×844; 4 nhà, 5 màn, số alarm active thật,
  không tràn ngang, không control ghi và không còn `[object Object]`.
- Layout mới: Tổng quan/Lịch sử/Cảnh báo/Cài đặt lấp đầy viewport desktop; màn Giám sát dùng
  một cuộn trang dọc có giới hạn thay cho nhiều thanh cuộn lồng nhau. Header Giám sát gộp
  điều hướng thành một hàng, KPI lấp đầy ô và cột phải xếp Bộ điều khiển trên Dữ liệu bổ sung,
  loại bỏ các dải trống lớn. Hai bảng lịch sử được gộp thành một bảng có header sticky và cuộn
  nội bộ; summary alarm được gộp vào panel chính. Dashboard runtime đang ở version 8.

Evidence máy đọc nằm trong `docs/ventilation/deployment/evidence/vent012_*.json`. Chu kỳ soak
chỉ được đánh đạt khi file `vent012_soak_24h.json` đã được export với `completed=true` và
`summary.pass=true`.

## Rollback theo thứ tự ngược

1. Tắt compose VENT-012; không dừng `tb-gateway` khử mùi.
2. Khôi phục widget type/dashboard từ backup/manifest của lượt deploy nếu chúng thay đổi.
3. Chỉ sau review riêng mới xóa relation, controller, system, profile và Gateway có ID ghi trong
   `vent012_manifest.json`; tuyệt đối không xóa Barn/Area/Farm hoặc đối tượng không `created`.
4. Không tự xóa telemetry/alarm lịch sử; retention/xóa dữ liệu cần phê duyệt riêng.

## Khi chuyển sang PLC thật

Xác minh endpoint, unit ID, register, byte/word order, type, scale, enum, timestamp và feedback.
Viết connector/codec production mới; không tái sử dụng register SIM như mapping thật. Device
production dùng identity riêng, dashboard chỉ đổi datasource/key mapping sau commissioning.
