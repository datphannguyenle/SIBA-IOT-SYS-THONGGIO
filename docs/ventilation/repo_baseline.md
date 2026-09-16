# VENT-001 — Repository baseline

## Phạm vi khảo sát

Khảo sát read-only repository `datphannguyenle/SIBA-IOT-SYS-THONGGIO` tại thời điểm
VENT-001 được activate. Source Khử mùi trong workspace ThingsBoard kế bên được dùng làm
tham chiếu ngoài repo; nó không tự động trở thành source of truth của repo này.

## What exists

- **confirmed** — Repository chỉ có policy/orchestration, template, lifecycle task và hồ
  sơ VENT-001. Evidence: `AGENTS.md`, `.codex/project_context.md`,
  `.codex/orchestration.md`, `.codex/model_routing.md`, `.codex/tasks/active/`.
- **confirmed** — V1 được giới hạn read-only; PLC/Gateway là nguồn trạng thái thiết bị.
  Evidence: `AGENTS.md` mục “Ranh giới an toàn V1” và `.codex/project_context.md`.
- **confirmed** — Tài liệu kỹ thuật 65 trang mô tả chức năng thiết bị, I/O và HMI.
  Evidence: *TÀI LIỆU KỸ THUẬT THIẾT BỊ ĐIỀU KHIỂN THÔNG GIÓ*, pp. 6–65.

## What does not exist

- **confirmed** — Không có JavaScript/TypeScript/Python/HTML/CSS production, ThingsBoard
  dashboard export, widget source, builder, deploy script hoặc runtime dump trong repo.
- **confirmed** — Không có PLC/Gateway raw-tag mapping, address map, scale, sampling
  cadence, heartbeat hoặc stale threshold.
- **confirmed** — Không có entity/profile/relation export để xác nhận topology runtime.

Evidence: inventory toàn bộ non-`.git` tree không tìm thấy `*.js`, `*.ts`, `*.py`,
`*.html`, `*.css`, `*.json` production, `*.yaml` hoặc `*.yml` trước khi tạo output của
VENT-001.

## External reference available

- **confirmed** — Workspace `/home/siba-iot-2/thingsboard-docker` có source và runtime
  evidence dashboard Khử mùi: `tb-custom-ui/deploy/build_dashboard_deo.py`,
  `tb-custom-ui/dashboard-theme.css`, `tb-custom-ui/widgets/` và
  `docs/he-thong/khu-mui/ui-polish-production-2026-09-14/`.
- **derived** — Các artifact này phù hợp để rút pattern shell, state/alias và responsive,
  nhưng không chứng minh data model hoặc nghiệp vụ thông gió.

## What is reusable

- **confirmed reference / proposed reuse** — theme shell, `header_bar`, `footer_bar`,
  `kpi_stat_card`, system chart và alarm pattern có bằng chứng ngoài repo. Chi tiết tại
  `docs/ventilation/reusable_components.md`.
- **not reusable as general components** — `deo_*`, `chem_station`, topology hóa chất,
  parameter/audit behavior và telemetry keys của Khử mùi.

Không có claim phần trăm tái sử dụng vì chưa có ventilation implementation để đo.

## What remains uncertain

- Topology và số lượng `VentilationController` thực tế.
- Semantic-to-raw mapping, datatype, scale, range, precision và freshness.
- Nguồn thật của fan/pump state là feedback hay relay-command state.
- Air speed/airflow/water values là đo trực tiếp, tính toán hay tổng tích lũy.
- Khả năng dùng trực tiếp external shared components sau khi code được đưa vào repo này.

## Terra routing decision

Target repo không có code để trace, nên không giao Terra cho target implementation.
Terra/medium chỉ trace read-only source Khử mùi bên ngoài để lập design-system baseline.
