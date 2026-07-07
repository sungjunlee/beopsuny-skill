---
milestone: workflow-suite
status: completed
started: 2026-07-07
due: TBD
objectives: [O1]
component: "router-loading"
---

# workflow-suite

에픽 #97 — Korean legal workflow suite roadmap. profile-workspace(#95) 종결 후 사용자 선택으로 착수. #109 workflow map이 명시적 "선행"(foundation)이며 #110-112 설계는 이 map에 의존 → 이번 스프린트는 #109에 스코프, 나머지는 map 확정 후 후속 예약.

## Goal
단일 `beopsuny` 스킬 안에서 commercial/privacy/labor/regulatory/litigation/startup/cross-border workflow가 named workflow처럼 읽히는 virtual workflow map이 문서화된다: 각 workflow의 trigger·required references·output mode·verification(Source Grade) 요구가 명확하고, 물리적 plugin split trigger가 DESIGN.md와 정렬된다. 새 라우터 의도·gate 변경 없이(router-loading HC1), 정적 구조 검증(O1)이 map을 고정한다.

## Plan

- [x] #109 (Batch 1, ~1 session) virtual workflow map → PR #216 (merged) — 7개 workflow 매핑 표 + split 경계(DESIGN §6 정렬) + 구조 검증 check

## Running Context
- **계약 앵커**: `router-loading` capability — HC1(스파인 축소가 always-on gate를 분리하지 않음), HC2(실패 라우트는 [INSUFFICIENT]로 degrade). #109 map은 기존 라우터 위의 virtual 계층 문서화이지 **새 라우터 의도 추가가 아니다**(HC1). trigger→references→output→verification은 기존 의도 표·gate 표를 소비만 한다.
- **후속 예약 (map 확정 후)**: #110 court-style dispute template, #111 enforcement/criminal response, #112 cross-border overlay roadmap. 각각 별 스프린트 후보 — 설계가 #109 map에 의존.
- **#110 착수 전 `spec-grill contract-review` 필요** (2026-07-06 reassess 권고, system-map Candidate Boundaries의 마지막 잔여 후보). #109 map이 workflow 분해를 확정하면 grill 대상/경계가 더 선명해질 것.
- 테스트↔문서 강결합 + 이동 문자열 보호 assert 규칙 + codex PR 본문 truncate 보강은 `_context.md` 참조.

## Progress
- 2026-07-07: #109 dispatched → PR #216 → reviewed (R1 changes_requested → R2 LGTM) → merged (squash). issue #109 close, worktree/브랜치 정리. workflow map foundation landed → #110-112 후속 착수 가능.
- 2026-07-07: Batch 1 relay 완료 — PR #216 ready_to_merge (리뷰 **R2** pass). R1에서 changes_requested: startup 행 주 의도 셀이 실재 의도명 미지목(D1 부분위반) — 유효한 지적. R2에서 (a) startup에 legal_research/contract_review/compliance_checklist 명시, (b) 검사에 "각 행 주 의도 셀은 실재 의도명 ≥1개" assert 추가(O1이 놓친 silent gap 폐색). 검증(직접): O1/O2 PASS(10/17), SKILL.md 무변경 269줄, mutation R1 5건 + R2 신규 assert 1건 = 6건 FAIL 재현. redispatch는 fresh dispatch가 in-flight 가드에 걸려 `--run-id`로 run resume해야 진행됨(운용 노트).
- 2026-07-07: 스프린트 생성. 에픽 #97 착수(사용자 "권장대로"). #109만 스코프(foundation 선행), 나머지는 후속 예약. component router-loading, objective O1.
- 2026-07-07: Sprint closed. 1/1 tasks completed.
