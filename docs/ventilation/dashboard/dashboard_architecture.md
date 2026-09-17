# Dashboard demo architecture

```text
fixtures/ventilation/demo.json
        │ FixtureSource.load()
        ▼
widgets/ventilation-adapter.js
        │ legacy compatibility mapping
        │ createViewModel(): Rev A canonical, boolean/null-safe model
        ▼
dashboard/app.js
        │ hash router + read-only renderers
        ├── default
        ├── vent_detail
        ├── vent_history
        └── vent_alarms
```

The HTML/CSS/JS demo is dependency-free and runs from an ordinary static server. The
outer `.tb-preview-shell` exists only to review parity outside ThingsBoard. Production
packaging would mount the dashboard content inside the real shell and omit that wrapper.

The only implemented source is `FixtureSource`. `ThingsBoardSource` deliberately rejects
until VENT-002 has direct runtime evidence and receives `APPROVED — IMPLEMENTATION READY`.
No API URL or write operation exists in the demo.
