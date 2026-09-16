# AGENTS.md — SIBA IOT SYS · Thông gió

## Mục tiêu và ranh giới

Repository này dùng GitHub làm shared state và source of truth cho hệ thống giám sát
thông gió SIBA trên ThingsBoard. ChatGPT Web giữ vai trò architect/planner/reviewer;
Codex là executor/tester/repo-native engineering agent.

V1 chỉ đọc dữ liệu từ PLC/Gateway. Không triển khai dashboard production trước gate
`APPROVED — DESIGN ONLY` và phê duyệt triển khai riêng.

## Vai trò

### MAIN

MAIN sở hữu kiến trúc, phân rã task, quyết định tích hợp, giải quyết xung đột, review
cuối và các approval gate. MAIN phải review các kết luận quan trọng trước khi integrate.
Route ưu tiên là GPT-6 Astra (`gpt-6-astra`) với reasoning effort `ultra`, gồm cả
difficult cross-task reasoning. Không dùng MAIN cho mechanical search/extraction khi có
thể delegate.

### Luna low/medium

Dùng cho trích xuất PDF/tài liệu, tìm kiếm repo hẹp, inventory, kiểm checklist, thu thập
bằng chứng và trích xuất dữ liệu có cấu trúc. Dùng low cho thao tác cơ học; medium khi cần
diễn giải có giới hạn. Không dùng Luna để quyết định kiến trúc cuối hoặc debug khó xuyên
nhiều hệ thống. Route ưu tiên là `gpt-5.6-luna`: effort `low`, tăng lên `medium` khi
bounded interpretation cần thêm reasoning.

### Terra medium

Dùng cho code tracing, phân tích implementation, builder/widget và debug runtime thông
thường. Route ưu tiên là `gpt-5.6-terra` với effort `medium`.

### Terra high

Chỉ dùng khi cần cho bug state khó, DOM/browser, race condition, debug xuyên hệ thống
hoặc review implementation phức tạp. Việc tăng effort phải có lý do và được ghi trong
handoff.

Exact model availability phải được kiểm tại runtime. Nếu route ưu tiên không khả dụng,
MAIN chọn model gần nhất theo role/capability, giữ nguyên role boundary và ghi model thay
thế cùng lý do dưới `MODELS USED`. Model rẻ hơn không được âm thầm nhận approval authority
của MAIN.

## Quy tắc orchestration

- Task độc lập có thể chạy song song khi handoff cost hợp lý.
- Một mutable file chỉ có một owner tại một thời điểm.
- Một mutable browser/runtime session chỉ có một owner tại một thời điểm.
- Không để hai agent đồng thời sửa cùng file hoặc thao tác cùng browser session.
- Mechanical evidence gathering nên giao cho model nhỏ hơn khi phù hợp.
- MAIN giữ objective, acceptance criteria, kiến trúc, integration và final review.
- Mọi thay đổi phải đi qua lifecycle `backlog -> active -> review -> done`.
- Không chuyển task sang `done` khi gate hoặc acceptance criteria chưa đạt.

## Evidence và mức độ chắc chắn

Mọi claim quan trọng phải có evidence khi có thể: file path, line/function, runtime
screenshot/API result hoặc document reference. Finding phải được phân loại:

- `confirmed`: có bằng chứng trực tiếp.
- `derived`: suy ra từ nhiều bằng chứng; phải nêu cách suy ra.
- `uncertain`: chưa đủ bằng chứng; không được dùng như fact.

Không biến assumption thành fact. Evidence không chứa credential, token hoặc dữ liệu
nhạy cảm.

## Ranh giới an toàn V1

V1 SHALL contain no:

- RPC invocation hoặc PLC/device command;
- attribute write hoặc parameter write;
- Auto/Manual, fan, pump hoặc louver command;
- alarm acknowledge, clear hoặc shelve;
- mutation nào thay đổi trạng thái ThingsBoard device.

PLC/Gateway là source of truth của trạng thái thiết bị. UI không được suy luận trạng thái
quạt, bơm hoặc cửa chớp từ command gần nhất.

## Quy tắc dữ liệu V1

- UI chỉ dùng semantic telemetry key; không bind trực tiếp raw PLC register.
- `null` hoặc missing hiển thị `--`; không ép thành `0`.
- `STALE != OFFLINE` và `UNKNOWN != STOPPED`.
- Số cấp 6/9 phải đọc từ telemetry, attribute hoặc config đã confirmed.
- Không hard-code assumption.
- Air speed, airflow và water consumption chỉ được dùng khi PLC mapping đã confirmed.

## Task và handoff

Mỗi task phải có Objective, Scope, Forbidden scope, Inputs, Expected outputs, Model
routing, Dependencies, Acceptance criteria, Required evidence và Gate. Dùng template
trong `.codex/templates/` và lưu đúng thư mục lifecycle.

Handoff phải có đúng các mục:

`STATUS`, `MODELS USED`, `FINDINGS`, `EVIDENCE`, `CHANGES`, `TESTS`, `UNCERTAIN`,
`RISKS`, `NEXT RECOMMENDED ACTION`.

## Cấm trong bootstrap

Không tự tạo dashboard/widget production, ThingsBoard entity, deploy script production,
RPC code hoặc bắt đầu implementation của VENT-001 trong task bootstrap orchestration.
