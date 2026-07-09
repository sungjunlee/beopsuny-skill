---
milestone: cross-border-overlay
status: completed
started: 2026-07-09
due: TBD
objectives: [O1]
component: "source-citation"
---

# cross-border-overlay

에픽 #97(workflow suite)의 **마지막** 하위 이슈 #112. #109 workflow map이 cross-border 행에 남긴 "#112 확장 로드맵은 후속 자리만 둠" 자리표시를 채운다. 해외법을 한국회사 실무 질문의 **보조축**으로 진입시키되, 새 라우터 의도·gate·capability 없이 기존 `source-citation` 계약(source grading + verification tag)과 `international_guide.md` 인덱스를 확장한다.

## Goal
한국회사 cross-border 질문에서 해외법이 한국법 workflow의 **보조축**으로 들어오고, 우선순위 overlay 영역(GDPR/SCC/UK IDTA, APPI, CCPA/CPRA, SaaS MSA, NDA, AI Act, sanctions/export control, FCPA/UK Bribery Act, contractor classification)이 각자의 한국법 anchor에 매핑되며, 해외법 source에도 source grading·verification tag가 적용되고 **jurisdiction/currency/source caveat가 기본 출력에 포함**된다. workflow-map cross-border 행의 "#112 자리표시"가 제거되고 구조 검증이 이를 고정한다 — 새 라우터 의도·gate 변경·capability 신설 없이(component `source-citation` 확장).

## Plan

- [x] #112 (Batch 1, ~1 session) cross-border overlay 로드맵 → PR #219 (merged) → (1) `international_guide.md`에 우선순위 해외법 overlay 영역 + 한국법 anchor 매핑 섹션 추가, (2) `source-grading.md`(source-citation 계약)에 해외법 source grading·verification tag·jurisdiction/currency/source caveat 규칙 추가, (3) workflow-map cross-border 행 자리표시 제거·overlay 로드맵 반영, (4) 신규 구조 검증 check + registration, mutation FAIL 재현

## Running Context
- **계약 앵커**: `source-citation` capability. #112 작업 3("source grading·verification tag를 해외법에 적용")이 citation 계약의 확장이다. litigation(#110)도 source-citation을 component로 썼음. **capability 신설 금지**(spec-grill map 2026-07-08이 지형 6개 확정) — 기존 계약 확장으로 처리.
- **새 라우터 의도 아님**(router-loading HC1): cross-border는 SKILL.md 라우팅 원칙 + workflow-map cross-border 행이 이미 `legal_research`/`compliance_checklist` + `international_guide.md` 인덱스 소비로 정의됨. gate 표·라우터 의도 표 변경 금지. `check_workflow_map_structure`의 cross-border assert(`인덱스`·`새 의도`·`international_guide.md` 소비)는 유지되어야 함.
- **해외법은 보조축**: 일반 해외법 도우미 금지. 결론 근거는 여전히 한국법 공식 원문. 해외법 overlay는 후보 쟁점 인덱스 + 현지 전문가 확인 안내. jurisdiction/currency/source caveat 기본 포함.
- **테스트↔문서 강결합**: workflow-map 짝 check = `check_workflow_map_structure`(L2738) + `check_litigation_element_fact_template`(L1934, `assert_not_contains` #110 자리표시 패턴 참조). international_guide 짝 = `check_international_index_routing`(L3743). source-grading 계약. 문서 수정 전 해당 check grep. 신규/이동 assert는 전문 문장 + mutation FAIL 재현.
- **자리표시 제거 패턴**: #110이 litigation 행에서 `assert_not_contains(workflow_map, "#110 court-style template은 후속 자리만 둠")`로 자리표시 제거를 고정한 것과 동형으로, cross-border는 `assert_not_contains(workflow_map, "#112 확장 로드맵은 후속 자리만 둠")` + 채워진 내용 전문 assert.
- **게이트**: O1 `PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py`, O2 `PYTHONPATH=.test-deps python3 tests/evaluate_scenario_outputs.py`(기준선 **10 outputs / 17 unsafe — 불변**). SKILL.md ≤271(현재 269).
- relay 운용 노트(redispatch `--run-id` resume, codex PR 본문 오케스트레이터 rewrite, 머지 후 학습커밋 rebase)는 `_context.md` 참조.

## Progress
- 2026-07-09: 스프린트 생성. 에픽 #97 마지막(#112). #109 workflow-suite / #110 litigation-template / #111 enforcement-response 스프린트가 참고 템플릿. component source-citation, objective O1. 다음: relay-ready로 Done Criteria 선(先)조인 → relay dispatch/review → ready_to_merge에서 정지.
- 2026-07-09: relay-ready로 Done Criteria 조인(request req-20260708234839266, leaf issue-112). relay-plan로 rubric(8 factor, 전 required)+dispatch prompt 작성. **relay-dispatch 착수** — codex executor, worktree isolation, `--publish-policy after-internal-review`(내부 리뷰 LGTM 후 PR publish). run-id `issue-112-20260708235135350-0151b32d`. 검증은 오케스트레이터 직접(O1/O2 재실행+diff 정독+mutation 재현).
- 2026-07-09: **executor 완료 → 오케스트레이터 직접 검증 통과 → 내부 리뷰 LGTM → PR #219 publish (ready_to_merge, 정지)**. diff 4파일 +72/-8: international_guide.md `## 0. 우선 외국법 보조축 overlay`(9개 영역→한국법 anchor+기존 의도), source-grading.md `### 4. 외국법 보조축 source rule`(grading+verification tag+jurisdiction/currency/source caveat DEFAULT 필수+한국법 결론근거 불가), workflow-map cross-border 행 자리표시 제거, `check_cross_border_overlay_roadmap`(13개 전문 assert+`assert_not_contains` 자리표시, 등록). 검증: O1 PASS·O2 PASS 10/17·SKILL.md 269 무변경·capability 6·mutation 3건(overlay 행 삭제/caveat bullet 삭제/자리표시 재도입) 독립 FAIL 재현·revert 후 PASS. 변경 문자열(모순 처리 renumber, 다루지 않는 것 rename)은 기존 assert 미결합(grep 확인). **머지는 사용자 명시 요청 대기(정지)**.
- 2026-07-09: 사용자 요청 — **상위 모델(Fable 5) 독립 적대적 리뷰 → MERGE-OK** (게이트 독립 재실행 O1/O2/SKILL 269/capability 6 + mutation 2건 독립 FAIL 재현; stale binding·router intent·auxiliary-axis·법률 anchor·scope creep 전부 클린; 비블로킹 nit=AI Act 행에 AI 기본법 anchor 추가 여지, 후속 후보). **PR #219 merged (squash)** → #112 CLOSED, worktree/bran치 정리. after-internal-review 정책상 리뷰가 publish 전(head afe053c)이라 PR 코멘트 부재 → gate-check `--skip` 감사코멘트 기록 + post-publication round-2 pass(ready_to_merge). 학습 커밋(source-citation)은 rebase 후 push(6506bee). post-merge main 게이트 재확인: O1/O2 PASS(10/17)·SKILL.md 269. **에픽 #97 마지막 하위 이슈 완료**.
- 2026-07-09: Sprint closed. 1/1 tasks completed.
