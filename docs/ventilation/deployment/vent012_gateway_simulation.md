# VENT-012 — Mô phỏng qua ThingsBoard IoT Gateway

## Trạng thái

Đã triển khai source và test local; phần runtime được thực hiện theo manifest riêng. Đây là
SIMULATION, không xác nhận mapping PLC production. Cổng đạt của task gồm kiểm live và soak 24 giờ.

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
python3 deploy/thingsboard/deploy_vent_modular.py execute --confirm-deploy
python3 deploy/thingsboard/vent012_deploy.py dashboard --confirm-dashboard
python3 deploy/thingsboard/vent012_deploy.py verify
```

Kịch bản ở `gateway/ventilation/control/scenarios.json`. Mặc định NORMAL/BOUNDARY/MANUAL/FAULT,
alarm đều khóa. Đổi file chỉ là điều khiển simulator cục bộ; không có HTTP control API.

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
