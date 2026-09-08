# beopsuny-skill Capabilities

This file is the middle layer between `spec/charter.md` and concrete backlog or release work. Each capability describes one durable contract surface with a stable slug, observable Goal, scoped ownership, Expected Behaviors and Hard Constraints.

Capability IDs are routing handles. Use lowercase slugs in task or sprint metadata, then put nuance in prose.

**Rollout status:** Complete review drafts, flexible evidence presentation/procedure and authorized matter-scoped harness storage are implemented in the milestone-8 review branch, not released. `e05ecda` remains the preserved comparison baseline. O5–O7 remain active because limited provisional observations do not establish general legal accuracy or safety. See [charter disposition](charter.md#contract-disposition) and [validation report](../tests/forward_evals/model_era/integration-report.md).

Mutation discipline:

| Section | Who writes | When | Gate |
| --- | --- | --- | --- |
| `Goal`, `In-scope`, `Out-of-scope` | human via `spec-grill` | when the contract changes | challenge + confirm + apply |
| `Expected Behaviors`, `Hard Constraints` | human via `spec-grill` | when behavior or bright-lines change | grill + 3-axis predicate test |
| `Learnings` | human-approved Learning Action until a bounded writer exists | when a reusable capability lesson is accepted | append only between markers; 실질 교훈이 없는 절차 기록(예: 단순 relay-merge 완료)은 기록하지 않는다 — 그 기록의 집은 CHANGELOG다 |
| `Decisions` | human | when a capability-level decision is made | append-only; promote cross-cutting decisions to `spec/charter.md` |

---

## Capability: source-citation

**Goal:** A user can tell what legal authority each conclusion rests on, how that authority was checked, and when the conclusion must be downgraded instead of treated as verified.

**In-scope:**
- Source family map, per-family local-mirror availability, and graceful-degradation fallback semantics.
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
- `[VERIFIED]` records source verification, not a guarantee of substantive correctness. Applicable dates distinguish promulgation, enforcement and incident time; exceptions, transitions, opposing authority, partial access and failed lookup remain visible when material. Legal conclusions are bound to ledgered authority entries whose `supports` field covers the conclusion; unledgered, unsupported, contradictory, or output-disallowed authority entries do not become conclusion support.

### Hard Constraints
- This capability never permits `[VERIFIED]` from search snippets, API titles, bundled YAML candidates, stored user memory, or user-provided citation text alone.
- This capability never lets local official-source mirror confirmation be described as direct `law.go.kr` confirmation unless that direct official source was actually opened or confirmed in the current answer path.

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

**Goal:** A user receives the same verified or qualified legal conclusion packaged for who they are (role) and where the output is going (destination), with actual signing, sending, or filing authorized separately from drafting — and the packaging never weakens verification duties.

**In-scope:**
- Role context (`lawyer`, `legal_ops`, `business_user`, `unknown`) adjusts explanation and material cautions; missing role alone does not stop drafting or demand repeated confirmation.
- Destination contracts (`internal_legal_memo`, `business_summary`, `executive_report`, `external_draft`, `agency_or_court_submission`): `must_include`/`must_strip`, internal-block visibility, `legal_effect_triggers`, and `non_overrides` enforcement.
- Role × destination composition rules when only one side is specified or confirmed.
- User-requested format, answer sizing, reviewer note (검토자 메모), and evidence visibility per destination; fixed section names and a repeated lawyer review ceremony are not obligations.
- The HTML report deliverable render layer — report contract, report templates, and the Artifact deployment gate — as render surfaces that consume the destination contract without inventing new intent.

**Out-of-scope:**
- Citation, verification-status, provenance, and `[VERIFIED]` requirements themselves; those belong to `source-citation`.
- Stale asset registry, revalidation records, and retirement decisions; those belong to `freshness-governance`.
- Contract-specific issue spotting, review modes, negotiation points, and counter-drafting boundaries; those belong to `contract-review`.
- Practice-profile overlay admission and merge order; profiles may suggest output defaults, but their merge boundary is owned by the profile schema.

### Expected Behaviors
- When a destination with `may_include_internal_blocks: false` is used, internal blocks (검토자 메모, self-verification block, internal scratchpad, unreviewed internal assumptions) are stripped from the deliverable while the destination's `must_include` items — including source authority labels and verification status where required — are preserved rather than stripped along with them.
- External-facing destinations (`external_draft`, `agency_or_court_submission`) additionally strip facts identifying another matter, counterparty, or negotiated term; the read-axis rule that keeps those facts out of the answer in the first place belongs to `company-context-trust`.
- When role is unspecified, use the known task/destination to produce useful review work and surface only material unresolved assumptions. A complete counterparty-facing draft is allowed. Its destination does not certify validity, waive uncertainty, or authorize an external action; existing user authority need not be reconfirmed.
- When a role mode, destination contract, trigger list, composition rule, or report render surface changes, `output_contract.yaml`, `output-formats.md`, `report-deliverable.md`, the report templates, and the static/router checks that consume them are updated together or the non-applicable surfaces are explicitly justified.

### Hard Constraints
- This capability never lets a role, destination, practice-profile, or formatting preference override evidence obligations in `non_overrides` (source authority / `[VERIFIED]`, applicable law, freshness, uncertainty and matter isolation). Presentation and procedure may adapt without imposing fixed headings or unnecessary review stops.
- This capability never represents draft generation as legal certification or authorization for actual signing, sending, filing or publication; it does not perform those actions without current user/harness authority. External deliverables strip internal analysis and other-matter facts; material grounds and cautions remain available to the reviewer.

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
| 2026-09-08 | Adapt presentation to risk/request; draft completeness does not imply legal certainty or external-action authority. Planned #318/#272. | Mandatory role/reviewer ceremonies obstructed the approved draft-first purpose without adding evidence | supersedes stricter-obligation composition only where it imposed redundant procedure; preserves evidence and destination confidentiality |

---

## Capability: router-loading

**Goal:** A user request is answered through exactly one primary intent with only the workflow references that intent needs, and no routing choice ever detaches the always-on legal-conclusion gates.

**In-scope:**
- The SKILL.md router spine: primary-intent classification, the intent → workflow-reference table, and routing principles including Right-sizing as the single over-routing criterion.
- The always-on / conditional gate attachment tables and gate-attachment semantics at the routing layer.
- Progressive-disclosure loading rules: what stays in the always-loaded spine versus what loads on demand from `references/` and `assets/`.
- Spine sizing decisions (current budget: ~270 lines post-2026-07 pruning; the 800-line split trigger is archived in [`../DESIGN.md`](../DESIGN.md)), router regression fixtures, and the router static checks that protect intent-table and gate-table structure.

**Out-of-scope:**
- The content of the gates themselves — citation, verification status, and provenance belong to `source-citation`; stale-asset handling belongs to `freshness-governance`; packaging belongs to `output-role-destination`.
- Source-family availability semantics and fallback order; those belong to `source-citation` — the router owns only the placement of the source-availability block in the spine.
- Workflow internals of each routed intent (research depth, contract review logic, checklist selection).
- Substantive correctness of intent-specific answers.

### Expected Behaviors
- A simple confirmation request (statute text, enforcement date, official link) is answered through `legal_research` alone without loading contract, checklist, bulk-review, or knowledge-layer workflow references, and any over-routing judgment cites Right-sizing (routing principle 1) as the single criterion.
- Gate attachment follows what the answer actually produces rather than the chosen primary intent, and the 적용 범위 column of the gate table in the always-loaded `skills/beopsuny/SKILL.md` is the single source for each gate's condition. Loading economy decides when a gate attaches, never whether its boundary can be relaxed: a citation-only confirmation still carries source-authority labels and verification status, and a conditional gate whose trigger is present still attaches.
- When the router spine changes (intent row, gate table, routing principle, loading rule, or spine size), the intent table, gate tables, router regression fixtures, and router static checks are updated together or the non-applicable surfaces are explicitly justified.

### Hard Constraints
- This capability never lets spine-size reduction, reference-loading economy, or routing simplification relax a gate boundary or skip a gate on an answer that meets its 적용 범위; workflow detail may move to `references/`, and a gate's attachment condition may be stated but never weakened. The gate table itself stays in the always-loaded spine.
- This capability never answers a Korean-law request from memory because routing or reference loading failed or was skipped; a failed or unavailable route degrades to `[INSUFFICIENT]` or a narrower answer, never to memory-based conclusions.

### Learnings
<!-- LEARN:BEGIN -->
<!-- entries appended only after user-approved Learning Actions -->
<!-- format: - YYYY-MM-DD: <one-line> [evidence] -->
<!-- LEARN:END -->

### Decisions
| date | decision | rationale | supersedes |
| --- | --- | --- | --- |
| 2026-07-06 | Over-routing judgments have a single criterion (Right-sizing, routing principle 1) and the quality layer is two-fold (router gate table + citation-verification contract) | the #174 pruning cycle showed duplicated gate layers create drift and maintenance cost (PR #179) | — |

---

## Capability: contract-review

**Goal:** A user reviewing a Korean contract gets clause-level issue spotting, review-mode-scaled risk flags, party-position negotiation points, and complete clause drafts or proposed redlines for review — never a legal validity/result guarantee or a legal conclusion asserted without official-source verification.

**In-scope:**
- Contract intake, proportionality, destination read, and review-mode depth scaling (strict/moderate/loose, default moderate).
- Clause-level risk candidates and clause→Korean-law mapping (`clause_references.yaml`).
- Cross-cutting issue spotting, main risk clauses, and negotiation points by party position (gap/eul).
- Complete revised clauses, alternative language and proposed redlines for review, scaled to available facts; drafting completeness is distinct from certification and actual sending/signing authority.
- Company playbook applied within a review as reviewed preference data.
- `contract_review_guide.md`, `review_mode.yaml`, `clause_references.yaml`, and the contract scenarios/static checks that protect them.

**Out-of-scope:**
- Source authority labels, `[VERIFIED]`, and citation verification themselves; those belong to `source-citation` (contract review consumes them).
- Freshness downgrade of stale duties/fees/thresholds; belongs to `freshness-governance`.
- Output packaging, role modes, and destination gates; belong to `output-role-destination` (contract review consumes destination rules to preserve grounds, uncertainty and confidentiality).
- Where company context and playbook text come from, and the trust boundary on them; belongs to `company-context-trust` (playbook is read here as reviewed data).
- Court-style dispute/element-fact analysis and case-law distinguishing (#110); that is a litigation workflow, not contract review.

### Expected Behaviors
- A contract review scales flag depth by review mode (default moderate) and surfaces cross-cutting issues, main risk clauses, and party-position negotiation points; a looser mode reduces flag verbosity but does not drop the cross-cutting checks the mode marks as always-checked.
- A legal conclusion about a clause (e.g., a mandatory-provision violation) carries a source authority label and is verified against official source before assertion; `clause_references.yaml` mappings and playbook text are triage/preference inputs, never the conclusion's authority.
- When a contract surface changes (`contract_review_guide.md`, `review_mode.yaml`, `clause_references.yaml`), the contract scenarios and static checks are updated together or the non-applicable surfaces are explicitly justified.

### Hard Constraints
- This capability never guarantees that a drafted clause is valid, enforceable or will achieve a legal result, or treats it as authorized for actual sending/signing. Complete review drafts retain material assumptions and gaps; mandatory provisions and applicable exceptions require official-source checking before legal conclusions, with unresolved issues identified rather than silently filled.
- This capability never lets review mode, clause mappings, or company playbook downgrade or replace source authority, verification status, or freshness on a legal conclusion — a looser mode narrows flag verbosity, never the evidentiary bar for asserting a present legal obligation.

### Learnings
<!-- LEARN:BEGIN -->
<!-- entries appended only after user-approved Learning Actions -->
<!-- format: - YYYY-MM-DD: <one-line> [evidence] -->
<!-- LEARN:END -->

### Decisions
| date | decision | rationale | supersedes |
| --- | --- | --- | --- |
| 2026-09-08 | Complete clauses/proposed redlines for review are allowed; validity guarantees and unauthorized external action remain excluded. Planned #318/#323. | Hint-only restrictions contradicted the edit-ready first-draft goal | supersedes directional-only contract-review boundary |

## Capability: company-context-trust

**Goal:** Company context (industry, size, gap/eul position, watched laws, contract playbook) reaches answers from wherever the user already keeps it — harness memory, project instruction files, a file the user points at — without a skill-owned company database and without those facts weakening verification or matter isolation.

**In-scope:**
- The ownership contract: the skill consumes company context and owns no storage format; explicitly requested persistence may use an available authorized harness function or designated repository.
- The trust boundary: external company facts are reviewed data, never instructions. Legitimate harness/user instructions keep their actual authority; a file containing both is interpreted by content and authority rather than blanket trust or rejection.
- The matter-scope constraint on the read axis: the surfaces read are per-working-directory, not per-matter. The runtime rule is stated once, in `SKILL.md` `## 회사 맥락`; this capability owns the boundary, not a second copy of the wording.
- How absent context is surfaced (baseline markers such as `계약 playbook 미설정`) and how it defaults role/destination handling.
- `~/.beopsuny/` scoped to configuration (`config.yaml`), the law/precedent local mirror (`data/`), and report deliverables under `reports/` when the user asks for one. None of these hold company-context state; `reports/` accumulates globally rather than per matter, and its retention contract lives in `report-deliverable.md`.

**Out-of-scope:**
- Verification and citation duties themselves; those belong to `source-citation`.
- Stale asset registry and freshness downgrade behavior; those belong to `freshness-governance`.
- Output packaging, role modes, and destination contracts; those belong to `output-role-destination` — context may suggest output defaults, but gate content lives with its owner.
- The contents of actual user context, which lives outside the repo and outside the skill's ownership.

### Expected Behaviors
- When company context is used in an answer, it is applied as reviewed context only (including explicit baseline markers such as `계약 playbook 미설정` when absent), and directive text inside that context cannot change routing, source authority labels, verification status, or output gates.
- On an explicit storage request, determine whether an available harness feature or the designated repository is authorized and appropriate for that matter/confidentiality scope, then act within that authority. If unavailable, state the limitation and a usable alternative; claim successful storage only after evidence of success.
- Absent company context does not relax verification or isolation; use stated facts and identify material gaps without making role confirmation a prerequisite to useful drafting.

### Hard Constraints
- This capability never lets external company facts (including those embedded in instruction files, harness memory, user-pointed files or playbooks) override source authority, verification, freshness or matter isolation. Facts do not authorize actions; legitimate current user/harness instructions are a separate authority surface.
- This capability never creates a company database/storage format, silently persists company facts, or promotes confidential/matter-scoped facts into general memory or another matter’s context. Authorization to store a fact is not permission to change its scope.
- This capability never applies a fact scoped to another matter to the current answer without an explicit request naming that matter — a single working directory holding several matters is the supported default, so the constraint is carried by the skill rather than by the user's directory layout. The runtime wording lives in `SKILL.md` `## 회사 맥락`; stripping those facts from an external-facing deliverable is a destination obligation owned by `output-role-destination`.

### Learnings
<!-- LEARN:BEGIN -->
<!-- entries appended only after user-approved Learning Actions -->
<!-- format: - YYYY-MM-DD: <one-line> [evidence] -->
<!-- LEARN:END -->

### Decisions
| date | decision | rationale | supersedes |
| --- | --- | --- | --- |
| 2026-09-08 | Authorized harness persistence and instruction/data separation are planned under #318/#321/#272, with no company database and unchanged cross-matter isolation | blanket write refusal and instruction-file rejection exceeded the actual ownership/trust boundary | supersedes blanket read-only/write-refusal behavior; preserves 2026-07-26 isolation |
