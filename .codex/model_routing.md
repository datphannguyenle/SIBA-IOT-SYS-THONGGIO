# Model routing

Use the preferred concrete routes below while delegating mechanical work to the smallest
capable model and effort that preserves correctness.

## Preferred concrete models

### MAIN

- Preferred: GPT-6 Astra (`gpt-6-astra`), reasoning effort `ultra`.
- Owns architecture, decomposition, difficult cross-task reasoning, integration decisions,
  conflict resolution, final review and approval gates.
- Should not perform mechanical search or extraction when that work can be delegated.

### Terra

- Preferred: `gpt-5.6-terra`, reasoning effort `medium`.
- Use for code tracing, implementation, runtime debugging and builder/widget work.
- Escalate to `gpt-5.6-terra` / `high` only for difficult state bugs, DOM/browser
  problems, race conditions, cross-system debugging or complex implementation review.
- Record the justification for escalation under `MODELS USED`.

### Luna

- Preferred: `gpt-5.6-luna`, reasoning effort `low`.
- Use for narrow repo search, PDF/document extraction, inventories, filtering, checklist
  verification, evidence collection and structured extraction.
- Escalate to `gpt-5.6-luna` / `medium` when bounded interpretation requires more
  reasoning.

## Runtime availability and fallback

- Check exact model availability at runtime.
- If a preferred model is unavailable, MAIN may select the nearest equivalent by role and
  capability.
- Record the fallback model and reason under `MODELS USED`.
- Preserve role boundaries when falling back.
- A cheaper model must never silently assume MAIN approval authority.

## Work-type routing

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
