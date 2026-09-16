# VENT-002 connectivity and freshness contract

## Result

`UNRESOLVED — candidate semantics only`

No ventilation device, connectivity attribute or telemetry timestamp was readable. The
following is a safe decision framework for later verification, not an implementation-ready
binding.

| State | Evidence required | Current result | Classification |
|---|---|---|---|
| `ONLINE` | confirmed controller entity plus authoritative active/connect event or Gateway connection signal | no ventilation signal observed | uncertain |
| `OFFLINE` | authoritative inactive/disconnect signal under a confirmed platform contract | no ventilation signal observed | uncertain |
| `STALE` | latest telemetry timestamp older than a threshold derived from evidenced sampling/transport cadence | no cadence or threshold observed | uncertain |
| `UNKNOWN` | missing/unmapped/invalid connectivity evidence or inability to resolve controller | evidence framework is valid; runtime cause unresolved | derived handling rule |

## Candidate ThingsBoard signals to verify

- Device `active` state.
- `lastActivityTime`, `lastConnectTime` and `lastDisconnectTime`.
- Connectivity lifecycle events or inactivity alarm.
- Gateway connection state for the specific ventilation device.
- Latest telemetry timestamp by semantic group.
- A documented device attribute only if it is the approved platform contract.

These are generic platform candidates. Existing feeding/deodorization behavior is
external/reference evidence and cannot set ventilation timeouts.

## Precedence proposal pending evidence

1. If no controller or authoritative connectivity source resolves: `UNKNOWN`.
2. If an authoritative connectivity source explicitly reports disconnected/inactive:
   `OFFLINE`.
3. If connectivity is online but a telemetry group exceeds its confirmed threshold:
   connectivity remains `ONLINE` while that group is `STALE`.
4. Otherwise the controller may be `ONLINE` and the group current.

This proposal preserves the required distinctions but must not be coded until the actual
signals and thresholds are verified.

## Stale thresholds

| Telemetry group | Sampling cadence | Observed update interval | Recommended `stale_after_sec` | Result |
|---|---|---|---|---|
| Environment | unknown | unavailable | null | blocker |
| Equipment feedback | unknown | unavailable | null | blocker |
| Controller mode/stage | unknown | unavailable | null | blocker |
| Louver position | unknown | unavailable | null | blocker |
| Conditional measurements | unknown | unavailable | null | blocker |

Hard rules remain: `STALE != OFFLINE`, `UNKNOWN != OFFLINE`, `UNKNOWN != STOPPED`, and
missing telemetry does not establish `OFFLINE`.
