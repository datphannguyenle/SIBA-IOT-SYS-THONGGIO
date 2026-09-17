# VENT-005 API mutation manifest

## Status

`DRY RUN ONLY — DO NOT EXECUTE`

The live ThingsBoard 4.3.1.2 OpenAPI document confirms the operation IDs below. Relation
creation/deletion uses `/api/v2/relation`; the older local helper's POST to
`/api/relation` is not part of this manifest.

## Ordered future actions

| Step | Method and path | Action | Request/result dependency |
|---:|---|---|---|
| 1 | `POST /api/assetProfile` | `CREATE` | Exact `AP-SYSTEM-V1` payload in profile manifest. |
| 2 | `POST /api/deviceProfile` | `BLOCKED` | Requires approved `RC-20-VEN-PROCESS-V1` ID and final profile behavior. |
| 3 | `POST /api/asset` | `BLOCKED` | Requires approved codes and returned Asset Profile ID. |
| 4 | `POST /api/customer/4199dcf0-a2bc-11f1-812e-f9c2621c1a59/asset/<systemAssetId>` | `BLOCKED` | Requires newly created System Asset ID. |
| 5 | `POST /api/device` | `BLOCKED` | Requires approved codes/cardinality and Device Profile ID. |
| 6 | `POST /api/customer/4199dcf0-a2bc-11f1-812e-f9c2621c1a59/device/<controllerDeviceId>` | `BLOCKED` | Requires newly created controller ID. |
| 7 | `POST /api/v2/relation` | `BLOCKED` | Barn `Contains` System payload below. |
| 8 | `POST /api/v2/relation` | `BLOCKED` | System `Contains` Controller payload below. |
| 9 | `POST /api/v2/relation` | `BLOCKED` | Optional Gateway `ConnectedTo` Controller payload below. |

The OpenAPI operation IDs are `saveAssetProfile`, `saveDeviceProfile`, `saveAsset`,
`saveDevice`, `assignAssetToCustomer`, `assignDeviceToCustomer` and `saveRelation`.

## Relation request bodies

Barn → System:

```json
{
  "from": {"entityType": "ASSET", "id": "e8a84a30-9c3c-11f1-a0fc-e93bd628a87f"},
  "to": {"entityType": "ASSET", "id": "<systemAssetId>"},
  "type": "Contains",
  "typeGroup": "COMMON"
}
```

System → Controller:

```json
{
  "from": {"entityType": "ASSET", "id": "<systemAssetId>"},
  "to": {"entityType": "DEVICE", "id": "<controllerDeviceId>"},
  "type": "Contains",
  "typeGroup": "COMMON"
}
```

Gateway → Controller:

```json
{
  "from": {"entityType": "DEVICE", "id": "e8b0d5b0-9c3c-11f1-a0fc-e93bd628a87f"},
  "to": {"entityType": "DEVICE", "id": "<controllerDeviceId>"},
  "type": "ConnectedTo",
  "typeGroup": "COMMON"
}
```

Angle-bracket identifiers make these deliberately non-executable while blocked. A
controlled execution manifest must replace them with IDs returned and re-read during
that same approved execution.

## Explicit exclusions

There is no API action for Gateway configuration, attributes, telemetry, dashboard,
rule chain, alarm, credentials, RPC or PLC/device state. Existing production objects and
relations are read-only inputs.
