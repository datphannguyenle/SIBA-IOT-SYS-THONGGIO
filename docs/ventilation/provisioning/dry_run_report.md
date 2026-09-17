# VENT-005 dry-run report

## Result

`BLOCKED — NOT READY FOR CONTROLLED EXECUTION`

The architecture can be expressed as a deterministic action sequence, but immutable
codes, controller cardinality and the required controller profile dependency are not
approved. Codex does not grant the execution gate.

## Read-only evidence

| Check | Result | Classification |
|---|---|---|
| Tenant inventory | 8,412 assets; 8,186 devices | confirmed runtime |
| Ventilation entity/profile/name matches | 0 | confirmed absence at inspection time |
| Barns with `barnType=1F1` | 4 (`ND2-1` … `ND2-4`) | confirmed runtime |
| Pilot Barn | `abc-dong-anh/ND2-1` | selected exact live object |
| Pilot ownership | Barn and Gateway share customer `4199dcf0-a2bc-11f1-812e-f9c2621c1a59` | confirmed runtime |
| Candidate entity names | both exact lookups returned HTTP 404 | no collision observed |
| Target profiles | `AP-SYSTEM-V1` and `DP-VEN-CTRL-V1` absent | confirmed runtime |
| Required rule chain | `RC-20-VEN-PROCESS-V1` absent | confirmed runtime |
| Relation conflicts | no current `Contains`, `ConnectedTo` or ventilation edge on pilot scope | confirmed runtime |

## Action summary

| Classification | Items |
|---|---|
| `REUSE` | Existing customer, pilot Barn and candidate Gateway |
| `NO-OP` | Existing legacy hierarchy, room/silo/deodorizer/feeder relations and Gateway config |
| `CREATE` | `AP-SYSTEM-V1` after execution approval |
| `BLOCKED` | Device Profile, both new entities, ownership assignment and all three new relations |

## Blockers

1. `ABCDA01`, `B` and `ND2-01` are traceable candidates, not approved immutable codes.
2. The proposed `1 system : 1 controller` cardinality lacks an authoritative installation
   or owner confirmation.
3. `RC-20-VEN-PROCESS-V1` does not exist; creating it is forbidden in VENT-005.
4. `DP-VEN-CTRL-V1` therefore lacks its approved default rule-chain dependency and final
   processing/alarm behavior.
5. The pilot Gateway has many feeder relations, but no evidence yet proves it is the
   communication owner for the future ventilation controller; `ConnectedTo` is blocked.

## API safety accounting

Across the VENT-005 inspection sessions:

- 8 POST requests, all authentication-only `/api/auth/login`.
- 513 post-authentication GET requests.
- 0 other POST requests.
- 0 PUT, PATCH or DELETE requests.

No password, access token, refresh token, JWT, cookie or device credential was printed,
saved or committed.

## Prohibited changes verification

- No ThingsBoard entity/profile/relation was created, updated or deleted.
- No Gateway configuration was read as a secret or modified.
- No telemetry or attribute was written.
- No dashboard, rule-chain or alarm artifact was created.
- No RPC, PLC/device command or alarm mutation occurred.

## Required reviewer decisions

Before granting controlled execution, ChatGPT Web or the accountable system owner must:

1. Approve or replace SITE `ABCDA01`.
2. Approve or replace AREA `B`.
3. Approve or replace BUILDING `ND2-01`.
4. Confirm one Ventilation System and one controller for the pilot Barn.
5. Decide whether `DP-VEN-CTRL-V1` may be created without `RC-20-VEN-PROCESS-V1`, or
   authorize a separate rule-chain design task first.
6. Confirm whether Gateway `e8b0d5b0-9c3c-11f1-a0fc-e93bd628a87f` owns the future
   ventilation endpoint.
