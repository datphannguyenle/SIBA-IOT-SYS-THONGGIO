# Handoff — VENT-014

## STATUS

`done`; source đã review, tích hợp vào builder contract nền tảng và deploy production.

## MODELS USED

Codex MAIN của phiên nền tảng; runtime không công bố model ID. Không dùng subagent.

## FINDINGS

- `confirmed`: hai selector shell còn letter-spacing `.55px` và `.06em`, trái hợp đồng 1.1.
- `confirmed`: thay đổi CSS làm artifact deterministic cũ lệch, cần build lại.
- `confirmed`: thông gió vẫn thiếu PLC thật nên trạng thái nền tảng là `CHỜ PLC`.
- `confirmed`: production version 13 dùng `siba_thong_gio_ops`; source/live read-back đạt.

## EVIDENCE

- `dashboard/modular.css`: `.vm-eyebrow`.
- `dashboard/modular-ops.css`: `.siba-home`.
- `deploy/thingsboard/build/modular/widget_*.json`: artifact sinh lại từ builder.

## CHANGES

- Đặt letter-spacing của eyebrow và liên kết Tổng quan về 0.
- Sinh lại năm widget JSON modular; không đổi contract/datasource.
- Builder nền tảng stage/cutover năm widget theo `selectedFarm` và giữ dashboard cùng ID.

## TESTS

- `python3 deploy/thingsboard/build_vent_modular.py --check`: PASS.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 183 test, PASS.
- Nền tảng: 80 test, entity audit 67/67, browser sáu dashboard × năm viewport, PASS.

## UNCERTAIN

- Chưa có PLC thật/profile/device `VentController`; commissioning vẫn pending.

## RISKS

- Năm widget type cũ phải giữ tối thiểu đến 17/10; xóa cần duyệt riêng.

## NEXT RECOMMENDED ACTION

Khi có PLC thật, provisioning qua contract, relation/read-back và `commissioned=true`;
chỉ sau telemetry thật đạt mới đổi trạng thái sang `PRODUCTION`.
