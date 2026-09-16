# V1 read-only safety audit

## Hard requirement

> V1 SHALL contain no RPC invocation, attribute write, alarm acknowledgement,
> parameter write, or UI event capable of changing PLC/ThingsBoard device state.

## Audit result

`PASS — DESIGN PACKAGE ONLY`

| Prohibited path | Result | Evidence |
|---|---|---|
| RPC invocation | absent | no source code; state/widget specs explicitly prohibit RPC |
| PLC/device command | absent | `vent_detail.md` is feedback/display only |
| Attribute write | absent | contract is static design metadata only |
| Parameter write | absent | no settings/parameter state or widget |
| Auto/Manual command | absent | mode is display-only |
| Fan/pump/louver command | absent | schematic accepts feedback only |
| Alarm acknowledge | absent | `vent_alarms.md` prohibits it |
| Alarm clear/shelve | absent | `vent_alarms.md` prohibits both |
| Other device-state mutation | absent | no production JS/Python/ThingsBoard artifact added |

## Semantic safeguards

- `null != 0`; missing displays `--`.
- `STALE != OFFLINE`.
- `UNKNOWN != STOPPED`.
- Last command is not actual feedback.
- 6/9 level behavior is a document capability, not a hard-coded runtime fact.
- Conditional metrics remain omitted until mapping is confirmed.

## Keyword review rule

Terms such as RPC, write, command, acknowledge, clear and shelve appear only in policy,
prohibition, evidence-gap or safety-audit prose. Their presence is not an implementation
path. Any future executable occurrence is a BLOCKER requiring separate authorization.

## Remaining blockers

- No confirmed semantic/raw mapping.
- No confirmed topology/alias scope.
- No confirmed feedback and freshness contract.
- No reviewer-issued `APPROVED — DESIGN ONLY`.
