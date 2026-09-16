# Entity topology baseline

## Observed topology

- **confirmed** — Target repo contains no ThingsBoard entity/profile/relation export.
- **confirmed external reference** — Existing SIBA platform documentation describes a
  shared `Farm -> Area -> Barn` tree and domain devices attached under it. This evidence
  is outside this repo: `/home/siba-iot-2/thingsboard-docker/docs/nen-tang/kien-truc.md`.
- **confirmed external reference** — Khử mùi uses Farm/all-device/selected-device aliases,
  including a `stateEntity` selected detail alias. This does not prove ventilation topology.

## Proposed topology

```text
Farm -> Area -> Barn -> VentilationController
```

Classification: **uncertain proposal**. Do not create entities or aliases from this diagram
until runtime/export evidence confirms ownership, relation direction/type and cardinality.

## Candidate aliases

| Alias purpose | Candidate resolution | Status |
|---|---|---|
| Current Farm | selected/fixed Farm constrained by tenant/customer | uncertain |
| Ventilation controllers in Farm | relation query or farm-scoped device query | uncertain |
| Selected Barn | state parameter | uncertain |
| Selected controller | state entity or Barn relation query | uncertain |
| Farm alarms | propagated alarms or scoped query | uncertain |

## Mapping assumptions to test

- One `VentilationController` per Barn.
- Controller device name/profile uniquely identifies the Barn.
- Farm/Area/Barn relations are accessible to the dashboard user.
- Alarm originators can be scoped to the selected Farm/Barn without tenant leakage.

All four are **uncertain**.

## Evidence needed

- Read-only entity export/API response showing entity types, IDs and relations.
- Device profile/type and sample controller identity.
- Confirmed relation names/directions and multi-farm/customer boundary.
- Alias resolution result for overview and selected Barn.
