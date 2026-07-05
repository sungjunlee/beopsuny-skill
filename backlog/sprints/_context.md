# Project Context

dev-backlog 세션 시작 시 읽는 프로젝트 수준 컨텍스트. 스프린트를 넘어 재발견 비용이 큰 것만 남긴다.

- **테스트↔문서 강결합**: `tests/validate_skill_contracts.py`가 SKILL.md·references의 정확한 한국어 문구 수십 개에 `assert_contains`로 결합돼 있다. 문서 문구를 고치면 반드시 해당 check 함수를 먼저 grep해서 짝 수정할 것. 검증 게이트: `PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py`(O1) + `tests/evaluate_scenario_outputs.py`(O2).
- **backlog/tasks/는 gitignore** (PR #179 리뷰 결정): GitHub 이슈 미러는 sync-pull로 재생성 가능한 파생물이라 추적하지 않는다. 스프린트 파일과 완료 태스크(`backlog/completed/`)만 추적. dev-backlog 생성기가 `milestone: ` 후행 공백을 만들므로 completed/로 옮길 때 strip.
- **리포트 레이어 계약** (2026-07 스프린트, 에픽 #184): HTML 리포트는 `references/report-deliverable.md`가 단일 계약 — destination 계약 소비(R1), self-contained 규격+이스케이프(R2), 능력 기반 채널(R3), Artifact 공유 가정 gate+legal_effect_triggers 승급(R4), 새 의도 없음(R5). 템플릿은 `assets/templates/`. **템플릿 주석에 금지 패턴 리터럴을 넣지 말 것** — 생성 리포트에 잔류해 guardrail에 걸린다(static check가 부재를 검증). O2 기대 수치는 unsafe fixture 12개.
- **미러 currency 함정** (#180, PR #193): legalize-kr 미러는 최신 **공포본**을 담아 시행 전 개정 텍스트일 수 있다 (frontmatter `시행일자`가 미래인지 확인 — 의료법 제34조 사례). 미러 기반 revalidation·인용 시 공포일≠시행일 원칙을 미러 자체에도 적용할 것. 계약화는 이슈 #194.
- **relay 운용 노트**: 리뷰가 PR 본문 evidence를 요구하면 same-head 복구는 `recover-state.js --allow-same-head --require-pr-body-change`. 오케스트레이터 수정 커밋 후에는 `rebrand-evidence.js`로 evidence를 새 head에 재기록(게이트 재실행 근거 명시). **codex executor의 PR 본문은 최종 메시지 잘림으로 evidence가 truncate됨(2026-07-05 스프린트에서 4연속)** — dispatch 후 PR 본문(게이트 전체 문자열·mutation 기록·rubric 요구 표)은 오케스트레이터가 직접 작성/보강하는 것이 기본.
- **freshness 자산 규칙** (2026-07-asset-hygiene): assets/ 하위 YAML은 maintenance 의무(opt-out, 테스트 allowlist는 freshness-governance.md 기준의 집행자). stale 자산 retire의 우선 경로는 값 재검증이 아니라 단정 표현 제거(live-check-hint 전환). retire 시 non-retire revalidation fixture는 테스트 계약상 삭제 필연(git 이력 보존). last_verified는 git 이력 대조로 정직 기록 — 날짜 세탁 금지.
- **프루닝 방향** (2026-07 스프린트, 에픽 #174): 아키텍처(단일 스킬 + 의도 라우터 + progressive disclosure)는 유지, 품질 레이어는 2겹(의도 라우터 gate 표 + citation-verification-contract)이 기준. 과잉 라우팅 판단은 SKILL.md 라우팅 원칙 1(Right-sizing)이 단일 기준. LVC 적용 강도는 light/full 2단 트리거. 죽은 자산은 retire-first(등록 아닌 삭제).
