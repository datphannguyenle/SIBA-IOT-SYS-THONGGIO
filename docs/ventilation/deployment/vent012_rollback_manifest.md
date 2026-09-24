# VENT-012 rollback manifest

Nguồn ID thực tế: `deploy/thingsboard/vent012_manifest.json` sau provision. Không chạy rollback
từ tên hoặc wildcard. Thứ tự dự kiến: stop containers → restore dashboard/widgets → relations
`VentilationSystemToController` → `BarnToVentilationSystem` → controllers → systems → gateway →
profiles. Mọi DELETE cần script guarded và phê duyệt riêng; VENT-012 hiện không cung cấp lệnh xóa.

Không bao giờ xóa: Barn ND2-1..4, Area, Farm, Customer, `tb-gateway` khử mùi, dashboard DEMO,
7 thiết bị VENT-011, shared bundle, lịch sử hoặc alarm.
