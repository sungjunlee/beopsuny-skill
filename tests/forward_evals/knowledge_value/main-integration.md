# Current main integration — 2026-09-09

PR #331 / issue #332 integrates the delivery patch with merged M8 main. Runtime/test head: `0bede3c` (A/B/C preparation originally ran at `52481e9`; staged bytes were compared again at `0bede3c`); supplier checkout: knowledge combined PR #84 + #77, with freshly generated stable/canary manifests. This is delivery and preparation verification, not a new model evaluation.

- Runtime keeps the 1,800-character default. Every oversized asset is wholly omitted with source length/hash, zero delivered length, null delivered hash and an exclusion reason. The actual supplier's five assets are oversized: runtime returns `skipped`, and evaluation preparation fails without writing partial staged input.
- Explicit 9,812-character override delivers five complete assets. All receipt source/delivered lengths and SHA-256 values match; the four staged files exactly match runtime rendered sections.
- A/B/C preparation CLI succeeds with 12 `not_measured` cells and two C sections discovered under `research/privacy/memos`. Historical `privacy/research/memos` snapshots remain supported. No model is invoked and C is not supplied operationally.
- The prior results, source bundle, execution plan and environment remain byte-for-byte unchanged relative to `a69c300`; historical baseline/input hashes retain their original meaning.
- Regressions: 130 unit tests; skill/package contracts PASS; scenario outputs 11 and unsafe fixtures 13 PASS; rescore 19 corpus / zero drift; Python compilation and diff check PASS. Personal-checkout-dependent unit coverage was removed; temporary fixture tests retain the contract, and the actual supplier is checked separately above.

Reproduction (run from this repository, with `$SUPPLIER` identifying a generated supplier checkout):

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tests/validate_skill_contracts.py
python3 tests/evaluate_scenario_outputs.py
python3 tests/check_rescore_baseline.py
python3 skills/beopsuny/assets/tools/knowledge_manifest_ingest.py --manifest-file "$SUPPLIER/_system/manifests/stable.json" --knowledge-root "$SUPPLIER" --strict
python3 skills/beopsuny/assets/tools/knowledge_manifest_ingest.py --manifest-file "$SUPPLIER/_system/manifests/stable.json" --knowledge-root "$SUPPLIER" --strict --max-asset-chars 9812
python3 tests/forward_evals/knowledge_value/prepare.py --knowledge-root "$SUPPLIER" --output /tmp/knowledge-main-abc --source-bundle tests/forward_evals/knowledge_value/sources --questions-dir tests/forward_evals/knowledge_value/questions --max-asset-chars 9812
```

The default strict loader exits nonzero with `status: skipped` because no complete asset fits; normal fail-open mode still exits zero. Downstream preparation also exits nonzero when complete sections are missing. A preparation receipt is not proof of legal accuracy, operational benefit, or completion of separate M8 PR #330 / #323. `research_hold` remains in effect. Rollback scope is this PR's loader/preparer/tests/documentation, not historical evidence rewriting or the supplier publication policy.

Independent review: Claude Opus 5 high initially found two P2 issues (strict total-omission exit and the M8 preparation command). Both were fixed at `0bede3c`; the follow-up review returned LGTM / no P1 or P2 and independently verified the strict-exit regression with a reverting mutation. The later `069b214` change improves the HTTP 404 test only; its loader/preparer regressions and GitHub Contract Tests pass. CodeRabbit did not review this draft PR.

Authenticated raw loading supports `BEOPSUNY_KNOWLEDGE_TOKEN` or `GITHUB_TOKEN`; unauthenticated 404 and authenticated publication validation are separate observations. No credentials or private asset text are included in this record.
