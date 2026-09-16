# VENT-002 entity topology verification

## Result

`PARTIALLY CONFIRMED`

Authenticated tenant inventory confirms the shared `Farm -> Area -> Barn` hierarchy.
The proposed final edge to `VentilationController` is not deployed: no matching device,
device type or device profile exists.

## Live inventory

| Entity | Count | Entity type | Relation from parent | Direction | Ownership | Classification |
|---|---:|---|---|---|---|---|
| Farm | 1 | ASSET / `Farm` | root for inspected hierarchy | from Farm to children | one tenant, one assigned customer | confirmed |
| Area | 3 | ASSET / `Area` | `FarmToArea` | Farm → Area | same tenant/customer scope | confirmed |
| Barn | 67 | ASSET / `Barn` | `AreaToBarn` | Area → Barn | same tenant/customer scope | confirmed |
| VentilationController | 0 | no device type/profile found | none | none | no ownership record exists | confirmed absence in current tenant |

All 1 Farm, 3 Areas and 67 Barns are assigned rather than customer-unassigned. Only one
Farm/customer scope exists, so isolation across multiple farms/customers remains
unverified.

## Relation evidence

- `FarmToArea`: 3 outgoing relations from the Farm to Area assets.
- `AreaToBarn`: 67 outgoing relations from Areas to Barn assets.
- Barn device children are limited to existing domains: 66 Deodorizers, 88 Gateways,
  66 Silos and 1 `default` device relation.
- No Barn relation targets a `VentilationController` or ventilation-declared device.

## Comparison with proposed topology

```text
Farm -> Area -> Barn -> VentilationController
```

| Segment | Result |
|---|---|
| Farm → Area | confirmed |
| Area → Barn | confirmed |
| Barn → VentilationController | rejected as a currently deployed relation |
| One controller per Barn | not satisfied: 0 declared controllers across 67 Barns |
| Tenant/customer ownership | confirmed for existing Farm/Area/Barn assets |
| Multi-farm isolation | unresolved because only one live Farm/customer scope exists |

## Runtime evidence

- Authenticated `GET /api/tenant/assets` paginated across 8,412 assets.
- Authenticated `GET /api/tenant/devices` paginated across 8,186 devices.
- Authenticated `GET /api/deviceProfiles` returned 11 profiles, none ventilation-scoped.
- Authenticated `GET /api/relations/info` was executed for the Farm, 3 Areas and 67 Barns.

No entity ID is hard-coded into the design contract.

## Blocker

An approved provisioning task must define/create the ventilation controller entity/profile
and Barn relation before aliases, telemetry or dashboard implementation can be verified.
VENT-002 does not authorize that mutation.
