# VENT-005 relation manifest

## Existing relations to preserve

| From | Relation | To | Action |
|---|---|---|---|
| `abc-dong-anh/Khu B` | `AreaToBarn` | `abc-dong-anh/ND2-1` | `NO-OP` |
| `abc-dong-anh/ND2-1` | `BarnToGateway` | `abc-dong-anh/ND2-1/GW-01` | `NO-OP` |
| Pilot Barn | existing room/silo/deodorizer relations | existing children | `NO-OP` |
| Pilot Gateway | existing `GatewayToFeeder` relations | existing feeder devices | `NO-OP` |

No legacy relation is renamed, removed or replaced.

## Proposed new relations

| Order | From | Type | To | Action | Blocker |
|---:|---|---|---|---|---|
| 1 | Barn ID `e8a84a30-9c3c-11f1-a0fc-e93bd628a87f` | `Contains` | new System Asset ID | `BLOCKED` | System Asset does not exist and its canonical identity is unapproved. |
| 2 | new System Asset ID | `Contains` | new Controller Device ID | `BLOCKED` | Both IDs and controller cardinality unresolved. |
| 3 | Gateway ID `e8b0d5b0-9c3c-11f1-a0fc-e93bd628a87f` | `ConnectedTo` | new Controller Device ID | `BLOCKED` | Optional edge requires proof that this Gateway owns the ventilation endpoint. |

Read-only preflight found no existing `Contains`, `ConnectedTo` or ventilation relation
on the pilot Barn/Gateway, so no current relation collision was observed.

## Idempotency checks for future execution

Before each relation POST:

1. GET the exact from/to/type relation.
2. Exact match → `REUSE` and do not POST.
3. Different parent, reverse direction, duplicate semantic edge or ownership mismatch →
   `BLOCKED`.
4. Absent relation with exact approved endpoints → `CREATE`.

`Contains` must remain acyclic and each new entity must have exactly one canonical
`Contains` parent.
