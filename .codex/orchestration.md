# Orchestration workflow

```text
RECEIVE TASK
-> INSPECT REPO
-> DECOMPOSE
-> DELEGATE
-> COLLECT EVIDENCE
-> MAIN REVIEW
-> IMPLEMENT
-> TEST
-> HANDOFF
-> REVIEW
-> DONE
```

## Execution rules

1. MAIN resolves objective, scope, forbidden scope, dependencies and gate before work.
2. Inspect the repository and current task records before changing files.
3. Decompose only independent, bounded work. Do not fragment trivial work.
4. Assign one owner to each mutable file and browser/runtime session.
5. Delegates return compact findings with evidence and confidence; MAIN reviews important
   conclusions before integration.
6. Implementation starts only when the task gate permits it.
7. Tests must match the risk and record commands/results actually observed.
8. Move the task record through `backlog`, `active`, `review`, `done`; Git history remains
   the audit trail.
9. A failed or incomplete gate returns the task to the appropriate earlier state.

## Task lifecycle

- `backlog`: scoped but not started.
- `active`: owner assigned; investigation or authorized implementation underway.
- `review`: expected outputs exist and evidence is ready for MAIN/reviewer assessment.
- `done`: acceptance criteria and gate have passed; handoff is complete.

## Approval gates

- Design approval and deployment approval are separate.
- `APPROVED — DESIGN ONLY` permits preparation of an implementation task, not deployment.
- Production writes, entity changes, widget/dashboard deployment and V2 controls require
  explicit task scope and their own gate.

## Conflict handling

Stop integration when findings conflict, ownership overlaps or evidence does not support
the proposed decision. MAIN records the conflict, chooses a targeted follow-up and keeps
uncertain claims marked as uncertain.
