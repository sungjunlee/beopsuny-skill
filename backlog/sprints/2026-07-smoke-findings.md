---
milestone: smoke-findings
status: completed
started: 2026-07-04
due: TBD
objectives: [O1, O2, O4]
component: "source-citation"
---

# smoke-findings

## Goal
smoke test가 드러낸 계약 구멍 2개를 막고(#195 리포트 공식 링크, #196 DATA_ROOT semantics), tier 트리거를 O2가 실제로 지키게 한다(#181 verification_tier 소비).

## Plan

- [x] Batch 1: #195 리포트 인용 law.go.kr 링크 슬롯 → PR #199 머지 (봇 P2 1건 반영: 링크를 조문·판례 인용 행으로 한정)
- [x] Batch 2: #196 BEOPSUNY_DATA_ROOT semantics 통일 → PR #200 머지 (오케스트레이터가 CHANGELOG 히스토리 소급 수정 원복)
- [x] Batch 3: #181 tier 위반 unsafe fixture + rule → PR #201 머지 (verification_tier 자동 부착으로 소비, O2 unsafe 15개)

## Running Context

- 실행 방식: 직전 스프린트와 동일 — sonnet subagent(worktree 격리) 위임 + 오케스트레이터 직접 검증(게이트 재실행, diff 정독, rule은 발화 경계 probe, mutation은 다른 변형으로 재현). opencode는 OpenAI oauth 재인증 전 불가.
- component=source-citation 근거: #195·#196은 인용 링크·소스 경로 계약, #181은 verification tier 게이트 — 모두 source-citation 계약 표면.
- O2 기준 수치: 현재 PASS 10 outputs, 13 unsafe fixtures (#194 이후). #181이 fixture를 늘리면 수치 갱신.
- #196 통일 방향(이슈 제안 채택): 변수 = 루트(`~/.beopsuny`), 미러는 `${ROOT}/data/{family}` — 기본 경로 레이아웃 불변.

## Progress
- 2026-07-04: 스프린트 생성 (#195, #196, #181).
- 2026-07-04: 3개 배치 전부 완료 (PR #199·#200·#201, 전부 CI green). 오케스트레이터 개입 3건 — #199 봇 P2 반영(계약 근거 행에 무의미한 법령 링크 방지), #200 CHANGELOG 히스토리 원복(완료 기준 grep이 과잉이었음 — 히스토리는 당시 기록 유지), #201은 개입 없음(probe 검증만). O2 최종: PASS 10 outputs, 15 unsafe fixtures. 스프린트 종료.
