# Fidelity audit — SIBA ThingsBoard Agent Standard Rev A

## Scope

This audit compares `SIBA_THINGSBOARD_AGENT_STANDARD_RevA.md` with
`SIBA_ThingsBoard_Entity_Data_Standard_RevA.docx`. The DOCX is the human architecture
and acceptance source. The Markdown is a proposed machine-oriented companion; content
classified as derived or interpretive must not be presented as a verbatim DOCX
requirement.

## Classification

| Markdown section | Classification | Fidelity note |
|---|---|---|
| Front matter | DERIVED / MACHINE-ORIENTED GOVERNANCE | Machine metadata and scope encoding; useful but not a DOCX section. |
| 0 Agent operating contract | DERIVED / MACHINE-ORIENTED GOVERNANCE | Agent-specific behavior assembled from project safety principles. |
| 1 Normative vocabulary | DERIVED / MACHINE-ORIENTED GOVERNANCE | DOCX defines MUST/SHOULD/MAY, but Markdown adds VERIFIED, PROPOSED, OPEN and DEPRECATED. |
| 2 Source precedence | CONFLICT / NEEDS DECISION | This hierarchy does not appear in the DOCX and may invert project-specific authority; it requires explicit governance approval. |
| 3 Required architecture outcome | DIRECT FROM DOCX | Mirrors the platform/control architecture; the control path is future-only for ventilation V1. |
| 4 Entity decision rules | DIRECT FROM DOCX | Matches Asset/Device rules and canonical hierarchy. |
| 5 Standard relations | DIRECT FROM DOCX | Matches canonical relations and directions. |
| 6 Naming standard | INTERPRETATION | Structure is direct; hyphen/underscore rendering resolves ambiguous DOCX tables using its explicit prose. Accepted by the 2026-09-17 errata. |
| 7 Profile governance | DIRECT FROM DOCX | Reusable profile intent and profile catalog are preserved. |
| 8 Data classification | DIRECT FROM DOCX | Attribute/telemetry/command separation is preserved. |
| 9 Data key rules | DIRECT FROM DOCX | Canonical lowerCamelCase and semantic key rules are preserved. |
| 10 Canonical telemetry catalog | DIRECT FROM DOCX | Target catalog only; not evidence of source mappings or runtime availability. |
| 11 Data dictionary contract | DIRECT FROM DOCX | Required mapping fields are represented; unknown values must remain open. |
| 12 Modbus Gateway standard | DIRECT FROM DOCX | Architecture and configuration requirements are preserved; actual registers remain project evidence. |
| 13 RPC and remote control | DIRECT FROM DOCX | Faithful future architecture, but `N/A` for read-only ventilation V1. |
| 14 Alarm standard | DIRECT FROM DOCX | Naming and lifecycle requirements are preserved; runtime alarm availability is unconfirmed. |
| 15 Rule Chain standard | DIRECT FROM DOCX | Target design, not proof that chains are deployed. |
| 16 Dashboard standard | DIRECT FROM DOCX | Reuse/state/alias principles are preserved. |
| 17 Access control | DIRECT FROM DOCX | CE/PE capability still needs environment-specific implementation. |
| 18 Retention and performance | DIRECT FROM DOCX | Values remain design inputs until measured and approved. |
| 19 Versioning and environments | DIRECT FROM DOCX | DEV/TEST/PROD and versioned artifacts are preserved. |
| 20 Agent workflow for a new system | DERIVED / MACHINE-ORIENTED GOVERNANCE | Operationalizes DOCX project workflow specifically for agents. |
| 21 Required agent output format | DERIVED / MACHINE-ORIENTED GOVERNANCE | Output headings are agent protocol, not a DOCX acceptance requirement. |
| 22 Validation checklist | INTERPRETATION | Based on DOCX acceptance/FAT/SAT controls, reorganized into machine-checkable groups. Traceability should be maintained. |
| 23 Anti-patterns and required correction | DERIVED / MACHINE-ORIENTED GOVERNANCE | Mostly derived from prohibitions scattered through the DOCX; the table itself is new. |
| 24 Example entity topology | INTERPRETATION | Builds a concrete machine-readable example from DOCX patterns; instance identities remain illustrative. |
| 25 Sources | DIRECT FROM DOCX | Source family is retained, but availability and revision of every referenced project document must be verified. |
| 26 Final compliance rule | DERIVED / MACHINE-ORIENTED GOVERNANCE | Agent enforcement language is new and cannot elevate proposed Rev A into approved mandatory policy. |

## Required treatment of highlighted additions

- **Source precedence:** keep proposed only; do not enforce until SIBA approves the
  authority order and resolves how approved project contracts relate to the standard.
- **Normative vocabulary:** separate the three DOCX terms from the four agent evidence
  labels.
- **Agent operating contract:** retain as project governance, labelled as derived.
- **Anti-patterns:** retain as a safety-oriented synthesis, with traceability to source
  clauses or project rules.
- **Final compliance rule:** must respect the Rev A `proposed baseline` status, legacy
  exceptions and explicit user approval gates.
- **Output format:** use for consistent agent handoff only; do not score it as product
  compliance.

## Decision

The Markdown is suitable as a derived agent companion after the classifications above
are preserved. It is not a byte-for-byte or requirement-for-requirement replacement for
the DOCX. A later revision should add source-clause references to every direct rule and
label every agent-only rule explicitly.
