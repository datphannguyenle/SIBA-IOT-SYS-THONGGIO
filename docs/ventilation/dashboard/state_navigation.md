# State navigation

| Hash | Purpose | Allowed interaction |
|---|---|---|
| `#default` | Farm overview | Filter-free Barn selection and navigation |
| `#vent_detail` | One-Barn monitor | Local schematic pan and history navigation |
| `#vent_history` | Six-hour fixture history | Read-only inspection and table pan |
| `#vent_alarms` | Fixture alarm list | Read-only inspection and table pan |

All header tabs are plain local navigation. A Barn card opens `vent_detail`. No navigation
handler sends a request or mutates device, alarm, entity or tenant state. Invalid hashes
fall back to `default`.
