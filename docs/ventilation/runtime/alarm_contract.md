# VENT-002 alarm contract verification

## Result

`UNRESOLVED FOR VENTILATION`

No authenticated ventilation alarm query was possible. No alarm was created,
acknowledged, cleared, shelved or updated.

| Contract item | Runtime result | Classification | Blocker |
|---|---|---|---|
| Originator | unknown | uncertain | controller/Barn entity scope unavailable |
| Alarm type | unknown | uncertain | no ventilation alarm response/profile |
| Severity values | unknown | uncertain | no ventilation alarm response/profile |
| Active semantics | generic ThingsBoard behavior exists externally; ventilation use unknown | external/reference | query/profile evidence required |
| Cleared semantics | generic ThingsBoard behavior exists externally; ventilation use unknown | external/reference | query/profile evidence required |
| Propagation | unknown | uncertain | relation and alarm-rule configuration unavailable |
| Farm scoping | unknown | uncertain | alias/relation/customer evidence unavailable |
| Barn scoping | unknown | uncertain | selected Barn/controller scope unavailable |
| Controller scoping | unknown | uncertain | controller entity unavailable |
| Retention | unknown | uncertain | server/runtime policy unavailable |
| History availability | unknown | uncertain | no successful alarm/history GET |
| Export capability | unknown | uncertain | deployed widget/edition/permission not inspected |

## Read-only query shape to verify later

An approved authenticated session must first resolve the ventilation originator and
relation scope, then use documented GET alarm list/history endpoints with valid OpenAPI
query parameters. The project evidence warns that ThingsBoard may ignore unknown query
parameters, so result scoping must be independently checked.

## External/reference evidence

- The deployed deodorization dashboard uses a read-only system alarm table.
- The technical PDF describes current alarms, date-filtered alarm history and HMI export.

Neither proves ventilation alarm originators, types, propagation, retention or
ThingsBoard export support.

## V1 safety boundary

The V1 alarm surface may provide filtering, sorting, paging, time-window selection and
row inspection only. Acknowledge, clear, shelve, assign, create and update operations
remain prohibited.
