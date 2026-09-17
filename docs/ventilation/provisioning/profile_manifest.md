# VENT-005 profile manifest

## Preflight

| Profile | Runtime match | Intended action | Manifest status |
|---|---:|---|---|
| `AP-SYSTEM-V1` | 0 | CREATE | `CREATE` after execution approval |
| `DP-VEN-CTRL-V1` | 0 | CREATE | `BLOCKED` by missing approved rule-chain/profile behavior |

The live tenant has 8 Asset Profiles and 11 Device Profiles. Neither target name exists.

## Asset Profile payload

Future endpoint: `POST /api/assetProfile`

```json
{
  "name": "AP-SYSTEM-V1",
  "default": false,
  "description": "SIBA Rev A system asset profile",
  "defaultRuleChainId": null,
  "defaultDashboardId": null,
  "defaultQueueName": null
}
```

Classification: `CREATE`. This is a dry-run action only.

## Device Profile payload

Future endpoint: `POST /api/deviceProfile`

```json
{
  "name": "DP-VEN-CTRL-V1",
  "type": "DEFAULT",
  "transportType": "DEFAULT",
  "default": false,
  "description": "SIBA Rev A ventilation controller profile",
  "defaultRuleChainId": "<BLOCKED: RC-20-VEN-PROCESS-V1 ID>",
  "defaultDashboardId": null,
  "defaultQueueName": null,
  "profileData": {
    "configuration": {"type": "DEFAULT"},
    "transportConfiguration": {"type": "DEFAULT"},
    "provisionConfiguration": null,
    "alarms": []
  }
}
```

Classification: `BLOCKED`. `RC-20-VEN-PROCESS-V1` does not exist among the three live
rule chains. VENT-005 is forbidden from creating a rule chain or inventing alarm rules,
so this payload is deliberately non-executable until the dependency is separately
defined and approved.

## Idempotency rule

- Exact absent profile → use the action above after approval.
- Exact profile with matching full definition → `REUSE`.
- Exact name with a different definition → `BLOCKED`; never overwrite automatically.
- A profile created by the controlled execution may be rolled back only if it has no
  external entity or rule-chain references.
