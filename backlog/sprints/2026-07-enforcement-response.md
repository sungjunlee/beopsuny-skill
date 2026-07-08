---
milestone: enforcement-response
status: active
started: 2026-07-08
due: TBD
objectives: [O1]
component: "output-role-destination"
---

# enforcement-response

에픽 #97 — Korean legal workflow suite 후속. litigation-template(#110) 종결 후 #111 착수. 착수 전 `spec-charter reassess`(2026-07-08) + `amend`(revision 3: 소송 결과 예측 Non-Goal 승격)로 spec 축 정리 완료.

## Goal
수사·조사 개시 상황(압수수색·임의제출·내부조사·제재 절차)에서 안전한 초기 대응 가이드가 제공된다: 증거보전(합법적 보존, 인멸·은닉 조력 금지), 변호인 선임, 임직원 인터뷰 주의, 보고라인 gate가 명시되고, 형량·승패·처분 결과 예측은 계속 금지된다(charter Non-Goal). 기존 role/destination 출력 gate와 정합하며(법적 효과 있는 행동 제약), 정적 구조 검증(O1)이 workflow를 고정한다.

## Plan

- [ ] #111 (Batch 1, ~1 session) enforcement/criminal response workflow — 초기 대응 가이드(증거보전·변호인·임직원 인터뷰·보고라인 gate) + 시나리오(중대재해·개인정보 유출·담합·영업비밀·산업기술·임금체불·무허가 영업) + 구조 검증. 결과 예측 금지 유지, 인멸 조력 금지

## Running Context
- **계약 앵커**: `output-role-destination` capability — #111 핵심이 법적 효과 있는 행동(수사 대응)에 role/destination gate를 적용하는 것. 보고라인·변호인·증거보전 gate는 "행동 제약" 출력 계약. `agency_or_court_submission` output mode(output-formats.md)와 정합.
- **안전 경계(하드)**: (1) 형량·승패·처분 결과 예측 금지 — charter Non-Goal(revision 3), SKILL.md line 22, #110 검사와 공통. (2) 증거 인멸·은닉·진술 조작·수사 방해를 돕는 문구 금지 — 가이드는 **합법적** 보존·대응만. (3) 변호사 자문 대체 금지 — 초기 대응 구조와 "변호인 선임" 안내지 확정 자문 아님.
- **capability 경계 주의**: #111은 enforcement workflow. litigation(#110)과 함께 별개 capability 후보 — **이번 종결 후 `spec-grill map`으로 litigation/enforcement capability 승격 여부 재검토**(reassess 2026-07-08 이월). 지금은 output-role-destination 확장으로 처리.
- **기존 자산 활용**: `assets/policies/checklists/serious_accident.yaml`(중대재해) 존재, `agency_or_court_submission` output mode 존재 — 신규 발명보다 이들과 정합하는 enforcement 초기 대응 계층 추가.
- **workflow map 정합**: enforcement/criminal은 workflow-map 7개 고정 workflow가 아님 — regulatory/litigation 인접. map 갱신 필요 시 행 구조·검사 유지.
- 테스트↔문서 강결합 + 이동 문자열 보호 + PR 본문 보강 + redispatch --run-id는 `_context.md` 참조.

## Progress
- 2026-07-08: 스프린트 생성. #111만 스코프(#112 후속). component output-role-destination, objective O1. 착수 전 reassess+amend(Non-Goal 승격) 완료.
