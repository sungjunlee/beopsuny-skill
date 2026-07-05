---
milestone: skill-diet
status: active
started: 2026-07-06
due: TBD
objectives: [O1, O2]
component: ""
---

# skill-diet

SKILL.md 다이어트 — 2026-07-asset-hygiene 종결 시 합의된 후속. 자산층이 정리된 상태에서 라우터 spine 분량을 재평가한다.

## Goal
#183의 섹션별 분해표와 후보별 go/no-go 판정이 기록되고, go 판정 후보는 실행되어(또는 실행 이슈로 분리되어) SKILL.md가 판정된 목표 줄 수에 도달하며, O1/O2 게이트가 전 과정에서 PASS를 유지한다. 전부 no-go면 목표치를 현실화(~300줄)하고 에픽 #174에 결론을 연결한 뒤 종결한다.

## Plan

- [ ] #183 (Batch 1, ~1 session) SKILL.md 2차 프루닝 실익 평가 — 섹션별 줄 수/역할 분해표, 후보 3개(개인정보 보조 지식 축 목록 / 출력 형식 예시 / Full·Lite 경로 블록) go/no-go 판정, 결론을 에픽 #174 코멘트로 연결

## Running Context
- **Batch 2는 조건부**: go 판정 후보가 있으면 실행 이슈를 생성해 Plan에 `- [ ] #N (Batch 2)`로 추가한다. 전부 no-go면 Batch 1만으로 스프린트 종결(목표치 ~300줄 현실화 포함).
- **#183 후보 2는 선반영 가능성**: "출력 계약 형식 예시 2개 → output-formats.md pointer 대체"는 asset-hygiene #206(PR #210)에서 출력 예시 3중 표현을 output-formats.md 단일 소스로 이미 정리함 — 평가 시 현재 SKILL.md 상태 기준으로 잔여분만 판정할 것.
- **component 공란 사유**: 이 스프린트 영역(router spine)은 선언된 capability에 없음. 2026-07-06 reassess가 `spec-grill router-loading`을 착수 전 권고 — grill 확정 시 `component: "router-loading"`으로 채운다.
- **압축 역효과 경계**: 프루닝 1차(#174, PR #179 finding ⑤⑥)에서 무리한 압축이 gate 표 셀 과밀을 유발함 — 절감 줄 수보다 라우팅 신뢰도 우선.
- 테스트↔문서 강결합: SKILL.md 문구 수정 전 `tests/validate_skill_contracts.py`의 해당 check 함수를 먼저 grep (자세한 것은 `_context.md`).

## Progress
- 2026-07-06: 스프린트 생성 (reassess 리포트와 같은 세션). #183 미러 sync-pull 완료. 착수 전 router-loading grill 권고 상태.
