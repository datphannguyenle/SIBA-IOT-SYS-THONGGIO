# Ventilation dashboard demo

Run from the repository root:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/dashboard/index.html`. Use the four header tabs or hashes
`#default`, `#vent_detail`, `#vent_history`, and `#vent_alarms`.

Tests: `python3 -m unittest discover -s tests -v` (browser tests need `geckodriver` +
Firefox and are skipped otherwise). Regenerate evidence with
`python3 tests/capture_dashboard_evidence.py`.

This is a repository-only fixture demo. It is not a deployed ThingsBoard dashboard and
must not be used as proof of production telemetry, aliases, alarms or connectivity.
