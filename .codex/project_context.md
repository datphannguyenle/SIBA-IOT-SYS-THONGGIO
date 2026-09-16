# Project context

## Project

SIBA IOT SYS - Ventilation Monitoring

## Operating model

- ChatGPT Web: architect, planner, reviewer.
- Codex: executor, tester, repo-native engineering agent.
- GitHub: shared state and source of truth.

## Current V1 scope

ThingsBoard monitors PLC only.

PLC controls:

- fans;
- pumps;
- louvers;
- ventilation logic.

ThingsBoard V1 provides:

- monitoring;
- telemetry;
- history;
- alarms;
- connectivity;
- mode/status display.

V1 is read-only. PLC/Gateway remains the source of truth for equipment state.

## V2 future scope

- control;
- settings;
- RPC;
- permissions;
- command feedback;
- audit log.

V2 is not authorized by V1 planning or design approval. It requires a separate data and
command contract, safety review, implementation task and deployment approval.

## Current gate

No production implementation may begin before `APPROVED — DESIGN ONLY` for VENT-001.
