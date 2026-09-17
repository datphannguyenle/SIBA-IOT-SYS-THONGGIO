# VENT-005 rollout scope

## Result

`PILOT BARN SELECTED — CANONICAL CODES NOT YET APPROVED`

## First-rollout Barn

One Barn is selected to keep the initial rollout bounded:

| Field | Value | Classification |
|---|---|---|
| Barn name | `abc-dong-anh/ND2-1` | confirmed runtime |
| Barn ID | `e8a84a30-9c3c-11f1-a0fc-e93bd628a87f` | confirmed runtime |
| Label | `ND2-1` | confirmed runtime |
| Barn type | `1F1` | confirmed server attribute |
| Parent Area | `abc-dong-anh/Khu B` | confirmed `AreaToBarn` relation |
| Parent Area ID | `78276fd0-9c3b-11f1-a0fc-e93bd628a87f` | confirmed runtime |
| Customer | `Trại ABC · Đông Anh` | confirmed runtime |
| Customer ID | `4199dcf0-a2bc-11f1-812e-f9c2621c1a59` | confirmed runtime |
| Existing Gateway | `abc-dong-anh/ND2-1/GW-01` | confirmed runtime |
| Gateway ID | `e8b0d5b0-9c3c-11f1-a0fc-e93bd628a87f` | confirmed runtime |

There are four live Barns with `barnType=1F1`: `ND2-1` through `ND2-4`. `ND2-1` is the
deterministic lowest-sequence pilot; the other three are outside this rollout.

## Canonical code candidates

| Code | Candidate | Basis | Status |
|---|---|---|---|
| SITE | `ABCDA01` | normalized from current `abc-dong-anh` namespace | `BLOCKED`: current farm identity is documented as temporary |
| AREA | `B` | current live parent is `Khu B` | `BLOCKED`: A/B/C area split is documented as temporary, not source-approved |
| BUILDING | `ND2-01` | normalized unique live Barn label `ND2-1` | `BLOCKED`: owner has not approved this immutable canonical code |

`1F1` is a Barn type shared by four live Barns, so it cannot by itself serve as the
unique BUILDING code for this tenant.

## Candidate exact target names

- System Asset: `ABCDA01-B-ND2-01-VEN-SYS-01`
- Controller Device: `ABCDA01-B-ND2-01-VEN-PLC-01`

Both names returned HTTP 404 from their exact tenant lookup on 2026-09-17, so no current
name collision was observed. They remain blocked because their identity segments are not
approved.

## Controller cardinality

The approved VENT-004 topology proposes one System Asset and one controller sequence
`01` for a Barn. The technical PDF describes one controller's capabilities but does not
prove the installed number per Barn, and the tenant currently has zero ventilation
controllers.

Proposed pilot cardinality: `1 system : 1 controller`.

Status: `BLOCKED` pending authoritative owner/project confirmation.
