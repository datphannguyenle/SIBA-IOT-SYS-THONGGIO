# VENT-014 — Đồng bộ source SIBA-OPS-DARK-1.1

## Status

`done`

## Objective

Đưa typography source dashboard thông gió về letter-spacing 0 theo hợp đồng nền tảng
`SIBA-OPS-DARK-1.1`, không deploy hoặc thay đổi runtime.

## Scope

- CSS modular và artifact build deterministic tương ứng.
- Regression toàn bộ test repo.

## Forbidden scope

- Không deploy ThingsBoard, sửa entity/profile/alarm hoặc kết nối PLC.
- Không đổi contract telemetry/nghiệp vụ thông gió.

## Inputs

- `/home/siba-iot-2/thingsboard-docker/tb-custom-ui/config/ui-standard.json`.
- Yêu cầu đồng bộ giao diện đa hệ ngày 02/10/2026.

## Expected outputs

- CSS dùng `letter-spacing: 0` cho eyebrow và liên kết Tổng quan.
- Artifact modular khớp builder; tối thiểu 183 test đạt.

## Model routing

| Work package | Model/effort | Owner | Reason |
|---|---|---|---|
| Sửa source, build, regression | Codex MAIN; runtime model ID không được giao diện công bố | `/root` | Thay đổi hẹp, không giao subagent |

## Dependencies

- Hợp đồng UI và registry ở repo nền tảng.

## Acceptance criteria

- [x] Hai khai báo letter-spacing thuộc shell modular bằng 0.
- [x] `build_vent_modular.py --check` đạt.
- [x] 183 test đạt.
- [x] Review và deploy sau cổng duyệt riêng của chương trình đa hệ; production version 13.

## Required evidence

- [x] File CSS và artifact build nằm trong diff Git.
- [x] Kết quả test được ghi trong handoff.
- [x] Finding được phân loại trong handoff.

## Gate

Giữ ở `review`; không deploy trước phê duyệt cutover dashboard thông gió.

## Ownership

### Mutable files

- `dashboard/modular.css`
- `dashboard/modular-ops.css`
- `deploy/thingsboard/build/modular/widget_*.json`

### Browser/runtime session

- Không sử dụng.

## Notes

- Thông gió vẫn `CHỜ PLC`; thay đổi này không chuyển trạng thái production.
