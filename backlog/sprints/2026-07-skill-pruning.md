---
milestone: skill-pruning
status: completed
started: 2026-07-02
due: TBD
objectives: [O1, O2]
component: "source-citation"
---

# skill-pruning

Epic: #174 — SKILL.md 프루닝 사이클 (게이트 5겹 → 2겹, register → retire)

## Goal

SKILL.md가 단일 라우터 spine으로 정리되고(게이트 중복 제거, 과잉 라우팅 규칙 1곳, LVC 2단 트리거), O1/O2 테스트가 프루닝 전후 모두 PASS인 상태.

## Plan

Batch 1 — SKILL.md 구조 정리 (기반 작업, 의존성 없음):
- [x] #175 품질 게이트 5겹 → 2겹 통합 (품질 계약 매핑 삭제 + 응답 품질 게이트 축약) (~1h)

Batch 2 — 규칙 산재 정리 (Batch 1 이후 통합 위치 확정):
- [x] #176 과잉 라우팅 금지 규칙 5곳 → 1곳 통합 (~45min)

Batch 3 — 행동 변화 (기준선 확보 후, 전후 시나리오 비교):
- [x] #177 Legal Verification Core 2단 트리거(light/full) 도입 (~1.5h)

Batch 4 — 계측 기반 감사 (마지막):
- [x] #178 시나리오 기반 asset 감사 + retire 사이클 (~2h)

검증 게이트 (모든 batch 공통):
- `PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py` PASS (O1)
- `PYTHONPATH=.test-deps python3 tests/evaluate_scenario_outputs.py` PASS (O2)

## Running Context

- 크리틱 원본: 2026-07-02 craft-critique 세션. 핵심: 아키텍처는 유지, 퇴적된 게이트만 프루닝.
- charter Non-Goal 유의: "single public skill" 방향 유지. 게이트 자체를 없애는 게 아니라 authoritative 위치를 하나로.
- capabilities.md source-citation의 Hard Constraints(스니펫/번들 YAML로 VERIFIED 금지 등)는 프루닝 대상이 아님 — 위치만 이동 가능.
- O1 static check가 router/loading·docs 등 contract 검사를 하므로, SKILL.md 섹션 삭제 시 static check가 참조하는 앵커/문구를 먼저 확인할 것.

## Progress

- 2026-07-02: 스프린트 생성. #174 에픽 + #175-178 등록, 이슈 미러 pull 완료.
- 2026-07-03: Batch 1-4 전부 완료, `sprint/skill-pruning` 브랜치에 4 커밋. O1/O2 전 배치 그린.
  - #175: 품질 계약 매핑 삭제 + gate 표 5행 통합 + 응답 품질 게이트 2줄 축약 (SKILL.md 326→302줄)
  - #176: 라우팅 원칙 1(Right-sizing) 단일 기준화, 중복 4곳 pointer/삭제
  - #177: LVC light/full 2단 트리거 + "축약형" 금지 회귀 가드
  - #178: 참조 그래프 감사 → external-sites.md retire, freshness-governance에 Unrouted Asset Rule(retire-first), append-only 방침 폐기
  - 감사 결과 기록: 체크리스트 YAML은 checklist-routing 경유 로드 경로 있어 유지 (freshness_debt registry에서 관리). 미참조 자산은 external-sites.md 하나.
- 2026-07-03: PR #179 리뷰 사이클 — 8-앵글 리뷰 findings 8건 수정(b105d06: light tier supports 필드, retire 의미 구분, CLAUDE.md 잔존 참조, gate 셀 정리, 축약형 가드 축소, backlog/tasks gitignore) → 2라운드 LGTM → CI green → **머지 완료**. 에픽 #174 종료, 스프린트 완료.
