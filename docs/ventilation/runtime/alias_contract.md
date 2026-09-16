# VENT-002 alias contract verification

## Result

`UNRESOLVED — no ventilation dashboard or authenticated alias response`

No alias was created or updated. The entries below are verification requirements, not
approved production alias definitions.

| Purpose | Entity filter type | Root/source | Relation query/direction | Entity type | State parameter | Cardinality | Boundary | Runtime result | Classification |
|---|---|---|---|---|---|---|---|---|---|
| Current Farm | unresolved | current customer/dashboard context unresolved | unresolved | Farm candidate | none expected, unverified | exactly 1 required | customer + tenant | HTTP 401 prevented inspection | uncertain |
| Ventilation controller collection | unresolved | Current Farm candidate | relation or scoped device query unresolved | VentilationController candidate | none expected | 0..N, actual count unknown | must remain within current Farm/customer | no live alias/config found | uncertain |
| Selected Barn | unresolved | state/navigation candidate | unresolved | Barn candidate | name and wrapped entity shape unresolved | exactly 1 required | current Farm/customer | no ventilation dashboard state exists in source | uncertain |
| Selected controller | unresolved | selected Barn candidate | relation query unresolved | VentilationController candidate | selected entity parameter unresolved | exactly 1 required for detail | current Barn/Farm/customer | no live result | uncertain |
| Farm alarm scope | unresolved | Current Farm candidate | propagation/query unresolved | mixed originators possible | none expected | N alarms | current Farm/customer only | no ventilation alarm query | uncertain |
| Barn alarm scope | unresolved | Selected Barn candidate | propagation/query unresolved | Barn/controller originators unresolved | selected Barn candidate | N alarms | selected Barn only | no ventilation alarm query | uncertain |

## Evidence

- **confirmed static evidence** — No `vent_*` source, ventilation dashboard export or
  `ventilation.json` exists in the inspected workspace.
- **confirmed runtime boundary** — Dashboard/entity GET probes returned HTTP 401.
- **external/reference only** — The deodorization dashboard demonstrates Farm,
  all-device and selected-device alias patterns. Those filters and device types do not
  confirm ventilation aliases.

## Implementation constraint

Do not implement overview or detail datasources until each alias has an observed resolution
result, cardinality, relation direction and tenant/customer isolation test. A filter by
device type alone is not evidence of Farm isolation.
