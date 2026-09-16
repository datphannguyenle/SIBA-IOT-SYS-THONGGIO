# VENT-002 entity topology verification

## Result

`UNRESOLVED`

The proposed `Farm -> Area -> Barn -> VentilationController` topology is neither
confirmed nor rejected. The ThingsBoard host was reachable, but read-only entity and
dashboard endpoints returned HTTP 401 without an authenticated session.

## Verification matrix

| Entity | Type | Name pattern | Relation type/direction | Parent/child behavior | Ownership/isolation | Classification |
|---|---|---|---|---|---|---|
| Farm | unresolved | unresolved | unresolved | unresolved | customer/tenant boundary unresolved | uncertain |
| Area | unresolved | unresolved | unresolved | unresolved | customer/tenant boundary unresolved | uncertain |
| Barn | unresolved | unresolved | unresolved | unresolved | customer/tenant boundary unresolved | uncertain |
| VentilationController | unresolved | unresolved | unresolved | unresolved | controller cardinality per Barn unresolved | uncertain |

No entity IDs are recorded because no authenticated entity response was obtained. No IDs
may be hard-coded into a future design contract.

## Evidence

- **confirmed** — The live ThingsBoard service was network-reachable.
- **confirmed** — Unauthenticated `GET /api/tenant/devices?pageSize=1&page=0` and
  `GET /api/dashboards?pageSize=1&page=0` returned HTTP 401.
- **confirmed static evidence** — External
  `/home/siba-iot-2/thingsboard-docker/docs/he-thong/thong-gio.md` states that no
  ventilation config, builder, widget or runtime artifact had been found.
- **external/reference only** — The shared platform documentation describes a general
  Customer/Farm/Area/Barn tree. It does not establish a ventilation controller relation.

## Comparison with proposed topology

| Question | Result | Reason |
|---|---|---|
| Farm exists for ventilation scope | unresolved | no authenticated response |
| Area and Barn relations exist | unresolved | no relation query result |
| VentilationController exists | unresolved | no device/profile inventory |
| One controller per Barn | unresolved | no cardinality evidence |
| Multi-farm isolation is enforced | unresolved | no customer/tenant-scoped query |

## Blocker

Provide an approved authenticated read session and the official ventilation device/profile
scope. Then execute entity, relation, owner and customer queries using GET/read-only APIs.
