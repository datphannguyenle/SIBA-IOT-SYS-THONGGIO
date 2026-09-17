# Responsive behavior

| Width | Layout |
|---|---|
| `>1100 px` | ThingsBoard preview sidebar, four KPI columns, two-column overview/detail |
| `701–1100 px` | Two KPI columns; primary/secondary panels stack |
| `≤700 px` | Preview sidebar hidden, one KPI column, two Barn columns, scrollable tabs |

The root document has no intentional horizontal overflow. Wide schematic, chart and table
content pans inside its own container. Mobile maintains at least 44 px navigation targets,
hides nonessential shell metadata and retains `DEMO DATA`.
