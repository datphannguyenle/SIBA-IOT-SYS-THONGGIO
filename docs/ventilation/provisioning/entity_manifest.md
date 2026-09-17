# VENT-005 entity manifest

## Manifest

| Order | Entity | Exact identity | Action | Evidence / condition |
|---:|---|---|---|---|
| 1 | Customer | `4199dcf0-a2bc-11f1-812e-f9c2621c1a59` / `Trại ABC · Đông Anh` | `REUSE` | Live customer owns both pilot Barn and Gateway. |
| 2 | Barn | `e8a84a30-9c3c-11f1-a0fc-e93bd628a87f` / `abc-dong-anh/ND2-1` | `REUSE` | Exact live `Barn`, `barnType=1F1`. |
| 3 | Gateway | `e8b0d5b0-9c3c-11f1-a0fc-e93bd628a87f` / `abc-dong-anh/ND2-1/GW-01` | `REUSE` | Exact live `Gateway`, same customer as Barn. |
| 4 | Ventilation System Asset | `ABCDA01-B-ND2-01-VEN-SYS-01` | `BLOCKED` | No collision, but canonical codes are not approved. Would use `AP-SYSTEM-V1`. |
| 5 | VentilationController Device | `ABCDA01-B-ND2-01-VEN-PLC-01` | `BLOCKED` | No collision; cardinality and `DP-VEN-CTRL-V1` remain blocked. |

## Future Asset payload

```json
{
  "name": "ABCDA01-B-ND2-01-VEN-SYS-01",
  "label": "Hệ thống thông gió ND2-1",
  "assetProfileId": {
    "entityType": "ASSET_PROFILE",
    "id": "<resolved AP-SYSTEM-V1 ID>"
  }
}
```

## Future Device payload

```json
{
  "name": "ABCDA01-B-ND2-01-VEN-PLC-01",
  "label": "Bộ điều khiển thông gió ND2-1",
  "deviceProfileId": {
    "entityType": "DEVICE_PROFILE",
    "id": "<resolved DP-VEN-CTRL-V1 ID>"
  }
}
```

Both payloads are `BLOCKED`, not executable JSON manifests, until every angle-bracket
reference and canonical code is replaced by a reviewed exact value.

## Ownership assignment

If later created, both new entities must be assigned to customer
`4199dcf0-a2bc-11f1-812e-f9c2621c1a59`. Creation must stop and roll back if the returned
entity has a different tenant/customer scope or if assignment fails.

## Collision result

- Exact candidate Asset lookup: HTTP 404, absent.
- Exact candidate Device lookup: HTTP 404, absent.
- Full inventory: 8,412 assets and 8,186 devices, with zero name/label/type/profile
  matches for ventilation terms.

Absence supports a future `CREATE`; it does not remove the current blockers or authorize
creation.
