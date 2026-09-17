# Deodorization design parity baseline

The direct baseline is the live ThingsBoard dashboard `SIBA · Khử mùi`, read through
GET-only API on 2026-09-17, plus its repository implementation and approved screenshots.
The live dashboard still exposes `default`, `deo_detail`, `deo_params`, `deo_alarms` and
the expected compact SIBA token set.

| Baseline behavior | Ventilation demo application |
|---|---|
| `#0c1622` canvas; `#152737` flat panels | Exact tokens reused |
| `#345163` 1 px panel border; 6 px radius | Exact shell treatment reused |
| Cyan active tab and primary monitor accents | Exact behavior reused |
| Amber outlined persistent DEMO badge | `DEMO DATA` is visible in every state |
| Compact 42–48 px header and 44 px tab targets | Same density/touch rhythm |
| Dense desktop, stacked mobile | Same responsive hierarchy |
| ThingsBoard owns top/left navigation | Demo shell is preview-only; dashboard owns no sidebar |

Source evidence: `/home/siba-iot-2/thingsboard-docker/tb-custom-ui/deploy/build_dashboard_deo.py`,
`dashboard-theme.css`, `widgets/header_bar.*`, `widgets/kpi_stat_card.*`,
`widgets/deo_barn_grid.*`, `widgets/deo_synoptic.*`, and approved `live-1920`/`live-390`
screenshots dated 2026-09-12.

The ventilation information architecture is distinct. No deodorization process meaning,
key, datasource or control behavior is copied.
