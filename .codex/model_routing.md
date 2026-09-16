# Model routing

Use the smallest capable model and effort that preserves correctness. Availability must
be verified at runtime; unavailable routes require a documented fallback.

| Work type | Preferred route | Typical output | Must not own |
|---|---|---|---|
| PDF/document extraction | Luna low | Structured facts, page references | Final architecture |
| Narrow repo search/inventory | Luna low | Paths, symbols, counts | Integration decision |
| Checklist/evidence verification | Luna low | Pass/fail with evidence | Unreviewed approval |
| Document interpretation | Luna medium | Confirmed/derived/uncertain findings | Difficult cross-system debug |
| Code tracing/implementation analysis | Terra medium | Call paths, change plan | Product approval |
| Builder/widget implementation | Terra medium | Scoped changes and tests | Production deployment approval |
| Normal runtime debugging | Terra medium | Reproduction and fix evidence | Unbounded redesign |
| Difficult state or DOM/browser bugs | Terra high | Root cause and bounded fix | Final integration decision |
| Race conditions/cross-system debugging | Terra high | Reproduction, causal evidence, review | Scope expansion without MAIN |
| Architecture, decomposition, conflict resolution | MAIN | Decisions, gates, integration | Delegation of final accountability |

## Escalation

Escalate from low/medium only when the problem demonstrates ambiguity, difficult state,
DOM/browser behavior, concurrency, cross-system interaction or high-risk review. Record
the reason under `MODELS USED` in the handoff.
