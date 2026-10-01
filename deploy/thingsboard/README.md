# VENT-006 · ThingsBoard demo deployment (thông gió)

Triển khai **cô lập** demo đã duyệt (VENT-003) lên tenant: 1 widget type static
`tenant.siba_vent_demo.vent_demo_view` + 1 dashboard `DB-30-VEN-DETAIL-V1-DEMO`.
Không bundle, không entity, không alias, không telemetry/attribute/RPC.

```bash
cd deploy/thingsboard
python3 build_vent_demo.py            # dựng build/*.json từ nguồn repo (xác định)
python3 build_vent_demo.py --check    # build có khớp nguồn không
python3 deploy_vent_demo.py preflight # chỉ GET
python3 deploy_vent_demo.py execute --confirm-create   # CHỈ khi đã được duyệt
python3 verify_vent_demo_ui.py        # Firefox headless, 4 state × 1920/390
python3 deploy_vent_demo.py regression
python3 rollback_vent_demo.py [--confirm-delete]
```

Mật khẩu: `TB_PASSWORD` hoặc file `~/.config/siba-tb-pass` (quyền 600). Không lưu token.
KHÔNG dùng `thingsboard-docker/tb-custom-ui/deploy/deploy_widgets.py` (ghi đè bundle `siba_custom_ui`).


## Hưu trí dashboard DEMO và SIM (01/10/2026)

Chỉ còn một dashboard chuẩn `DB-30-VEN-DETAIL-V1-GATEWAY-SIM` (`0e30c5f0-b7bf-11f1-a719-7da6129c6745`). `DB-30-VEN-DETAIL-V1-DEMO`
(`b9ff4d70-…`) và `DB-30-VEN-DETAIL-V1-SIM` (`32b1ecb0-…`) đã xóa trên ThingsBoard (bản sao lưu đầy đủ ở `~/siba-data/vent013-backup/`).
Các script cũ nhắm vào hai ID đó (`deploy_vent_modular.py`, `update_vent_demo.py`, `verify_vent008_ui.py`, `vent011_deploy.py` ở phần dashboard)
sẽ lỗi 404 nếu chạy lại; giữ để tra cứu lịch sử, đừng chạy. Báo cáo và bằng chứng VENT-006..011 vẫn nhắc ID cũ như một phần lịch sử.
Thiết bị `SIM-VEN-*` và 6 alarm rule trên device profile không đổi. Khi chạy PLC thật: cấu hình lại thiết bị và đổi alias/nhãn nguồn của dashboard chuẩn.
