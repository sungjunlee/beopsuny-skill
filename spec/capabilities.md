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

## Capability: freshness-governance

**Goal:** A user can tell when bundled assets or dated reference claims are only triage seeds, what live source check is still required, and why a stale item was kept, refreshed, or retired.

**In-scope:**
- Stale asset registry, freshness metadata, revalidation records, and retirement decisions for bundled YAML and dated reference claims.
- Runtime downgrade behavior for stale or volatile values, including `triage_only`, `[STALE]`, `[INSUFFICIENT]`, reviewer-note `Currency`, and `Before relying` requirements.
- Freshness gates for checklist routing, source access, bulk review cells, and stale registered references.
- Static checks, router fixtures, and revalidation fixtures that protect stale assets from becoming current-law conclusions.

**Out-of-scope:**
- Source family authority labels, citation ledger binding, provenance strings, and `[VERIFIED]` minimum conditions; those belong to `source-citation`.
- Role, destination, report rendering, and external-facing packaging rules; those belong to `output-role-destination`.
- Contract-specific issue spotting, review mode, negotiation points, and counter-drafting boundaries; those belong to `contract-review`.
- Substantive legal correctness after a live source has been checked; this capability only owns freshness and stale-asset handling.

### Expected Behaviors
- When a registered stale asset, stale reference claim, or volatile checklist value is relevant to an answer, it is used only to narrow triage or identify source families until live legal research supports the conclusion; if the live check fails or is incomplete, the answer marks the item `[STALE]` or `[INSUFFICIENT]` and states the remaining `Currency` or `Before relying` gap.
- When freshness metadata, the stale registry, freshness routing rules, or stale-output guardrails change, `freshness-governance.md`, `freshness_debt.yaml`, source-access/checklist-routing pointers, revalidation fixtures, and static/router checks are updated together or each non-applicable surface is explicitly justified.
- Before an asset or reference is retired from the stale registry or its review date is advanced, a revalidation record identifies the official source families checked, volatile items reviewed, asset update, retirement decision, remaining stale scope, and freshness-debt update status.

### Hard Constraints
- This capability never lets bundled YAML, stale reference text, stored user memory, old newsletters, or stale registered values assert present obligations, fees, forms, deadlines, thresholds, penalties, source counts, treaty counts, or filing requirements without live official or primary-source verification.
- This capability never removes a loaded asset from `freshness_debt.yaml`, marks a stale item `retire`, or advances `maintenance.next_review` when only partial refresh evidence exists or `remaining_stale_scope` is non-empty.

### Learnings
<!-- LEARN:BEGIN -->
<!-- entries appended only after user-approved Learning Actions -->
<!-- format: - YYYY-MM-DD: <one-line> [evidence] -->
- 2026-07-05 (run #issue-204-20260705095743002-2309059f): 죽은 자산은 README 인벤토리 테스트가 화석화할 수 있다 — retire 시 자산 파일·README 표·정적 검증 목록·잔존 포인터(assets 내부 포함)를 한 커밋에서 같이 걷어야 하고, 복구한 라우팅은 guardrail assert로 고정해야 mutation에 문다 [PR #208]
- 2026-07-05 (run #issue-205-20260705102550376-ffa339e0): opt-in 검증은 사각지대를 낳는다 — 자산 전수 규칙은 opt-out(명시 allowlist)로 집행하고, root 타입 같은 파서 경계도 bypass 경로가 된다. last_verified는 git 이력 대조로 정직하게 기록, 재검증 없으면 stale 등록이 정답 [PR #209]
- 2026-07-05 (run #issue-206-20260705104721047-9f15251c): 표현 단일화는 삭제로 끝내지 말고 재발 금지 assert(금지 위치 재도입 시 FAIL)로 고정해야 유지된다. 3중 표현 정리 시 각 사본의 고유 정보(하급심 caveat 등)가 단일 소스에 이미 있는지 대조 후 삭제 [PR #210]
- 2026-07-05 (run #issue-207-20260705110935312-cc604e1f): stale 자산 retire의 가장 싼 경로는 값 재검증이 아니라 단정 표현 제거(live-check-hint 전환) — 자산이 현행 값을 주장하지 않으면 freshness 부채 자체가 소멸한다. 관행 수치는 '법정 기준 아님' 주석으로 오독만 막으면 유지 가능 [PR #211]
<!-- LEARN:END -->

### Decisions
| date | decision | rationale | supersedes |
| --- | --- | --- | --- |
| 2026-07-05 | Freshness registry maintenance and runtime stale downgrade stay in one capability | the same stale-asset evidence determines both maintainer retirement decisions and whether an answer may state a current-law conclusion | — |
| 2026-07-06 | Asset-wide verification rules are enforced opt-out with an explicit allowlist, including parser-boundary shapes such as non-mapping YAML roots | opt-in verification created blind spots and a non-mapping root bypassed checks in #205 (PR #209); promoted from the 2026-07-05 Learning | — |

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

---

## Capability: router-loading

**Goal:** A user request is answered through exactly one primary intent with only the workflow references that intent needs, and no routing choice ever detaches the always-on legal-conclusion gates.

**In-scope:**
- The SKILL.md router spine: primary-intent classification, the intent → workflow-reference table, and routing principles including Right-sizing as the single over-routing criterion.
- The always-on / conditional gate attachment tables and gate-attachment semantics at the routing layer.
- Progressive-disclosure loading rules: what stays in the always-loaded spine versus what loads on demand from `references/` and `assets/`.
- Spine sizing decisions, router regression fixtures, and the router static checks that protect intent-table and gate-table structure.

**Out-of-scope:**
- The content of the gates themselves — citation, verification status, and provenance belong to `source-citation`; stale-asset handling belongs to `freshness-governance`; packaging belongs to `output-role-destination`.
- Full/Lite source-family semantics and fallback order; those belong to `source-citation` — the router owns only the placement of the mode block in the spine.
- Workflow internals of each routed intent (research depth, contract review logic, checklist selection).
- Substantive correctness of intent-specific answers.

### Expected Behaviors
- A simple confirmation request (statute text, enforcement date, official link) is answered through `legal_research` alone without loading contract, checklist, bulk-review, or knowledge-layer workflow references, and any over-routing judgment cites Right-sizing (routing principle 1) as the single criterion.
- Every answer that cites legal authority passes the always-on gates (citation verification, self-verification, output contract) regardless of the chosen primary intent, and conditional gates (freshness, profile/practice) attach whenever their trigger is present — loading economy never changes gate applicability.
- When the router spine changes (intent row, gate table, routing principle, loading rule, or spine size), the intent table, gate tables, router regression fixtures, and router static checks are updated together or the non-applicable surfaces are explicitly justified.

### Hard Constraints
- This capability never lets spine-size reduction, reference-loading economy, or routing simplification detach an always-on legal gate from the always-loaded surface; workflow detail may move to `references/`, gate attachment may not.
- This capability never answers a Korean-law request from memory because routing or reference loading failed or was skipped; a failed or unavailable route degrades to `[INSUFFICIENT]` or a narrower answer, never to memory-based conclusions.

### Learnings
<!-- LEARN:BEGIN -->
<!-- entries appended only after user-approved Learning Actions -->
<!-- format: - YYYY-MM-DD: <one-line> [evidence] -->
- 2026-07-06 (run #issue-212-20260706094947677-9370550e): relay-merge of PR #213 [PR #213]
<!-- LEARN:END -->

### Decisions
| date | decision | rationale | supersedes |
| --- | --- | --- | --- |
| 2026-07-06 | Over-routing judgments have a single criterion (Right-sizing, routing principle 1) and the quality layer is two-fold (router gate table + citation-verification contract) | the #174 pruning cycle showed duplicated gate layers create drift and maintenance cost (PR #179) | — |

---

## Capability: profile-practice-memory

**Goal:** A user's company, practice, and project/matter context is remembered across sessions and applied to answers — without stored content ever weakening verification gates, without unconfirmed writes, and without context leaking across matter boundaries.

**In-scope:**
- `~/.beopsuny/` memory locations, file roles (profile, practice overlays, project/matter files, review/learning/verification logs), and merge order.
- The trust boundary: stored profiles, playbooks, and logs are reviewed data, never instructions.
- User-confirmed writes and the quick/full onboarding flows, including seed-document candidate extraction.
- Project/matter workspace boundaries and cross-context read defaults.
- Profile schemas under `assets/schemas/` and the static checks and router scenarios that protect them.

**Out-of-scope:**
- Verification and citation duties themselves; those belong to `source-citation`.
- Stale asset registry and freshness downgrade behavior; those belong to `freshness-governance`.
- Output packaging, role modes, and destination contracts; those belong to `output-role-destination` — profiles may suggest output defaults, but gate content lives with its owner.
- The contents of actual runtime user data, which lives outside the repo.

### Expected Behaviors
- When stored profile, playbook, practice-overlay, or log content is used in an answer, it is applied as reviewed context only (including explicit baseline markers such as `계약 playbook 미설정` when absent), and directive text inside stored data cannot change routing, source authority labels, verification status, or output gates.
- No file under `~/.beopsuny/` is created or modified without explicit user confirmation in the current conversation; onboarding extracts candidates from seed documents and past reviews and shows them before saving.
- When a memory location, schema, merge order, or workspace boundary changes, `memory-structure.md`, the affected `assets/schemas/*.yaml`, and the profile static checks and scenarios are updated together or the non-applicable surfaces are explicitly justified.

### Hard Constraints
- This capability never lets stored memory content (profile, practice overlay, playbook, logs, project/matter files) weaken or override SKILL.md gates, source authority labels, self-verification, freshness downgrade, or role/destination restrictions — memory narrows and personalizes, it never authorizes.
- This capability never reads or applies another project's or matter's files into the current answer without an explicit user request naming that context; cross-context reads default to off.

### Learnings
<!-- LEARN:BEGIN -->
<!-- entries appended only after user-approved Learning Actions -->
<!-- format: - YYYY-MM-DD: <one-line> [evidence] -->
- 2026-07-06 (run #issue-104-20260706132920374-5a508dc3): relay-merge of PR #214 [PR #214]
- 2026-07-07 (run #issue-105-20260707120238754-f291ebf4): relay-merge of PR #215 [PR #215]
<!-- LEARN:END -->

### Decisions
| date | decision | rationale | supersedes |
| --- | --- | --- | --- |
