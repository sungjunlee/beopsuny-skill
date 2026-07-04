---
milestone: verification-hardening
status: completed
started: 2026-07-04
due: TBD
objectives: [O1, O2, O4]
component: "source-citation"
---

# verification-hardening

## Goal
검증 계약의 두 구멍을 막는다: (1) 미러 시행 전 공포본이 [VERIFIED] 현행 인용으로 새는 경로(#194), (2) exact-string 테스트가 문서 개선을 막고 구조 결함은 놓치는 문제(#182). 추가로 리포트 레이어의 실사용 smoke test 1회.

## Plan

- [x] Batch 1: #194 미러 시행일자 확인 규칙 계약화 (priority:high) — sonnet subagent 위임 → PR #197 머지, 이슈 close
- [x] Batch 2: #182 gate 표·tier 표 구조 검사 전환 (priority:high로 상향) — sonnet subagent 위임 → PR #198 머지, 이슈 close (exact-string 16개 대체)
- [x] Batch 3: 리포트 실사용 smoke test — sonnet subagent 생성 + 오케스트레이터 계약 검증 → 발견 2건 이슈화 (#195 공식 링크 슬롯 부재, #196 DATA_ROOT semantics 불일치)

## Running Context

- component=source-citation 근거: #194가 미러 provenance/currency 계약(source-citation 소유)의 직접 수정. #182는 테스트 인프라로 capability 밖이지만 스프린트 지배 작업은 #194.
- 실행 방식 (사용자 지시 2026-07-04): 구현은 opencode executor 또는 sonnet subagent에 위임, **위임 결과물은 오케스트레이터가 직접 검증** (게이트 재실행 + diff 정독 + #182는 mutation 확인 + #194는 미러 원본 대조).
- #194 예시 사례: 의료법 제34조 — 미러 frontmatter 공포 2026-06-09 / 시행 2026-12-10, 시행 전 제목 "비대면협진" vs 현행 "원격의료" (_context.md 미러 currency 함정 참조).
- 순차 실행 이유: 두 이슈 모두 tests/validate_skill_contracts.py·O2 fixture를 건드림.

- smoke test 판정 (2026-07-04, NDA internal_legal_memo 시나리오): 계약 준수 PASS — self-contained(외부 리소스 0)·금지 패턴 0·footer 4블록·자가 검증 블록·경로 규칙 전부 충족. 인용 3건(민법 §398④, 2000다35771 판시, 약관법 §8) 오케스트레이터가 미러 원문 대조 — 전부 일치, [INSUFFICIENT] 유보 정직. 결함은 계약 차원 2건(#195, #196). 부수 관찰: role×destination 합성 규칙 부재(output-role-destination capability 필요성의 실증 — 기존 권장사항 강화), review_mode.yaml moderate의 include_missing_clauses(true)↔include_missing_clauses_section(false) 해석 애매.

## Progress
- 2026-07-04: 스프린트 생성, #182 priority:high 상향.
- 2026-07-04: Batch 3 smoke test 완료 — sonnet subagent 생성, 오케스트레이터 검증 PASS, #195·#196 등록.
- 2026-07-04: opencode dispatch는 OpenAI oauth 만료(401)로 불가 — #194·#182는 sonnet subagent(worktree 격리) 경로로 전환. relay policy의 opencode dispatch 항목은 provider-qualified(openai/gpt-5.3-codex-spark)로 수정.
- 2026-07-04: Batch 1 완료 — PR #197 머지 (CI green, 봇 코멘트 0). 오케스트레이터 검증에서 rule 과잉 발화(날짜 미파싱) + fixture 실날짜 time-bomb 결함 발견·수정(0ec8737), probe 3종으로 발화 경계 확인. O2 unsafe fixture 13개로 증가.
- 2026-07-04: Batch 2 완료 — PR #198 머지 (CI green, 봇 코멘트 0). exact-string 16개 → 구조 검사 2함수(gate 표·tier 표), 표 밖 규범 문장 assert는 유지. 오케스트레이터가 mutation 3종을 구현자와 다른 변형으로 독립 재현(행 삭제 FAIL / 경로 오타 FAIL / 리워딩 PASS). 스프린트 종료.
