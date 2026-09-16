# VENT-002 alias contract verification

## Result

`CONFIRMED ABSENT FOR VENTILATION`

All nine live dashboards and their configuration were read through authenticated GETs.
None is a ventilation dashboard and none contains a `vent_*` state or ventilation alias.
No alias was created or updated.

| Purpose | Entity filter / root source | Relation / direction | Entity type / state parameter | Cardinality | Customer/tenant boundary | Runtime result | Classification |
|---|---|---|---|---|---|---|---|
| Current Farm | fixed/current entity; root is dashboard/user scope | none expected | ASSET `Farm`; no parameter expected | exactly 1 | current user customer + tenant | no ventilation alias exists; one assigned Farm is live | confirmed absent alias |
| Controller collection | relations query rooted at Current Farm/Barns | future Barn → controller relation; exact type absent | DEVICE `VentilationController`; no parameter expected | 0..N required; current declared count 0 | must remain inside current Farm/customer | no controller type, relation or alias | confirmed absent |
| Selected Barn | state entity filter rooted in controller/Barn navigation | hierarchy context Farm → Area → Barn | ASSET `Barn`; wrapped state parameter name unresolved | exactly 1 | current Farm/customer only | no `vent_*` state or parameter | confirmed absent |
| Selected controller | state entity or relations query rooted at Selected Barn | future Barn → controller relation | DEVICE `VentilationController`; wrapped selected-entity parameter unresolved | exactly 1 | selected Barn/Farm/customer | no controller entity or alias | confirmed absent |
| Farm alarm scope | entity/alarm source rooted at Current Farm | propagation or scoped query unresolved | Farm/controller originators unresolved; no state parameter | 0..N alarms | current Farm/customer only | no ventilation alarm alias/widget | confirmed absent |
| Barn alarm scope | entity/alarm source rooted at Selected Barn/controller | propagation/query direction unresolved | Barn/controller originators unresolved; selected Barn parameter required | 0..N alarms | selected Barn only | no ventilation alarm alias/widget | confirmed absent |

## Dashboard evidence

The nine dashboards are system statistics, Thermostats, Firmware, Software, crusher,
deodorization production/simulation, MUGE and irrigation. Existing Farm/selected-device
aliases belong to other domains and are reference patterns only.

## Implementation impact

Alias resolution cannot be implemented safely because its controller root and final
relation do not exist. A later approved provisioning/configuration task must establish the
entity/profile/relation contract before aliases are created. Device-type-only filtering is
not sufficient evidence of Farm isolation.
