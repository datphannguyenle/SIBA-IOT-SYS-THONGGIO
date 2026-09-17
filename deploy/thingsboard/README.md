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
