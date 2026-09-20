# State navigation (VENT-007 / 5 States)

| Hash | Purpose | Allowed interaction |
|---|---|---|
| `#default` | Farm overview | Barn selection and local tab navigation |
| `#vent_detail` | One-Barn monitor | Equipment status inspection, system flags review |
| `#vent_history` | Six-hour history | Environmental telemetry review, "Gió & nước" inspection |
| `#vent_alarms` | Alarm list | Read-only alarm inspection by source (`PLC` vs `PLATFORM`) |
| `#vent_settings` | Controller settings | Read-only inspection of 224 settings parameters (default `--`) |

All header tabs are local navigation/filter operations. A Barn card opens `vent_detail`
with its `barnId`; this selection survives tab changes and ThingsBoard state remounts.
Only the ND2-1 fixture has detailed monitoring/history/settings. Other known demo Barns
show their own summary plus an explicit unavailable-detail notice and a link back to the
sample Barn. An unknown ID must not silently show another Barn's measurements.
The alarm list is explicitly farm-wide; it is not presented as a selected-Barn query.
No navigation handler sends an RPC request or mutates device, alarm, entity, or tenant state.
In ThingsBoard runtime, read `ctx.stateController.getStateParams()` and navigate with
`ctx.stateController.openState(state, {barnId}, false)`. Standalone uses
`#vent_detail?barnId=...`. The active tab exposes `aria-current="page"`.
Invalid hashes fall back to `default`.
