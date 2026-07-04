---
milestone: smoke-findings
status: active
started: 2026-07-04
due: TBD
objectives: [O1, O2, O4]
component: "source-citation"
---

# smoke-findings

## Goal
smoke test가 드러낸 계약 구멍 2개를 막고(#195 리포트 공식 링크, #196 DATA_ROOT semantics), tier 트리거를 O2가 실제로 지키게 한다(#181 verification_tier 소비).

## Plan

- [ ] Batch 1: #195 리포트 인용 law.go.kr 링크 슬롯 (계약 R2 + 템플릿 2종 + O1)
- [ ] Batch 2: #196 BEOPSUNY_DATA_ROOT semantics 통일 (source-access.md 커맨드 + report-deliverable.md + O1) — #195 이후 순차 (report-deliverable.md·O1 공유)
- [ ] Batch 3: #181 light/full tier 위반 unsafe fixture + evaluator rule (verification_tier 소비 또는 제거) — 순차 (CHANGELOG·O2 공유)

## Running Context

- 실행 방식: 직전 스프린트와 동일 — sonnet subagent(worktree 격리) 위임 + 오케스트레이터 직접 검증(게이트 재실행, diff 정독, rule은 발화 경계 probe, mutation은 다른 변형으로 재현). opencode는 OpenAI oauth 재인증 전 불가.
- component=source-citation 근거: #195·#196은 인용 링크·소스 경로 계약, #181은 verification tier 게이트 — 모두 source-citation 계약 표면.
- O2 기준 수치: 현재 PASS 10 outputs, 13 unsafe fixtures (#194 이후). #181이 fixture를 늘리면 수치 갱신.
- #196 통일 방향(이슈 제안 채택): 변수 = 루트(`~/.beopsuny`), 미러는 `${ROOT}/data/{family}` — 기본 경로 레이아웃 불변.

## Progress
- 2026-07-04: 스프린트 생성 (#195, #196, #181).
