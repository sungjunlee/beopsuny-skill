---
milestone: output-modes
status: active
started: 2026-07-05
due: TBD
objectives: [O1, O2, O4]
component: "output-role-destination"
---

# output-modes

## Goal
에픽 #96의 잔여 gap을 닫는다: business_user 고위험 상황 gate(#106), role×destination 보수 합성 규칙 명문화 + external_draft 내부 메타 누출 fixture(#107), README 톤 재조정 충족 여부 감사(#108). 새 capability `output-role-destination`(2026-07-05 spec-grill 확정)의 Behavior 1·2를 실행 계약으로 옮기는 스프린트.

## Plan

- [ ] Batch 1: #106 고위험 상황 gate 목록(해고·형사·개인정보 유출·기관 제출·계약 서명·고액 과징금)을 output 계약 표면에 추가 + O2 unsafe fixture
- [ ] Batch 2: #107 보수 합성 규칙(role 미확정 + destination 지정 → 엄격한 쪽 우선) 명문화 + external_draft 내부 메타 누출 unsafe fixture
- [ ] Batch 3: #108 README investigation-assist 톤 감사 — v0.3.2에서 이미 조정된 부분과 AC 대조, 충족 시 근거와 함께 close

## Running Context

- 실행 방식: 직전 2개 스프린트와 동일 — sonnet subagent(worktree 격리) 위임 + 오케스트레이터 직접 검증(게이트 재실행, diff 정독, rule 발화 경계 probe, mutation 독립 재현). opencode는 OpenAI oauth 재인증 전 불가.
- component=output-role-destination: 이 스프린트가 새 슬러그의 첫 소비자. 합성 규칙은 capability Behavior 2("stricter obligation wins": must_strip 합집합, must_include 양쪽 모두, 서명·송부·제출 직접 지시 금지)를 그대로 따른다 — 위임 시 재해석 금지.
- 기존 커버리지 (중복 금지): router-14에 business_user unsafe fixture 2건(unsafe-business-user-direct-send, unsafe-business-user-cautious-but-action-ready) 존재. #188이 리포트/Artifact 맥락 자가 검증 블록 누출 fixture를 이미 추가함 — #107의 신규 fixture는 텍스트 external_draft 경로여야 함.
- O2 기준 수치: PASS 10 outputs, 15 unsafe fixtures (v0.4.0 시점).

## Progress
- 2026-07-05: 스프린트 생성 (#106, #107, #108). capability output-role-destination spec 확정·push (f82727b).
