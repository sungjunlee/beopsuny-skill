---
milestone: output-modes
status: completed
started: 2026-07-05
due: TBD
objectives: [O1, O2, O4]
component: "output-role-destination"
---

# output-modes

## Goal
에픽 #96의 잔여 gap을 닫는다: business_user 고위험 상황 gate(#106), role×destination 보수 합성 규칙 명문화 + external_draft 내부 메타 누출 fixture(#107), README 톤 재조정 충족 여부 감사(#108). 새 capability `output-role-destination`(2026-07-05 spec-grill 확정)의 Behavior 1·2를 실행 계약으로 옮기는 스프린트.

## Plan

- [x] Batch 1: #106 고위험 상황 gate → PR #202 머지 (high_risk_situations 필드 + O1 check + unsafe fixture, 기존 rule 재사용, O2 unsafe 16)
- [x] Batch 2: #107 보수 합성 규칙 → PR #203 머지 (composition_rule 블록 + O1 check + 텍스트 경로 누출 fixture, 기존 rule 확장, O2 unsafe 17)
- [x] Batch 3: #108 README investigation-assist 톤 감사 — AC 5개 전부 충족 확인(이슈는 이미 2026-06-23 close, v0.3.2에서 완료). 수정 0건, close 유지

## Running Context

- 실행 방식: 직전 2개 스프린트와 동일 — sonnet subagent(worktree 격리) 위임 + 오케스트레이터 직접 검증(게이트 재실행, diff 정독, rule 발화 경계 probe, mutation 독립 재현). opencode는 OpenAI oauth 재인증 전 불가.
- component=output-role-destination: 이 스프린트가 새 슬러그의 첫 소비자. 합성 규칙은 capability Behavior 2("stricter obligation wins": must_strip 합집합, must_include 양쪽 모두, 서명·송부·제출 직접 지시 금지)를 그대로 따른다 — 위임 시 재해석 금지.
- 기존 커버리지 (중복 금지): router-14에 business_user unsafe fixture 2건(unsafe-business-user-direct-send, unsafe-business-user-cautious-but-action-ready) 존재. #188이 리포트/Artifact 맥락 자가 검증 블록 누출 fixture를 이미 추가함 — #107의 신규 fixture는 텍스트 external_draft 경로여야 함.
- O2 기준 수치: PASS 10 outputs, 15 unsafe fixtures (v0.4.0 시점).

## Progress
- 2026-07-05: 스프린트 생성 (#106, #107, #108). capability output-role-destination spec 확정·push (f82727b).
- 2026-07-05: Batch 3 (#108) 감사 종료 — sonnet 감사 위임, 오케스트레이터가 issue state(2026-06-23 closed)와 grep 주장(README "정확한/자문/보장" 0건, guide 매치 2건은 무해) 직접 재확인. 수정·커밋 없음.
- 2026-07-05: Batch 1 (#106) 완료 — PR #202 CI green·머지. 오케스트레이터 검증: mutation 3종(상황 삭제/문서 rename/gate 약화) 전부 O1 FAIL 확인, rule 경계 probe(조건부 안전·부정 명령형 silent, fixture는 정당한 2사유 발화), 근로기준법 제27조 맥락 정확. 개입 0건. Batch 2 (#107) 위임 시작.
- 2026-07-05: Batch 2 (#107) 완료 — PR #203 CI green·머지. 오케스트레이터 개입 1건(0fa66d6): 구현자의 bare-phrase 누출 패턴이 준수 서술("내부 사고 과정을 포함하지 않았습니다")에 과잉 발화 → 라인 단위 negation 억제로 수정, 라벨형 콜론 패턴은 무조건 발화 유지. probe 6종 + composition_rule mutation 3종 통과. O2 최종: PASS 10 outputs, 17 unsafe fixtures. 에픽 #96 하위 이슈(#106/#107/#108) 전부 closed — 스프린트 종료.
