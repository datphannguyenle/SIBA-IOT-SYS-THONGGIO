# Responsive behavior

| Width | Layout |
|---|---|
| `>1100 px` | ThingsBoard preview sidebar, four KPI columns, two-column overview/detail |
| `701–1100 px` | Two KPI columns; primary/secondary panels stack |
| `≤700 px` | Preview sidebar hidden, one KPI column, two Barn columns, scrollable tabs |

The root document has no intentional horizontal overflow. Wide schematic, chart and table
content pans inside its own container. Mobile maintains at least 44 px navigation targets,
hides nonessential shell metadata and retains `DEMO DATA`.

## VENT-008 validation — 20/09/2026

All five standalone states were captured with measured inner viewports of 1920×1080,
1366×768,820×1180 and 390×844; zero document horizontal overflow in all 20 checks.
Evidence: `evidence/vent008_capture.json` and the `vent008-*.png` screenshots.
Mobile uses a true 390×844 iframe, not a Firefox outer-window resize (which may clamp width).
Historical screenshots named `*-390.png` without the VENT-008 prefix did not prove that width.

The settings-group wrapper has `min-width:0` so wide matrices scroll within their panel.
History SVG width is recalculated on standalone window resize / ThingsBoard `onResize`;
the Celsius domain is shared, while humidity retains its explicitly labelled right axis.
The original architecture illustration stacks below its copy on narrow screens and is
non-operational; SVG status indications remain separate. Live verification is recorded
separately in the deployment report, not inferred from standalone captures.
