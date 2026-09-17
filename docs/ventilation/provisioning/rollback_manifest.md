# VENT-005 reverse-order rollback manifest

## Applicability

No rollback action is currently required because VENT-005 made no ThingsBoard mutation.
The sequence below applies only to objects confirmed as created by a later approved
execution. Pre-existing/reused objects are never deletion targets.

## Reverse-order actions

| Reverse step | API action | Status now | Guard |
|---:|---|---|---|
| 1 | `DELETE /api/v2/relation?fromId=e8b0d5b0-9c3c-11f1-a0fc-e93bd628a87f&fromType=DEVICE&relationType=ConnectedTo&relationTypeGroup=COMMON&toId=<controllerDeviceId>&toType=DEVICE` | `BLOCKED` | Execute only if that exact edge was created by the manifest. |
| 2 | `DELETE /api/v2/relation?fromId=<systemAssetId>&fromType=ASSET&relationType=Contains&relationTypeGroup=COMMON&toId=<controllerDeviceId>&toType=DEVICE` | `BLOCKED` | Exact from/to/type/typeGroup match required. |
| 3 | `DELETE /api/v2/relation?fromId=e8a84a30-9c3c-11f1-a0fc-e93bd628a87f&fromType=ASSET&relationType=Contains&relationTypeGroup=COMMON&toId=<systemAssetId>&toType=ASSET` | `BLOCKED` | Never delete `AreaToBarn`. |
| 4 | `DELETE /api/device/<controllerDeviceId>` | `BLOCKED` | Created ID only; confirm no retained telemetry/history obligation. |
| 5 | `DELETE /api/asset/<systemAssetId>` | `BLOCKED` | Created ID only; confirm no remaining relations. |
| 6 | `DELETE /api/deviceProfile/<deviceProfileId>` | `BLOCKED` | Only if created by execution and unused by every Device. |
| 7 | `DELETE /api/assetProfile/<assetProfileId>` | `BLOCKED` | Only if created by execution and unused by every Asset. |

The live OpenAPI operation IDs are `deleteRelation`, `deleteDevice`, `deleteAsset`,
`deleteDeviceProfile` and `deleteAssetProfile`.

The relation query parameter names above were read from the live OpenAPI definition.
Angle-bracket IDs remain deliberately non-executable until an approved execution records
the actual IDs returned by ThingsBoard.

## Rollback stop conditions

- An ID does not match the execution receipt.
- A profile or entity pre-dated the execution.
- A relation differs by direction, type or endpoint.
- Another entity now references the candidate target.
- Deletion would remove telemetry/history that policy requires retaining.
- Customer/tenant ownership changed after creation.

On a stop condition, preserve state and escalate; do not broaden deletion scope.
