# TODOS

현재 TODO는 2026-04-12 로드맵을 폐기하고, 다음 공개 릴리즈 전에 닫아야 하는 release-blocking trust-contract hardening 항목만 추적한다.

이 문서는 실행 순서와 범위만 잡는다. 자세한 Done Criteria는 GitHub Issues가 source of truth다.

## Release-blocking checklist

1. [ ] [#164](https://github.com/sungjunlee/beopsuny-skill/issues/164) VERIFIED current-law binding에서 `공식 실무자료: 미확정`을 결론 근거로 쓰지 않게 유지한다.
2. [ ] [#165](https://github.com/sungjunlee/beopsuny-skill/issues/165) 법망 API provenance를 검색 결과, 원문 필드 확인, 공식 원문 확인으로 분리한다.
3. [ ] [#166](https://github.com/sungjunlee/beopsuny-skill/issues/166) Desktop Chat Lite 템플릿에 항상 적용되는 legal gate card를 유지한다.
4. [ ] [#167](https://github.com/sungjunlee/beopsuny-skill/issues/167) 외부 초안과 stale-law 답변의 action-ready 누수를 unsafe fixture로 막는다.
5. [ ] [#168](https://github.com/sungjunlee/beopsuny-skill/issues/168) CI와 release workflow가 forward-eval unittest, contract tests, version preflight를 실행한다.
6. [ ] [#169](https://github.com/sungjunlee/beopsuny-skill/issues/169) 오래된 2026-04 TODO 로드맵을 이 체크리스트와 GitHub Issues로 대체한다.

## Retired roadmap

아래 항목은 기존 계획에서 이미 흡수됐거나 현재 구조와 맞지 않아 새 작업의 기준으로 쓰지 않는다.

- `DESIGN.md 생성`: 현재는 `spec/charter.md`, `spec/system-map.md`, `spec/capabilities.md`, README 품질 계약 지도가 더 최신이다. DESIGN 구조 개선은 별도 [#150](https://github.com/sungjunlee/beopsuny-skill/issues/150) 범위로 둔다.
- `Source Grading A/B/C/D`: 현재는 `source_grades.yaml`과 source authority label, verification status, provenance 분리 계약으로 대체됐다.
- `YAML Policy 구조 리팩터링`: `assets/policies/`, `assets/schemas/`, reference 문서 경계가 이미 잡혀 있다. 추가 이동은 별도 근거가 있을 때만 한다.
- `7차원 리뷰 Phase 1`: 현재는 Legal Verification Core, role/destination gate, self-verification, evaluator fixture로 대체됐다.

## Verification

변경 전후에는 최소 아래를 통과시킨다.

```bash
PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py
PYTHONPATH=.test-deps python3 tests/evaluate_scenario_outputs.py
PYTHONPATH=.test-deps python3 tests/forward_eval_harness.py --mode sample --evidence /tmp/beopsuny-forward-sample.yaml
python3 -m unittest tests/test_forward_eval_harness.py
python3 -m py_compile tests/validate_skill_contracts.py tests/evaluate_scenario_outputs.py tests/forward_eval_harness.py
```
