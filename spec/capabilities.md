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

---

## Capability: output-role-destination

**Goal:** A user receives the same verified or qualified legal conclusion packaged for who they are (role) and where the output is going (destination), with legal-effect gates applied before any signing, sending, or filing — and the packaging never weakens verification duties.

**In-scope:**
- Role modes (`lawyer`, `legal_ops`, `business_user`, `unknown`): default sections, legal-effect gates, and the conservative fallback for unconfirmed roles.
- Destination contracts (`internal_legal_memo`, `business_summary`, `executive_report`, `external_draft`, `agency_or_court_submission`): `must_include`/`must_strip`, internal-block visibility, `legal_effect_triggers`, and `non_overrides` enforcement.
- Role × destination composition rules when only one side is specified or confirmed.
- Answer sizing, reviewer note (검토자 메모), and self-verification visibility per destination.
- The HTML report deliverable render layer — report contract, report templates, and the Artifact deployment gate — as render surfaces that consume the destination contract without inventing new intent.

**Out-of-scope:**
- Citation, verification-status, provenance, and `[VERIFIED]` requirements themselves; those belong to `source-citation`.
- Stale asset registry, revalidation records, and retirement decisions; those belong to `freshness-governance`.
- Contract-specific issue spotting, review modes, negotiation points, and counter-drafting boundaries; those belong to `contract-review`.
- Practice-profile overlay admission and merge order; profiles may suggest output defaults, but their merge boundary is owned by the profile schema.

### Expected Behaviors
- When a destination with `may_include_internal_blocks: false` is used, internal blocks (검토자 메모, self-verification block, internal scratchpad, unreviewed internal assumptions) are stripped from the deliverable while the destination's `must_include` items — including source authority labels and verification status where required — are preserved rather than stripped along with them.
- When the role is unspecified or unconfirmed and the request names a destination or matches a `legal_effect_triggers` entry, the output composes the `unknown`/`business_user` conservative gate with the destination contract, and conflicts resolve to the stricter obligation: `must_strip` sets union, both `must_include` sets apply, and no direct instruction to sign, send, or file survives composition.
- When a role mode, destination contract, trigger list, composition rule, or report render surface changes, `output_contract.yaml`, `output-formats.md`, `report-deliverable.md`, the report templates, and the static/router checks that consume them are updated together or the non-applicable surfaces are explicitly justified.

### Hard Constraints
- This capability never lets a role, destination, practice-profile, or formatting preference override the `non_overrides` set (Legal Verification Core, 출처 권위 / `[VERIFIED]` contract, Freshness Governance, lawyer/legal_ops review requirements); packaging may only add restrictions, never subtract verification duties.
- This capability never emits an external-facing deliverable (`external_draft`, `agency_or_court_submission`, or a shared report/Artifact) that directly instructs signing, sending, or filing without the required reviewer gate, and never redeploys a previously shared external deliverable without disclosure.

### Learnings
<!-- LEARN:BEGIN -->
<!-- entries appended only after user-approved Learning Actions -->
<!-- format: - YYYY-MM-DD: <one-line> [evidence] -->
<!-- LEARN:END -->

### Decisions
| date | decision | rationale | supersedes |
| --- | --- | --- | --- |
| 2026-07-05 | Report render layer (report contract, templates, Artifact gate) is in-scope of this capability, not a separate capability | render layer consumes the destination contract with no new intent; splitting now would be premature at 2 capabilities | — |
| 2026-07-05 | Unconfirmed role + named destination composes conservatively: stricter obligation wins | 2026-07-04 smoke test showed agents improvise when no composition rule exists | — |
