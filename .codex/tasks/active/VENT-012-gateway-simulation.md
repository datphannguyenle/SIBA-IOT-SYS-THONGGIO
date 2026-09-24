# VENT-012 — Mô phỏng end-to-end qua Gateway

## Status
active

Checkpoint 24/09/2026: runtime, alarm cycle, edge cases, Gateway reconnect, browser và 181
tests đã đạt. Layout desktop được cân lại theo yêu cầu: bốn state vừa viewport, Giám sát chỉ
còn một cuộn trang, không cuộn lồng. Soak 24 giờ mới chạy từ 15:35:00 UTC+7 bằng user service
`siba-vent012-soak`; không chuyển review trước khi có đủ
1440 mẫu sạch và export evidence.

## Objective
PLC giả lập Modbus → Gateway riêng → ThingsBoard → dashboard, ND2-1..4.

## Scope
Simulator, connector/converter chỉ đọc, entity/profile/relation SIM, alarm SIM lan cấp trại,
sửa UI hiện có, nghiệm thu dữ liệu/laptop và chạy 24 giờ. User approved implementation.

## Forbidden scope
Không PLC thật, RPC/ghi Modbus, Root chain, notification ngoài, shared bundle, khử mùi/MUGE,
xóa đối tượng cũ hoặc merge PR. Dừng trước phát alarm nếu phát hiện đường notification ngoài.

## Inputs
Contract v0.3; VENT-011; plan VENT-012 đã duyệt; Gateway khử mùi chỉ tham khảo kỹ thuật.

## Expected outputs
Manifest preflight/rollback, simulator/gateway cấu hình tái lập, UI tests, evidence deployment,
runbook/commissioning và báo cáo soak 24 giờ.

## Model routing
MAIN tích hợp/triển khai; requested Terra medium UI và audit đọc-only độc lập.

## Dependencies
Runtime Barn ownership, Gateway schema/RPC guard, audit notification; credentials ngoài Git.

## Acceptance criteria
- 41 khóa giám sát + 224 cài đặt, số 0/thiếu dữ liệu không lẫn.
- Bốn nhà tách dữ liệu; 5 màn, laptop/mobile; alarm propagation đúng và không đếm đôi.
- Restart/ngắt kết nối phục hồi; 24 giờ evidence, không tự đánh đạt sớm.
- Protected fingerprints không đổi; không lệnh ghi PLC.

## Required evidence
API/Modbus/subscription/browser đối chiếu; tests; screenshot; UTC timestamps; không secrets.

## Runtime evidence
- `docs/ventilation/deployment/evidence/vent012_alarm_cycle.json`
- `docs/ventilation/deployment/evidence/vent012_edge_cases_active.json`
- `docs/ventilation/deployment/evidence/vent012_gateway_reconnect.json`
- `docs/ventilation/deployment/evidence/vent012_ui_verify.json`
- external soak state: `~/.config/siba-vent012-soak.json`

## Gate
Đạt mô phỏng end-to-end qua Gateway; không cấp quyền commissioning production.

## Ownership
MAIN: deployment/runtime; UI agent: ventilation-source.js/modular.js/test_vent012_ui.py;
audit agent: vent012_audit.py/vent012_preflight.json; file khác MAIN.
