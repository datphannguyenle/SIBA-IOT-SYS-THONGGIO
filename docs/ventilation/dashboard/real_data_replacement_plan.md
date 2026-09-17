# Real-data replacement plan

1. Finish VENT-002 with direct evidence for entities, aliases, all keys, enum encodings,
   units/scales, freshness, feedback provenance, alarms and history.
2. Obtain `APPROVED — IMPLEMENTATION READY`; the demo does not grant it.
3. Implement `ThingsBoardSource.load()` using GET/read subscriptions only, mapping raw
   results to the canonical view model.
4. Run fixture and production adapters through the same contract tests, including null,
   stale, offline and unknown cases.
5. Package approved shared widgets/builders, remove the standalone preview shell, and
   validate in a dedicated non-production dashboard before any deployment gate.

No fixture value, stage count, threshold, alias, alarm type or entity name can be copied
into the production source merely because it appears correct in this demo.
