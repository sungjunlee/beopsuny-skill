---
milestone: asset-hygiene
status: active
started: 2026-07-05
due: TBD
objectives: [O1, O2]
component: "freshness-governance"
---

# asset-hygiene

## Goal
2026-07-05 YAML 자산 전수 감사에서 나온 구멍 4개를 닫는다: 죽은 자산·끊긴 라우팅 수리(#204), freshness maintenance opt-in→의무화 반전 + legal_terms 등록(#205), 출력 예시 3중 표현 단일화(#206), clause_references 휘발성 값 live-check-hint 전환으로 최대 리스크 자산 retire(#207). 스킬 분리 없이 자산층 품질만 올리는 정갈화 스프린트 — SKILL.md 다이어트는 범위 외.

## Plan

- [ ] Batch 1: #204 죽은 자산·끊긴 라우팅 수리 — clause_taxonomy 삭제(retire-first) + mandatory_provisions ↔ self-verification Dim 4 연결 (소형)
- [ ] Batch 2: #205 freshness 테스트 opt-out 반전 + legal_terms maintenance 등록 (소형, 재발 방지 구조)
- [ ] Batch 3: #206 출력 예시 단일화 — source_grades.yaml example 블록 → output-formats.md (소형)
- [ ] Batch 4: #207 clause_references 휘발성 값 live-check-hint 전환 + freshness_debt retire (대형, 실질 작업량의 대부분)

## Running Context

- 실행 방식: 직전 3개 스프린트와 동일 — sonnet subagent(worktree 격리) 위임 + 오케스트레이터 직접 검증(게이트 재실행, diff 정독, mutation 독립 재현). opencode는 OpenAI oauth 재인증 전 불가.
- 감사 근거: clause_taxonomy는 runtime 참조 0건(README 표+테스트 화석화만), mandatory_provisions 헤더 anchor는 self-verification.md 이관 전 구조를 가리킴, check_asset_freshness_metadata_tracked는 maintenance dict 없으면 silent skip(opt-in), source_grades.yaml은 output_format/example_* 5블록으로 md 2곳과 3중 표현.
- 순서 의존: Batch 2의 allowlist 판단은 Batch 1의 clause_taxonomy 삭제 이후가 깔끔(죽은 자산에 maintenance 붙이는 낭비 방지). Batch 4는 Batch 2가 만든 의무화 체계 아래에서 clause_references maintenance를 갱신.
- 테스트↔문서 강결합(_context.md): 문서 문구 수정 전 해당 check 함수 grep해서 짝 수정. 게이트: `PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py`(O1) + `tests/evaluate_scenario_outputs.py`(O2).

## Progress
- 2026-07-05: 스프린트 생성 (#204, #205, #206, #207). YAML 자산 전수 감사(30개, 9,430줄) 결과 기반.
