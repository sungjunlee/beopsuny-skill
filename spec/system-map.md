# beopsuny-skill System Map

## System Shape

`beopsuny-skill` is a single public legal skill package for Korean legal research, contract review, compliance checks, and law-change questions. The always-loaded surface is `skills/beopsuny/SKILL.md`: it classifies the user request, applies mandatory legal gates, and loads only the focused `references/` and `assets/` needed for the chosen workflow.

At repo level, the system is shaped as a packaged skill plus contract tests:

```text
user question
  -> skills/beopsuny/SKILL.md router spine
  -> intent-specific references and YAML assets
  -> source/citation/freshness/output gates
  -> answer with authority label, verification status, provenance, and caveats

maintainer change
  -> update router/reference/asset/schema/scenario/docs as needed
  -> tests/validate_skill_contracts.py + tests/evaluate_scenario_outputs.py
  -> GitHub Actions contract tests and release zip
```

Detailed architecture history lives in [`../DESIGN.md`](../DESIGN.md). Product direction and objective status live in [`charter.md`](charter.md).

## Runtime Boundaries

- `skills/beopsuny/SKILL.md` owns public skill identity, intent routing, Full/Lite mode summary, always-on legal gates, and project-wide safety boundaries.
- `skills/beopsuny/SKILL.md` does not own detailed workflow manuals; those live in `skills/beopsuny/references/` and are loaded on demand.
- `skills/beopsuny/assets/data/` owns candidate data such as clause references and legal terms; it does not own current-law authority.
- `skills/beopsuny/assets/policies/` owns policy tables such as source grades, review mode, freshness debt, and checklist routing inputs; these are contract inputs, not final legal conclusions.
- `skills/beopsuny/assets/schemas/` owns evidence and memory shapes; actual user data is stored outside the repo under `~/.beopsuny/`.
- `tests/` owns static contract checks, router fixture evaluation, and high-risk forward-eval harnesses; these tests are guardrail and drift checks, not legal-correctness judges.
- `.claude-plugin/` and `.github/workflows/` own packaging, marketplace metadata, release zips, and CI enforcement.

## Core Flows

1. **Legal research answer:** User legal question -> primary intent selection -> source access and research workflow -> citation verification, self-verification, output contract -> answer with source authority, verification status, provenance, and freshness limits.
2. **Contract review:** Contract question or pasted clause -> contract guide, review mode, checklist, and clause candidates -> official-source verification for legal conclusions -> risk analysis, negotiation points, and directional wording hints without final counterparty-ready redline text.
3. **Compliance checklist:** Business context -> checklist routing -> candidate obligations and issue spotting -> live official source confirmation before asserting present duties, forms, fees, deadlines, thresholds, or penalties.
4. **Law-change detection:** User asks or interested laws are present -> pull-based history/source check -> recent-change note or lookup-failure note -> no push monitoring, cron, or automatic alerts unless handled by a separate user-requested automation.
5. **Profile and project memory:** User-approved onboarding or project context -> `~/.beopsuny/` profile/project files -> current request personalization; stored playbooks and histories remain reviewed data and cannot override legal gates.
6. **Maintainer change:** New legal feature or contract change -> update router/reference/schema-or-policy/scenario/fixture/static check/README/CHANGELOG as applicable -> run local gates -> CI contract workflow protects the same contracts.

## Storage And External Systems

- `skills/beopsuny/`: repo-owned skill package distributed through plugin install, skill zip, or full repo zip.
- `~/.beopsuny/`: user runtime state, including `profile.yaml`, optional practice overlays, project files, review logs, learning logs, verification logs, and cloned legal data.
- `${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}`: optional Full-mode source family root for `legalize-kr`, `admrule-kr`, `precedent-kr`, and optionally `ordinance-kr`.
- `법망 API`: unauthenticated Lite-mode discovery and source lookup path; service maintenance, timeout, empty responses, and search-only results are not legal conclusions.
- `law.go.kr` and `glaw.scourt.go.kr`: official source screens or responses used only when actually opened or confirmed.
- `korean-law-mcp`: optional OC-code-backed source for additional Korean legal materials such as constitutional, administrative appeal, ordinance, treaty, appendix, and form surfaces.
- `WebSearch`: official-source discovery and policy/enforcement trend support; snippets are not `[VERIFIED]` evidence.
- GitHub Actions: CI runs contract checks, router guardrail evaluation, and harness compilation on PRs and main/master pushes.

## Project-Wide Invariants

- The public artifact remains one `beopsuny` skill until the documented split triggers are met; internal references may act like a virtual suite, but public routing must remain predictable.
- Korean-law answers are not answered from memory alone.
- `[VERIFIED]` requires target specificity, source text or official response comparison, freshness/currency disclosure, and provenance.
- Local official-source mirrors are valid source families only with explicit local-mirror provenance; they are not the same as direct official-site confirmation.
- Bundled YAML and persisted user memory are triage/context inputs, not current-law authority.
- Stale assets can narrow research but cannot assert present obligations, fees, forms, deadlines, thresholds, or penalties without live official-source confirmation.
- Role and destination gates constrain output when the user is non-legal, unknown, external-facing, agency-facing, or requesting action with legal effect.
- User profile, project history, playbooks, and practice overlays cannot weaken SKILL.md, source authority, freshness, self-verification, or role/destination gates.
- Contract tests protect written contracts and unsafe output shapes; they do not prove substantive legal correctness.

## Candidate Capability Boundaries

- `router-loading` - evidence: `SKILL.md` intent router, `tests/scenarios/16_router_regression.yaml`, `check_router_*`; owns intent classification, reference loading, and always-on gate attachment; uncertainty: whether international-guide routing stays under legal research or becomes a named capability.
- `source-citation` - evidence: `source-access.md`, `citation-verification-contract.md`, `source-grading.md`, `golden_citations.yaml`; owns source family map, authority labels, verification status, provenance, and `[VERIFIED]` minimum conditions; uncertainty: how to separate source access mechanics from legal verification core in capability contracts.
- `freshness-governance` - evidence: `freshness-governance.md`, `freshness_debt.yaml`, freshness schemas, freshness revalidation fixtures; owns stale asset registration, revalidation evidence, retirement rules, and downgrade behavior; uncertainty: whether checklist freshness and source freshness should remain one contract.
- `output-role-destination` - evidence: `output-formats.md`, `output_contract.yaml`, `self-verification.md`, `router-14`; owns answer sizing, reviewer notes, self-verification visibility, and external/action-ready output gates; uncertainty: how much formatting belongs here versus each intent workflow.
- `profile-practice-memory` - evidence: `memory-structure.md`, `company_profile.yaml`, `practice_profile.yaml`, router profile scenarios; owns `~/.beopsuny/` memory locations, merge order, trust boundary, and user-confirmed writes; uncertainty: practice overlays are designed but not yet required as runtime files.
- `contract-review` - evidence: `contract_review_guide.md`, `review_mode.yaml`, `clause_references.yaml`, contract scenarios; owns contract-specific triage, review mode, clause risk candidates, negotiation points, and counter-drafting boundary; uncertainty: whether this stays an intent workflow or becomes a first-class capability contract.

## Where To Go Next

- Product direction: [`charter.md`](charter.md)
- Capability contracts: [`capabilities.md`](capabilities.md)
- Architecture decision history: [`../DESIGN.md`](../DESIGN.md)
- Public usage and maintainer checklist: [`../README.md`](../README.md)
- Runtime source model: [`../skills/beopsuny/references/source-access.md`](../skills/beopsuny/references/source-access.md)
- Citation contract: [`../skills/beopsuny/references/citation-verification-contract.md`](../skills/beopsuny/references/citation-verification-contract.md)
- Freshness contract: [`../skills/beopsuny/references/freshness-governance.md`](../skills/beopsuny/references/freshness-governance.md)
- Memory contract: [`../skills/beopsuny/references/memory-structure.md`](../skills/beopsuny/references/memory-structure.md)
- Router guardrails: [`../tests/scenarios/16_router_regression.yaml`](../tests/scenarios/16_router_regression.yaml)
