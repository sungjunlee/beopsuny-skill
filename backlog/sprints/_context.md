# Project Context

dev-backlog 세션 시작 시 읽는 프로젝트 수준 컨텍스트. 스프린트를 넘어 재발견 비용이 큰 것만 남긴다.

- **테스트↔문서 강결합**: `tests/validate_skill_contracts.py`가 SKILL.md·references의 정확한 한국어 문구 수십 개에 `assert_contains`로 결합돼 있다. 문서 문구를 고치면 반드시 해당 check 함수를 먼저 grep해서 짝 수정할 것. 검증 게이트: `PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py`(O1) + `tests/evaluate_scenario_outputs.py`(O2).
- **backlog/tasks/는 gitignore** (PR #179 리뷰 결정): GitHub 이슈 미러는 sync-pull로 재생성 가능한 파생물이라 추적하지 않는다. 스프린트 파일과 완료 태스크(`backlog/completed/`)만 추적. dev-backlog 생성기가 `milestone: ` 후행 공백을 만들므로 completed/로 옮길 때 strip.
- **프루닝 방향** (2026-07 스프린트, 에픽 #174): 아키텍처(단일 스킬 + 의도 라우터 + progressive disclosure)는 유지, 품질 레이어는 2겹(의도 라우터 gate 표 + citation-verification-contract)이 기준. 과잉 라우팅 판단은 SKILL.md 라우팅 원칙 1(Right-sizing)이 단일 기준. LVC 적용 강도는 light/full 2단 트리거. 죽은 자산은 retire-first(등록 아닌 삭제).
