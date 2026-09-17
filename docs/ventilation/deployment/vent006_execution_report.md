# VENT-006 — Execution report

## Kết quả

`review — DEMO DEPLOYED`. Đúng hai lệnh tạo được gửi, cả hai trả 200 và qua xác minh đọc lại.

| Mục | Giá trị |
|---|---|
| Duyệt | ChatGPT Web `APPROVED — CONTROLLED THINGSBOARD DEMO DEPLOYMENT` (17/09/2026) |
| Commit tooling/payload | `7cb9621b47b31601496cbada644257c2d56ce2c3` (nhánh `feat/VENT-006-tb-demo-deploy`) |
| Thời điểm | 2026-09-17T14:38:08+07:00 |
| Người chạy lệnh ghi | Người dùng chạy `deploy_vent_demo.py execute --confirm-create` trên máy này (quyền tự động của agent bị chặn cho lệnh deploy) |
| ThingsBoard | `100.86.144.207:8080`, 4.3.1.2 CE, tenant `0abe2520-9528-11f1-af48-7566a705eb32` |

## Lệnh ghi đã thực hiện

| # | Lệnh | HTTP | Object |
|---|---|---|---|
| 1 | `POST /api/widgetType` (không id, không `updateExistingByFqn`) | 200 | widget type `b9fa9280-b26a-11f1-83ad-9912edc644d2`, fqn `siba_vent_demo.vent_demo_view` |
| 2 | `POST /api/dashboard` (không id) | 200 | dashboard `b9ff4d70-b26a-11f1-83ad-9912edc644d2`, `DB-30-VEN-DETAIL-V1-DEMO`, version 1 |

Nhật ký rào chắn (`guard_mutation_log`) chỉ có hai lệnh trên. Không bundle, entity, profile,
relation, rule chain, alarm, customer, telemetry, attribute hay RPC.

## Preflight ngay trước khi ghi (evidence/vent006_baseline_pre_mutation.json)

- Tra cứu `tenant.siba_custom_ui.header_bar` = 200 (hiệu chuẩn); `tenant.siba_vent_demo.vent_demo_view` = 404.
- Không dashboard trùng tiêu đề; không dashboard nào tham chiếu `tenant.siba_vent_demo.*`.
- Mốc bảo vệ khớp kế hoạch: Khử mùi v27 `99c899a8…`, SIMULATION v9 `faccbe91…`,
  MUGE v107 `ed99833e…`, bundle `siba_custom_ui` 15 widget `af87a8ba…`.

## Xác minh đọc lại

- Widget type: fqn, `type=static`, tenant đúng, `controllerScript` và `templateCss` giống hệt payload,
  tra theo fqn đầy đủ trả đúng ID.
- Dashboard: tiêu đề đúng; đúng 4 state, root `default`; mọi widget `tenant.siba_vent_demo.vent_demo_view`;
  không alias, không datasource, không customer; cấu hình đọc lại giống hệt payload.

Chi tiết UI: [vent006_verification.md](vent006_verification.md). Rollback: [vent006_rollback.md](vent006_rollback.md).

---

## Refinement 1 — CONTROLLED VISUAL REFINEMENT UPDATE

Bản ghi tạo ở trên giữ nguyên. Refinement được ghi vào `vent006_manifest.json` dưới khóa
`refinements` (không đổi `created`, không đổi timestamp tạo).

- Duyệt: `APPROVED — VENT-006 CONTROLLED VISUAL REFINEMENT UPDATE`.
- Lệnh: `deploy_vent_demo.py refine --confirm-update` — rào chắn chỉ cho POST có `id` đúng manifest;
  dashboard chỉ được cập nhật khi cấu hình live khác build (hiện không khác → không gửi).
- Kết quả thực thi: xem mục bổ sung sau khi chạy.
