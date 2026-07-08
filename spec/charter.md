---
last_amended: 2026-07-08
revision: 3
---

# beopsuny-skill Charter

## Problem            <!-- Tier 1 · Direction (human-gated) -->
Korean legal research, contract review, and compliance answers are high-stakes, source-sensitive, and freshness-sensitive; a general agent can easily overclaim, invent citations, blur source authority, or give action-ready advice to the wrong audience.

## Approach           <!-- Tier 1 · Direction (human-gated) -->
Keep one public `beopsuny` skill with a small always-loaded router spine, then load focused references, YAML policies, schemas, and checklists only when the request needs them. Legal conclusions must pass source/citation, freshness, self-verification, and role/destination output gates; when those gates cannot be satisfied, the skill lowers confidence instead of filling gaps.

## Non-Goals          <!-- Tier 1 · Direction (human-gated) -->
- Replace a lawyer or provide final legal advice — the skill provides researched legal information and practical review support, not binding professional judgment.
- Guess statutes, case numbers, enforcement dates, filing requirements, fees, or penalty standards — missing or stale authority must produce `[UNVERIFIED]`, `[INSUFFICIENT]`, `[STALE]`, or a narrower answer.
- Use stale bundled YAML as current-law authority — bundled assets can triage and route, but live source verification is required before present obligations, documents, deadlines, or amounts are asserted.
- Promise push monitoring, cron jobs, or automatic legal-change alerts unless the user explicitly asks for an automation — law-change detection is pull-first by default.
- Produce final counterparty-ready contract language or automatic redlines — contract review can identify risk, negotiation points, and directional wording hints, but not certify final text.
- Predict litigation outcomes, sentencing, or enforcement/administrative dispositions — litigation and enforcement workflows provide element/fact analysis structure and safe initial-response guidance, not win/loss, sentence, or disposition forecasts.
- Split into multiple public skills only for internal neatness — the current direction is a single public skill with internal router/reference boundaries until real usage demands a separate surface.

## Objectives         <!-- Tier 2 · Predicates (add/remove human-gated; status proof-gated) -->
- O1 [validated] Running `PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py` reports `PASS` for the skill's static contract checks across router/loading, source/citation, freshness, output, profile/practice, docs, CI, optional installed-skill drift, and registry completeness domains. · src: execution
- O2 [validated] Running `PYTHONPATH=.test-deps python3 tests/evaluate_scenario_outputs.py` reports `PASS` for the router guardrail fixture set, including unsafe outputs that must fail the relevant guardrail rules. · src: execution
- O3 [active] A new legal feature can be reviewed against README's quality-contract checklist, with corresponding router/reference/schema-or-policy/scenario/fixture/static-check/README/CHANGELOG updates or explicit evidence that a row is not applicable. · src: inferred
- O4 [active] A user in Claude Code, Codex, or Claude Desktop can identify whether Beopsuny is in Full or Lite mode and see provenance that distinguishes local official-source mirrors, direct official-source checks, API fallback, and insufficient-source states. · src: inferred · gap: no Full/Lite-and-provenance smoke evidence cited yet (reassess-flagged 2026-07-06 and 2026-07-08); promote to `validated` only when a run cites it.

## Decisions          <!-- Tier 3 · History (immutable, append-only) -->
| date | decision | rationale | supersedes |
| --- | --- | --- | --- |
| 2026-07-06 | Quality layering is two-fold (router gate table + citation-verification contract) and over-routing judgments use the single Right-sizing criterion | five overlapping gate layers created drift and maintenance cost in the #174 pruning cycle (PR #179); promoted from `_context.md` and the router-loading capability | — |
| 2026-07-06 | Repo-wide asset verification is enforced opt-out (explicit allowlist) and dead assets are retired by deletion, not registration | opt-in verification created blind spots and dead assets fossilized through inventory tests in the asset-hygiene sprint (PRs #208, #209); promoted from freshness-governance | — |
| 2026-07-08 | Litigation and enforcement outcome prediction (win/loss, sentencing, administrative disposition) is a charter Non-Goal | already an always-on SKILL.md boundary and a tested contract via the #110 court-style template check; #111 enforcement shares the same bright line, so the boundary is promoted to Tier 1 direction | — |
