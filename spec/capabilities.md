# beopsuny-skill Capabilities

This file is the middle layer between `spec/charter.md` and concrete backlog or release work. Each capability describes one durable contract surface with a stable slug, observable Goal, scoped ownership, three first-pass Expected Behaviors, and two Hard Constraints.

Capability IDs are routing handles. Use lowercase slugs in task or sprint metadata, then put nuance in prose.

Mutation discipline:

| Section | Who writes | When | Gate |
| --- | --- | --- | --- |
| `Goal`, `In-scope`, `Out-of-scope` | human via `spec-grill` | when the contract changes | challenge + confirm + apply |
| `Expected Behaviors`, `Hard Constraints` | human via `spec-grill` | when behavior or bright-lines change | grill + 3-axis predicate test |
| `Learnings` | human-approved Learning Action until a bounded writer exists | when a reusable capability lesson is accepted | append only between markers |
| `Decisions` | human | when a capability-level decision is made | append-only; promote cross-cutting decisions to `spec/charter.md` |

---

## Capability: source-citation

**Goal:** A user can tell what legal authority each conclusion rests on, how that authority was checked, and when the conclusion must be downgraded instead of treated as verified.

**In-scope:**
- Source family map, Full/Lite source-access boundaries, and fallback semantics.
- Source authority labels, verification status tags, provenance strings, and `[VERIFIED]` minimum conditions.
- Citation ledger binding for legal conclusions, including pinpoint, currency, supports, contradiction, and downgrade behavior.
- Golden citation fixtures and static/router checks that protect source-label and provenance drift.

**Out-of-scope:**
- Stale asset registry, revalidation records, and retirement decisions; those belong to `freshness-governance`.
- User-facing answer layout beyond citation/status/provenance requirements; that belongs to `output-role-destination`.
- Contract-specific issue spotting, review mode, negotiation points, and counter-drafting boundaries; those belong to `contract-review`.
- Proving substantive legal correctness beyond the source/citation contract.

### Expected Behaviors
- Every exposed legal citation that supports a conclusion has a target-specific citation or pinpoint, `source_authority`, `verification_status`, `provenance`, and currency/freshness state; if any required element is missing, the conclusion is downgraded instead of marked `[VERIFIED]`.
- When a source family, source label, or local-mirror provenance rule changes, the source-access docs, source-grading policy, citation-verification contract, golden fixtures, and static checks are updated together or the non-applicable surfaces are explicitly justified.
- Legal conclusions are bound to ledgered authority entries whose `supports` field covers the conclusion; unledgered, unsupported, contradictory, or output-disallowed authority entries do not become conclusion support.

### Hard Constraints
- This capability never permits `[VERIFIED]` from search snippets, API titles, bundled YAML candidates, stored user memory, or user-provided citation text alone.
- This capability never lets local official-source mirror confirmation be described as direct `law.go.kr` or `glaw.scourt.go.kr` confirmation unless that direct official source was actually opened or confirmed in the current answer path.

### Learnings
<!-- LEARN:BEGIN -->
<!-- entries appended only after user-approved Learning Actions -->
<!-- format: - YYYY-MM-DD: <one-line> [evidence] -->
<!-- LEARN:END -->

### Decisions
| date | decision | rationale | supersedes |
| --- | --- | --- | --- |
