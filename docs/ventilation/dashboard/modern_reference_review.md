# Modern dashboard reference review — 20/09/2026

Reviewed online at the user's request; inspiration informs the existing SIBA design,
not a replacement theme. No third-party screenshots or assets copied into the product.

| Primary reference | Applicable lesson | Application here |
|---|---|---|
| [Grafana dashboard practices](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/) | A consistent monitoring strategy and meaningful metrics | Keep compact overview KPIs and drill-down, avoid invented metrics to fill space |
| [IBM Carbon dashboards](https://carbondesignsystem.com/data-visualization/dashboards/) | Strong hierarchy, consistent colors, limited clutter, local exploration | Maintain SIBA tokens; add local search; shared temperature scale; labelled humidity axis |
| [ThingsBoard smart farming](https://thingsboard.io/use-cases/smart-farming/) | Overview/detail states, environmental trends and alarm context, dark viewing mode | Keep five-state SIBA navigation, separate contextual illustration from equipment status |

The ThingsBoard reference contains control features. Those are explicitly **not** adopted:
this module remains fixture-isolated and read-only. The references do not validate any
ventilation PLC mapping, physical topology, measurement threshold or entity alias.

## Original asset applied

Created `dashboard/assets/ventilation-barn-v1.png` using built-in imagegen (prompt and
provenance in the adjacent README). It appears below the overview Barn cards, not in place
of live-status SVGs, charts or measurement labels. The persistent demo badge and illustration
caption remain. No external asset CDN, runtime image service, or new ThingsBoard entity is used.

This is a bounded visual refinement: navy flat panels, cyan focus, white platform sidebar,
teal platform header and the established radius/density remain unchanged.
