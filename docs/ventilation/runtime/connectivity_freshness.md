# VENT-002 connectivity and freshness contract

## Result

`UNRESOLVED FOR VENTILATION`

Authenticated runtime inventory found no ventilation controller entity. Generic
ThingsBoard device activity semantics cannot be assigned to a non-existent controller,
and no sampling cadence exists from which to derive stale thresholds.

| State | Evidence required | Runtime result | Classification |
|---|---|---|---|
| `ONLINE` | declared controller plus authoritative active/connect or Gateway signal | no controller/signal | uncertain |
| `OFFLINE` | authoritative inactive/disconnect signal under confirmed contract | no controller/signal | uncertain |
| `STALE` | telemetry age beyond evidence-backed cadence threshold | no samples/cadence | uncertain |
| `UNKNOWN` | controller or signal cannot be resolved | safe current handling for absent binding | derived |

## Candidate platform signals for a future controller

- Device `active`, `lastActivityTime`, `lastConnectTime`, `lastDisconnectTime`.
- Connectivity lifecycle/inactivity events.
- Gateway connection state assigned to the ventilation device.
- Latest timestamp per semantic telemetry group.

These are platform candidates only. Existing feeding/deodorization timeout behavior is
not ventilation evidence.

## Safe precedence pending a real contract

1. Unresolved controller or authoritative signal → `UNKNOWN`.
2. Explicit authoritative disconnect/inactive evidence → `OFFLINE`.
3. Connected controller plus telemetry older than a confirmed threshold → controller
   `ONLINE`, affected telemetry group `STALE`.
4. Otherwise a confirmed connected/current signal may be `ONLINE`/current.

| Group | Observed cadence | `stale_after_sec` | Result |
|---|---|---|---|
| Environment | unavailable | null | blocker |
| Equipment feedback | unavailable | null | blocker |
| Mode/stage | unavailable | null | blocker |
| Louver position | unavailable | null | blocker |
| Conditional measurements | unavailable | null | blocker |

`STALE != OFFLINE`, `UNKNOWN != OFFLINE`, `UNKNOWN != STOPPED`, and missing telemetry
does not establish `OFFLINE`.
