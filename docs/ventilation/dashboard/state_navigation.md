# State navigation (VENT-007 / 5 States)

| Hash | Purpose | Allowed interaction |
|---|---|---|
| `#default` | Farm overview | Barn selection and local tab navigation |
| `#vent_detail` | One-Barn monitor | Equipment status inspection, system flags review |
| `#vent_history` | Six-hour history | Environmental telemetry review, "Gió & nước" inspection |
| `#vent_alarms` | Alarm list | Read-only alarm inspection by source (`PLC` vs `PLATFORM`) |
| `#vent_settings` | Controller settings | Read-only inspection of 224 settings parameters (default `--`) |

All header tabs are plain local navigation. A Barn card on the overview opens `vent_detail`.
No navigation handler sends an RPC request or mutates device, alarm, entity, or tenant state.
In ThingsBoard widget runtime, navigation is routed via `ctx.stateController.openState(state, {}, false)`.
Invalid hashes fall back to `default`.
