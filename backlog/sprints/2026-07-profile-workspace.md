---
milestone: profile-workspace
status: active
started: 2026-07-06
due: TBD
objectives: [O1, O2]
component: "profile-practice-memory"
---

# profile-workspace

에픽 #95 — practice profile + matter workspace foundation. 2026-07-06 skill-diet 종결 후 사용자 선택(#47 DOCX 제외, 에픽 #95→#97 순서)으로 착수. capability `profile-practice-memory`는 착수 전 spec-grill로 확정(2026-07-06).

## Goal
에픽 #95의 완료 기준 충족: shared company profile과 분야별 practice profile(contract/privacy/labor/regulatory/litigation)의 책임이 분리되고, matter workspace가 outputs·history·source log·cross-matter gate를 가지며, 저장물은 계속 untrusted(검토 대상) 데이터로 취급된다. O1/O2 게이트 전 과정 PASS.

## Plan

- [ ] #104 (Batch 1, ~1 session) practice profile cold-start — shared company profile ↔ 분야별 practice profile 구조 설계, quick/full 온보딩 확장, seed document의 stated position vs signed practice 추출 절차 명시. memory-structure.md·스키마·정적 검사 짝 갱신
- [ ] #105 (Batch 2, ~1 session) matter workspace — matter별 source-log/review-log/outputs/history 역할 분리, cross-matter context 기본 off + 예외 절차. capability HC2가 계약 앵커

## Running Context
- **계약 앵커**: `profile-practice-memory` capability (2026-07-06 확정) — HC1: 저장물은 gate를 약화·우회 불가(좁히고 개인화만). HC2: 다른 matter 파일은 지명된 명시 요청 없이 읽지 않음(cross-context 기본 off). Behavior 2: `~/.beopsuny/` 쓰기는 사용자 확인 필수.
- **기존 자산 활용**: `practice_profile.yaml` 스키마·`memory-structure.md` §Practice profile direction·§프로젝트 workspace 경계가 이미 존재 — #104/#105는 신규 발명이 아니라 이 방향 문서를 실행 계약으로 승격+확장하는 작업. 관련 정적 검사 5개(check_memory_profile_workflow, check_company_profile_playbook_schema, check_practice_profile_overlay_schema, check_current_law_verified_binding_excludes_unconfirmed_practice_material, check_memory_practice_profile_direction) 짝 수정 확인 필수.
- **다음 스프린트 예약**: 에픽 #97 (#109 workflow map 선행 → #110-112). #110 착수 전 `spec-grill contract-review` 필요 (2026-07-06 reassess 권고, 마지막 잔여 후보).
- 테스트↔문서 강결합 + 이동 문자열 보호 assert 규칙은 `_context.md` 참조.

## Progress
- 2026-07-06: 스프린트 생성. profile-practice-memory capability grill 확정(5번째 capability, 212줄 예산 내), system-map landed 갱신. 에픽 순서는 사용자 확정(profile 먼저).
