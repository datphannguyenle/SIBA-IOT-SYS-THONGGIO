# VENT-001 — Dashboard thông gió read-only baseline và design plan

## Status

`review`

## Objective

Xây dựng baseline có bằng chứng và kế hoạch thiết kế bốn state dashboard giám sát thông
gió V1 trước implementation.

## Scope

### Phase 0 — Repository baseline

- Ghi nhận cấu trúc repo, code/runtime artifact hiện có và khoảng trống.
- Inventory component có thể tái sử dụng.
- Trace kiến trúc hiện tại nếu repo có code.
- Ghi rõ runtime assumptions và phân loại mức chắc chắn.

### Phase 1 — Ventilation data contract

- Lập inventory semantic telemetry.
- Gắn raw source/document reference khi có; không bind UI trực tiếp raw PLC register.
- Ghi type, unit, source, freshness và missing-state behavior.
- Phân loại từng field `confirmed`, `derived` hoặc `uncertain`.
- Air speed, airflow và water consumption giữ `uncertain` cho tới khi PLC mapping được
  xác nhận.

### Phase 2 — Entity topology

- Kiểm chứng topology thực tế.
- Đánh giá `Farm -> Area -> Barn -> VentilationController` như một hypothesis.
- Nếu topology khác, report evidence; không ép dữ liệu theo assumption.

### Phase 3 — Design-system baseline

- Rà dashboard Khử mùi hiện tại khi source hoặc runtime artifact tồn tại.
- Inventory theme, header/footer, KPI, chart, alarm và responsive pattern có thể tái sử
  dụng.
- Phân biệt component tổng quát với widget nghiệp vụ `deo_*`.

### Phase 4 — Four-state design

- `default`: tổng quan trại và lưới nhà.
- `vent_detail`: giám sát chi tiết nhà, schematic và mode/status read-only.
- `vent_history`: trend và lịch sử.
- `vent_alarms`: cảnh báo read-only.
- Chuẩn bị design brief, responsive states và acceptance matrix.

## Forbidden scope

- Production code, dashboard, widget hoặc deploy script.
- ThingsBoard entity/profile/rule-chain mutation.
- RPC, PLC/device command, attribute/parameter write.
- Auto/Manual, fan, pump hoặc louver command.
- Alarm acknowledge, clear hoặc shelve.
- Bắt đầu implementation VENT-001 trong task baseline này.

## Inputs

- Tài liệu kỹ thuật bộ điều khiển thông gió.
- PLC/Gateway mapping khi được cung cấp.
- Source/runtime artifact dashboard Khử mùi khi tồn tại.
- Project context và orchestration rules trong `.codex/`.

## Expected outputs

- Repo and reusable-component inventory.
- Data contract draft với confirmed/derived/uncertain.
- Entity topology finding có evidence.
- Design-system baseline.
- Brief và plan cho bốn state, chưa có production implementation.
- Handoff theo template chuẩn.

## Model routing

| Work package | Model/effort | Owner | Reason |
|---|---|---|---|
| PDF extraction, inventories, evidence checklist | Luna low | Assigned at activation | Mechanical evidence gathering |
| Interpretation of ambiguous document/data fields | Luna medium | Assigned if needed | Bounded interpretation |
| Code tracing of existing builder/widgets | Terra medium | Assigned if code exists | Implementation-aware analysis |
| Architecture and design gate review | MAIN | MAIN | Final decisions and conflict resolution |

## Dependencies

- Access to relevant documents and repository artifacts.
- Read-only access to runtime evidence if repository evidence is insufficient.
- Confirmed PLC mapping for fields that must leave `uncertain`.

## Acceptance criteria

- [x] Repo baseline and reusable inventory have paths/evidence.
- [x] No V1 mutation path is proposed or implemented.
- [x] Semantic telemetry inventory distinguishes confirmed/derived/uncertain.
- [x] Missing, stale, offline, unknown and stopped states remain distinct.
- [x] Entity topology is evidenced instead of assumed.
- [x] Four state briefs cover desktop, tablet and mobile behavior.
- [x] Design reuses only components proven general-purpose.
- [x] MAIN review records unresolved conflicts and risks.
- [x] No production code or ThingsBoard state changed.

## Required evidence

- File paths and line/functions for repository findings.
- PDF page/section references for document findings.
- Runtime screenshot/API result only when read-only access is available and required.
- A confirmed/derived/uncertain label for every material claim.

## Gate

`APPROVED — DESIGN ONLY`

Implementation is forbidden before this gate. Passing it does not authorize production
deployment or any V2 write/control capability.

## Ownership

### Mutable files

Assigned when the task moves to `active`; one owner per file.

### Browser/runtime session

Assigned when needed; one owner per session.

## Runtime assumptions

- `uncertain`: no runtime or production topology is assumed until inspected.
- `confirmed`: V1 is read-only and PLC/Gateway is the equipment-state source of truth.
