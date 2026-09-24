# VENT-012 checkpoint

## Status

`active` — end-to-end runtime đạt; soak 24 giờ chưa đủ thời gian.

## Runtime

- Dashboard: `DB-30-VEN-DETAIL-V1-GATEWAY-SIM`, ID trong `vent012_manifest.json`, version 3.
- Containers: `ventilation-plc-sim`, `tb-gateway-ventilation`; cả hai healthy.
- Four controllers: `SIM-VEN-ND2-1` .. `SIM-VEN-ND2-4`.
- Default scenarios restored to NORMAL/BOUNDARY/MANUAL/FAULT; all `allow_alarms=false`.
- Soak user service `siba-vent012-soak` started 24/09/2026 09:48:07 UTC+7, interval 60
  seconds, state outside Git at `~/.config/siba-vent012-soak.json`; planned completion
  25/09/2026 09:48:07 UTC+7. Two successive samples were observed before handoff.

## Verified

- 181 local tests PASS; `git diff --check` PASS.
- Firefox live PASS: 1366×768, 1536×734, 390×844 and all five screens.
- Alarm: four `[SIM]` alarms created through telemetry/rule engine, propagated with identical
  IDs to system/Barn/Area/Farm, then recovered through telemetry. No alarm mutation API.
- Edge cases: missing, invalid enum, controller no-response and stale; restored afterward.
- Gateway stop/restart recovered telemetry; protected deodorization gateway fingerprint unchanged.

## Continue

1. Run `python3 deploy/thingsboard/vent012_soak.py status`.
2. If `completed=true`, run `python3 deploy/thingsboard/vent012_soak.py export`.
3. Inspect all samples/failures, rerun preflight, runtime verify, browser verify and tests.
4. Only if all pass, update task/report and move task to review. Do not self-approve PLC use.

Do not print credentials, merge PR, connect a real PLC, enable RPC/downlink, or mutate shared
ThingsBoard resources. If the monitor stopped early, report it; do not fabricate elapsed time.
